#!/usr/bin/env python

from math import sqrt
from os import system
import sys

# Vector class
class Vector3:
    def __init__(self, *args):
        if len(args) == 3:
            self.X = args[0]
            self.Y = args[1]
            self.Z = args[2]

    def __iadd__(self, other):
        if type(other) is Vector3:
            X = self.X + other.X
            Y = self.Y + other.Y
            Z = self.Z + other.Z
            return Vector3(X, Y, Z)

    def __add__(self, other):
        if type(other) is Vector3:
            X = self.X + other.X
            Y = self.Y + other.Y
            Z = self.Z + other.Z
            return Vector3(X, Y, Z)

    def __sub__(self, other):
        if type(other) is Vector3:
            X = self.X - other.X
            Y = self.Y - other.Y
            Z = self.Z - other.Z
            return Vector3(X, Y, Z)

    def __imul__(self, other):
        if type(other) is float or type(other) is int:
            X = self.X * other
            Y = self.Y * other
            Z = self.Z * other
            return Vector3(X, Y, Z)

    def __mul__(self, other):
        if type(other) is float or type(other) is int:
            X = self.X * other
            Y = self.Y * other
            Z = self.Z * other
            return Vector3(X, Y, Z)

    def __truediv__(self, other):
        if type(other) is float or type(other) is int:
            X = self.X / other
            Y = self.Y / other
            Z = self.Z / other
            return Vector3(X, Y, Z)

    def magnitude(self):
        return sqrt(self.X ** 2 + self.Y ** 2 + self.Z ** 2)

    def normalized(self):
        return self / self.magnitude()

# Atom class
class Atom:
    def __init__(self):
        self.type = "X"
        self.P = Vector3()
        self.Q = 0.0
        self.Q0 = self.Q

    def __init__(self, *args):
        if len(args) == 3:
            self.type = args[0]
            self.P = args[1]
            self.Q = args[2]
            self.Q0 = self.Q

    def Qreset(self):
        self.Q = self.Q0

# Off class
class Off:
    def __init__(self, *args):
        if len(args) == 2:
            self.atom = args[0]
            self.off = Atom(1, atoms[self.atom].P, -QMAX)
            atoms[self.atom].Q -= self.off.Q
            self.displacement = Vector3(0.0, 0.0, 0.0)
            for i in args[1]:
                self.displacement += (atoms[self.atom].P - atoms[i].P)
            self.displacement = self.displacement.normalized() * RMAX
            self.DISPLACEMENTSTEP = self.displacement / RSTEPS

    def PlaceAtDistance(self, other):
        if type(other) is float:
            f = other / self.displacement.magnitude()
            self.off.P = atoms[self.atom].P + self.displacement * f

    def Rreset(self):
        self.off.P = atoms[self.atom].P

    def Rincrement(self):
        self.off.P += self.DISPLACEMENTSTEP

    def Qincrement(self):
        self.off.Q += QSTEP
        atoms[self.atom].Q -= QSTEP

def Dipole(atoms):
    D = Vector3(0.0, 0.0, 0.0)
    if type(atoms) is list:
        for item in atoms:
            D += item.P * item.Q
    elif type(atoms) is Atom:
        D = atoms.P * atoms.Q
    return D

def Error(QMDipole, DDECDipole):
    E = QMDipole - DDECDipole
    return float(E.X ** 2 + E.Y ** 2 + E.Z ** 2)

ANGSTROMPERA0 = 0.529177211
EAPERDEBYE = 0.20819434

# rm old log files
system("rm log/*")

# read job file
jobFile = sys.argv[1]
InFile = open(jobFile, "r")
buffer = InFile.read()
InFile.close()
lines = buffer.split("\n")
words = buffer.split()

FileName = words[0]
QMAX = float(words[1])
QSTEPS = int(words[2])
RMAX = float(words[3])
RSTEPS = int(words[4])
NSTEPS = int(words[5])

system("rm out/" + FileName + ".out")

QSTEP = QMAX / QSTEPS * 2

del(lines[0:4])

offsList = []

for line in lines:
    line = line.split()
    line = [int(item) for item in line]
    if len(line) >= 2:
        offsList.append([line[0], line[1:len(line)]])

# read log file
logFileName = "in/" + FileName + ".log"
InFile = open(logFileName, "r")
buffer = InFile.read()
buffer = buffer.split("\n")
InFile.close()

for i, line in enumerate(buffer):
    if "Dipole moment (field-independent basis, Debye)" in line:
        buffer = buffer[i + 1].split()
        QMDipole = Vector3(float(buffer[1]),
                           float(buffer[3]),
                           float(buffer[5]))

QMDipole *= EAPERDEBYE

# read cube file
cubeFileName = "in/" + FileName + ".cube"
InFile = open(cubeFileName, "r")
buffer = InFile.read()
buffer = buffer.split("\n")
InFile.close()

NATOMS = int(buffer[2].split()[0])

buffer = buffer[6:6+NATOMS]
atoms = []

for item in buffer:
    item = item.split()
    atoms.append(Atom(int(item[0]),
                      Vector3(float(item[2]), float(item[3]), float(item[4])) * ANGSTROMPERA0,
                      0.0))

# read DDEC file
DDECFileName = "in/DDEC6_even_tempered_net_atomic_charges.xyz"
InFile = open(DDECFileName)
buffer = InFile.read()
buffer = buffer.split("\n")
InFile.close()

buffer = buffer[2:2 + NATOMS]
for i, item in enumerate(buffer):
    item = item.split()
    atoms[i].Q = float(item[4])
    atoms[i].Q0 = atoms[i].Q

DDECDipole = Vector3(0.0, 0.0, 0.0)
for item in atoms:
    DDECDipole += (item.P * item.Q)
E = Error(QMDipole, DDECDipole)

# print debug info
print("ID\t\tType\t\tX\t\tY\t\tZ\t\tQ")
for i, item in enumerate(atoms):
    print(str(i) + "\t\t"
          + str(item.type) + "\t\t"
          + str(round(item.P.X, 5)) + "\t\t"
          + str(round(item.P.Y, 5)) + "\t\t"
          + str(round(item.P.Z, 5)) + "\t\t"
          + str(round(item.Q, 5)))
print("\n")

print("\t\tX\tY\tZ\ttot\tError")
print("QM Dipole\t"
      + str(round(QMDipole.X, 3)) + "\t"
      + str(round(QMDipole.Y, 3)) + "\t"
      + str(round(QMDipole.Z, 3)) + "\t"
      + str(round(QMDipole.magnitude(), 3)) + "\t"
      + "-----")
print("DDEC Dipole\t"
      + str(round(DDECDipole.X, 3)) + "\t"
      + str(round(DDECDipole.Y, 3)) + "\t"
      + str(round(DDECDipole.Z, 3)) + "\t"
      + str(round(DDECDipole.magnitude(), 3)) + "\t"
      + str(round(E, 3)))
print()

# create offsite charges
offs = []

for i, item in enumerate(offsList):
#    print("---")
    offs.append(Off(item[0], item[1]))
#    print(atoms[offs[i].atom].type, atoms[offs[i].atom].P.X,
#          atoms[offs[i].atom].P.Y, atoms[offs[i].atom].P.Z,
#          atoms[offs[i].atom].Q)
#    print(offs[i].off.type, offs[i].off.P.X, offs[i].off.P.Y, offs[i].off.P.Z,
#          offs[i].off.Q)
#    print(offs[i].displacement.X, offs[i].displacement.Y,
#          offs[i].displacement.Z, offs[i].displacement.magnitude())
#    print(offs[i].DISPLACEMENTSTEP.X, offs[i].DISPLACEMENTSTEP.Y,
#          offs[i].DISPLACEMENTSTEP.Z, offs[i].DISPLACEMENTSTEP.magnitude())
#print("---")

# scanning algorithm
OfFile = open("log/offsite.log", "w")

for i in range(0, QSTEPS + 1):

    for item in offs:
        item.Rreset()

    for j in range(0, RSTEPS + 1):

        # calculate Dipole, Error, write to file
        allAtoms = []
        for item in atoms:
            allAtoms.append(item)
        for item in offs:
            allAtoms.append(item.off)

        DDECDipole = Dipole(allAtoms)
        E = Error(QMDipole, DDECDipole)

        OfFile.write(str(round(offs[0].off.Q, 3)) + ","
                     + str(round((offs[0].off.P - atoms[offs[0].atom].P).magnitude(), 3)) + ","
                     + str(E) + "\n")

        for item in offs:
            item.Rincrement()

    for item in offs:
        item.Qincrement()

OfFile.close()

for item in atoms:
    item.Qreset()

for item in offs:
    item.off.Qreset()
    item.Rreset()

# call R script
system("Rscript src/2Dgridsearch.R")

# read fitdata
InFile = open("log/fitdata.log", "r")

buffer = InFile.read()
buffer = buffer.split("\n")
Nfit = int(buffer[0])

Rfit = []
Qfit = []

for item in buffer:
    item = item.split()
    if len(item) == 2:
        Rfit.append(float(item[0]))
        Qfit.append(float(item[1]))

InFile.close()

# create RMSE test data for fit data
NSTEP = int(round(Nfit / NSTEPS, 0))

# copy cubefile, insert dummy lines for dummy hydrogens
InFile = open(cubeFileName, "r")
OfFile = open("log/potential.cube.bk", "w")

buffer = InFile.read()
buffer = buffer.split("\n")

for i in range(0, 6):
    OfFile.write(buffer[i] + "\n")

for i, item in enumerate(offs):
    OfFile.write(str(i) + " XXXXX\n")

for i in range(6, len(buffer)):
    OfFile.write(buffer[i] + "\n")

InFile.close()
OfFile.close()

# generate partial_charges_data.m.bk, add dummy lines
OfFile = open("log/partial_charges_data.m.bk", "w")

OfFile.write("partial_charge = [\n")
for i, item in enumerate(offs):
    OfFile.write(str(i) + " XXXXX\n")

for item in atoms:
    OfFile.write(str(round(item.Q, 6)) + "\n")

OfFile.write("]\n\natomic_number = [\n")

for item in offs:
    OfFile.write("1\n")

for item in atoms:
    OfFile.write(str(item.type) + "\n")

OfFile.write("]\n\natomic_dipole = [\n")

for item in offs:
    OfFile.write(" 0.000000     0.000000     0.000000\n")

for item in atoms:
    D = Dipole(item)
    OfFile.write(str(round(D.X, 6)) + "\t" + str(round(D.Y, 6)) + "\t"
                 + str(round(D.Z, 6)) + "\n")

OfFile.write("];\n")

OfFile.close()

# TODO: RMSE loop
n = 1

for i in range(0, NSTEPS):

    # TODO: place offsite charges
    for item in offs:
        item.off.Q = Qfit[n]
        atoms[item.atom].Q = atoms[item.atom].Q0 - item.off.Q
        item.PlaceAtDistance(Rfit[n])
        print(Rfit[n], (item.off.P - atoms[item.atom].P).magnitude(), item.off.Q, atoms[item.atom].Q)

    # TODO: manipulate potential.cube, partial_charges_data
    system("cp log/potential.cube.bk log/potential.cube")
    system("cp log/partial_charges_data.m.bk log/partial_charges_data.m")

    for j, item in enumerate(offs):
        system("sed -i '" + str(j + 2) + "s/.*/" + str(item.off.Q)
               + "/' log/partial_charges_data.m")
        system("sed -i '" + str(item.atom + 2 + len(offs))
               + "s/.*/" + str(atoms[item.atom].Q)
               + "/' log/partial_charges_data.m")
        system("sed -i '" + str(j + 7) + "s/.*/    1    1.000000    "
               + str(round(item.off.P.X / ANGSTROMPERA0, 6)) + "    "
               + str(round(item.off.P.Y / ANGSTROMPERA0, 6)) + "    "
               + str(round(item.off.P.Z / ANGSTROMPERA0, 6)) + "    "
               + "/' log/potential.cube")

    # call m script
    # system("octave --no-gui -q src/calculate_nonperiodic_RRMSE.m | tee log/RRMSE.log")
    system("matlab -nojvm -nodisplay -nosplash -r \"addpath src; addpath log; "
           + "calculate_nonperiodic_RRMSE; exit\" | tee log/RRMSE.log")

    # TODO: write to a file
    InFile = open("log/RRMSE.log")
    buffer = InFile.read()
    buffer = buffer.split("\n")
    InFile.close()

    OfFile = open("out/" + FileName + ".out", "a")

    OfFile.write(str(Rfit[n]) + ",")
    OfFile.write(str(Qfit[n]) + ",")
    for item in buffer:
        if "RMSE" in item and "=" in item:
            OfFile.write(str(buffer[buffer.index(item) + 2]) + ",")
    OfFile.write("\n")

    OfFile.close()

    n += NSTEP

# TODO: ESP scan???
