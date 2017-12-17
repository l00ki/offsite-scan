# Offsite-scan

Tool to find suitable parametrizations for virtual sites to approximate charge anisotropies.

Usage:
1. Place in in/: DDEC6_even_tempered_net_atomic_charges.xyz from Chargemol output, Gaussian density .cube file and Gaussian .log file
2. write a jobfile
```
<name of cubefile and logfile without extension>
<maximum magnitude in elemental charges> <number of charge steps, 100 are plenty>
<maximum distance in Angstrom> <number of distance steps, 100 are plenty>
<steps for ESP scan, 100 steps are plenty>
<number of 1st anistropic atom> <numbers of atoms constructing the displacement vector, separated by single spaces>
<number of 2nd anistropic atom> <numbers of atoms constructing the displacement vector, separated by single spaces>
...
<number of ith anistropic atom> <numbers of atoms constructing the displacement vector, separated by single spaces>
```
3. run
```
./run.sh <jobfile>
```
4. out/ contains the ESP error curve. Find the minimum for the initial parameters.
