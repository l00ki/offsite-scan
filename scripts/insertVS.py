#!/usr/bin/env python

# inserts virtual sites into .top, .pdb and .charg files (need to be in the
# same directory
# usage: ./insertVS.py <filename w/o extension>
# Offs: list of multipole atoms separated by single spaces
# a: virtual site distance as a multiple of the constructing C-X bond. for
# Offsite charges, add 1 to <r_offsite>/<r_C-X>
# r: virtual site distance in Angstrom
# Chr: virtual site charge

from math import sqrt
from os import system
from sys import argv, exit

class Vec3:
    def __init__(self, *args):
        self.X = args[0]
        self.Y = args[1]
        self.Z = args[2]

    def __add__(self, other):
        X = self.X + other.X
        Y = self.Y + other.Y
        Z = self.Z + other.Z
        return(Vec3(X, Y, Z))

    def __sub__(self, other):
        X = self.X - other.X
        Y = self.Y - other.Y
        Z = self.Z - other.Z
        return(Vec3(X, Y, Z))

    def __mul__(self, other):
        X = self.X * other;
        Y = self.Y * other;
        Z = self.Z * other;
        return(Vec3(X, Y, Z))

    def __truediv__(self, other):
        X = self.X / other;
        Y = self.Y / other;
        Z = self.Z / other;
        return(Vec3(X, Y, Z))

    def Magnitude(self):
        return(sqrt(self.X**2 + self.Y**2 + self.Z**2))

    def Normalized(self):
        return(self / self.Magnitude())

class Atom:
    def __init__(self, *args):
        self.Line = str(args[0])
        self.Serial = int(self.Line[6:11])
        self.Name = str(self.Line[12:16])
        self.AltLoc = str(self.Line[16])
        self.ResName = str(self.Line[17:20])
        self.ChainID = str(self.Line[21])
        self.ResSeq = int(self.Line[22:26])
        self.ICode = str(self.Line[26])
        self.Position = Vec3(float(self.Line[30:38]),
                             float(self.Line[38:46]),
                             float(self.Line[46:54]))
        self.Occupancy = float(self.Line[54:60])
        self.TempFactor = float(self.Line[60:66])
        self.Rest = str(self.Line[76:])

    def UpdateLine(self):
        self.Line = self.Line[:6] + '{:5d}'.format(self.Serial) + self.Line[11:]
        self.Line = self.Line[:12] + self.Name + self.Line[16:]
        self.Line = self.Line[:22] + '{:4d}'.format(self.ResSeq) + self.Line[26:]
        self.Line = self.Line[:30] + '{:8.3f}'.format(self.Position.X) + self.Line[38:]
        self.Line = self.Line[:38] + '{:8.3f}'.format(self.Position.Y) + self.Line[46:]
        self.Line = self.Line[:46] + '{:8.3f}'.format(self.Position.Z) + self.Line[54:]

    def UpdateParams(*args):
        self.Serial = int(args[0])
        self.ResSeq = int(args[1])
        self.Position.X = float(args[2])
        self.Position.Y = float(args[3])
        self.Position.Z = float(args[4])
        self.UpdateLine()

class Offsite:
    def __init__(self, *args):
        self.Origin = Atom(args[0])
        self.Neighbors = []
        self.Displacement = Vec3(0.0, 0.0, 0.0)

    def Displace(self):
        self.Displacement = Vec3(0.0, 0.0, 0.0)
        for item in self.Neighbors:
            self.Displacement = self.Origin.Position - item.Position
        self.Displacement = self.Displacement.Normalized() * r
        self.Origin.Position = self.Origin.Position + self.Displacement
        self.Origin.UpdateLine()

def ManTOP():
    InFile = open(TOPBK, "r")
    OfFile = open(TOP, "w")

    buffer = InFile.read()
    buffer = buffer.split("\n")

    while (buffer):
        line = buffer.pop(0)

        if "[ atoms ]" in line:
            while (len(line) >= 9): # allows for initial comment
                OfFile.write(line + "\n")
                print(line)
                line = buffer.pop(0)
            for i in range(Natoms + 1, Natoms + Nsites + 1):
                OfFile.write("        " + str(i) + "    OFF     1       LIG     X       " + str(i) + "    0.000   0.000\n")
                print("        " + str(i) + "    OFF     1       LIG     X       " + str(i) + "     0.000   0.000")
            OfFile.write("\n")
            print("")

            OfFile.write("[ virtual_sites" + str(Meth) + " ]\n")
            OfFile.write("; Site    aj  ai  funct   a\n")
            print("[ virtual_sites" + str(Meth) + " ]")
            print("; Site    ai  aj  funct   a")

            for i, item in enumerate(aj):
                OfFile.write("    " + str(Natoms + i + 1) + "    ")
                for j in ai[i]:
                    OfFile.write(j + "    ")
                OfFile.write(item + "    1    " + str(a) +"\n")
                print("    " + str(Natoms + i + 1) + "    " """+ ai[i]""" + "    " + item + "    1    " + str(a))

        OfFile.write(line + "\n")
        print(line)

    InFile.close()
    OfFile.close()

def ManCHR():
    InFile = open(CHRBK, "r")
    OfFile = open(CHR, "w")

    buffer = InFile.read()
    buffer = buffer.split()

    for i, line in enumerate(buffer):
        if str(i+1) in aj:
            line = float(line) - float(Chr)
        OfFile.write(str(line) + "\n")
        print(line)

    for i in range(0, Nsites):
        OfFile.write(str(Chr) + "\n")
        print(str(Chr))

    print("")

    InFile.close()
    OfFile.close()

def ManPDB():
    InFile = open(PDBBK, "r")
    OfFile = open(PDB, "w")

    buffer = InFile.read()
    buffer = buffer.split("\n")

    AtomCounter = 0
    MolCounter = 0

    while (not "ATOM  " in buffer[0]):
        OfFile.write(buffer[0] + "\n")
        print(buffer.pop(0))

    while("ATOM  " in buffer[0]):
        Atoms = []
        Offsites = []

        for i in range(0, Natoms):
            AtomCounter = AtomCounter + 1
            Atoms.append(Atom(buffer[i]))
            OfFile.write(Atoms[i].Line + "\n")
            print(Atoms[i].Line)

        for i, item in enumerate(aj):
            Offsites = Offsites + [Offsite(Atoms[int(item)-1].Line)]
            for j in ai[i]:
                Offsites[-1].Neighbors.append(Atom(Atoms[int(j)-1].Line))

        for item in Offsites:
            AtomCounter = AtomCounter + 1
            item.Origin.Serial = AtomCounter
            item.Origin.Name = " X  "
            item.Displace()
            OfFile.write(item.Origin.Line + "\n")
            print(item.Origin.Line)

        for i in range(0, Natoms):
            buffer.pop(0)

    while (buffer):
        OfFile.write(buffer[0] + "\n")
        print(buffer.pop(0))

    InFile.close()
    OfFile.close()

def main():
    ManTOP()
    ManCHR()
    ManPDB()

if (len(argv) != 2):
    print("NOT AN ARGUMENT")
    exit(1)

TOP = argv[1] + ".top"
TOPBK = TOP + ".bk"
PDB = argv[1] + ".pdb"
PDBBK = PDB + ".bk"
CHR = argv[1] + ".charg"
CHRBK = CHR + ".bk"

initialprint = open(TOPBK, "r").read()
print(initialprint)

Meth = 2 #int(input("Method     :    "))
Natoms = int(input("No of atoms:    "))
Offs = input("Offs       :    ")
Offs = Offs.split()
Nsites = len(Offs)

ai = []
aj = Offs
for i in range(0, len(Offs)):
    ai.append(input("aj=" + str(aj[i]) + ", ai   :    ").split())
if (len(ai) != Nsites):
    print("No of sites does not match No of origins")
    exit(1)
a = float(input("a          :    "))
r = float(input("r          :    "))
Chr = float(input("Chr        :    "))

# main routine
main()

exit(0)
