#!/bin/bash
#
# creates a subfolder for each .top/.pdb pair, creates a GROMACS job and
# submits it. Requires the included forcefield in .itp format. Specify LIQ or
# GAS with $1.

lib=/cluster/work/igc/schreluk/MD5/lib/MDP

if [ -z "$1" ]
then
  echo "specify a method"
  exit 1
fi

libfile=$1

for i in *.top
do
  i=`echo $i | cut -d '.' -f1`
  echo $i

  if [ -d $i ]
  then
    echo "$i has already been created"
    continue 
  fi

  mkdir $i
  cd $i
  cp ../${i}.top .
#  cp ../${i}.gro conf.gro
  cp ../${i}.pdb conf.pdb
  cp ../*.itp .
  mdp=`echo "$lib/production.${libfile}.ALLBONDS.mdp"`
  cp $mdp ./grompp.mdp

#  grompp_mpi -c conf.gro -p ${i}.top -o ${i}.tpr -maxwarn 30
  grompp_mpi -c conf.pdb -p ${i}.top -o ${i}.tpr -maxwarn 30

  if [ $? -ne 0 ]
  then
    echo "grompp_mpi exited with status $?"
    continue
  fi

  createjobgromacs_li ${i}.tpr ${i}
  bsub < ${i}.job

  cd ..
done

exit 0
