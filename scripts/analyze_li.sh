# TITLE		analyze_li.sh
# DESCRIPTION	Needs to be activated in an vdS-like simulation
#		folder. Analyses MD simulation. 	
# DATE		06.06.2017
# AUTHOR	Kay Schaller
# USAGE		./analyze_li.sh LIQ/GAS/SURF 1000/1000/1
# NOTES		Needs simulation type (LIQ/GAS/SURF) and number of
#		molecules in simulation as argument.
# =============================================================

#!/bin/bash

home=/cluster/work/igc/schreluk/freesolv/
WDIR=$PWD

if [[ ! -z "$2" ]]; then
 no_mol=$2
else
 no_mol=1
 echo "Number of molecules assumed to be 1. Give argument to change."
fi
if [[ ! -z "$1" ]]; then
  sim_typ=$1
else
  sim_typ="GAS"
  echo "Simulation assumed to be GAS-Typ. Give an argument to change."
fi


for i in */
do
cd $WDIR
if [[ ! -d $i/ ]]; then
	echo "LI for $i not yet done."
else
	cd $i
	i=`echo $i | rev | cut -d '/' -f2 | rev`
#	echo "${i}-run.part0001.log" 
	test=""
	test=`tail -n1 *.part0001.log | grep Finish`

	if [[ -z "$test" ]]; then
		echo "LI for $i incomplete!"	
	else
		if [[ ! -a "bar.log" ]]; then
			echo "LI for $i complete - calculating results."
			#bsub '
			g_energy_mpi -f ${i}-run.part0001.edr -nmol $no_mol -skip 100 -o bar.xvg < ${home}promp/g_energy_${sim_typ}.inp > bar.log
#-b 10000 -s ${i}.tpr -o -xvg xmgrace # < $home/../promp/g_energy_${sim_typ}.inp &> bar.log
#'
		else
			echo "TI for $i already calculated."
		fi
	fi
fi
  done

exit 0
