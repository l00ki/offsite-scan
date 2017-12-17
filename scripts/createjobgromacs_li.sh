#!/bin/bash


getfilename () {                                                                
                                                                                 
     args=`echo $1 | awk -F"." '{print NF}'`                                     
     getfilenameout=$1                                                           
     if [ ${args} -gt 1 ]; then                                                  
                                                                                 
         getfilenameout=`echo $1 | awk -F'.' '{for(i=1;i<NF-1;i++){printf "%s.", $i}; printf "%s\n", $    (NF-1)}'`
                                                                                 
     fi                                                                          
                                                                                 
} # end of function getfilename () { 



getscriptname () {

   args=`echo $1 | awk -F"/" '{print NF}'`

   scriptname=`echo $1 | awk -F"/" -v var=$args '{print $var}'`

} # end of function getscriptname ()



printError () {

    getscriptname $0
    echo "Error in usage."
    echo "Type: $scriptname <inputfile> [jobname]"
    echo ""

    exit 1
}


file=""
nname=""

if ( test $# -lt 1 ); then

     printError

elif ( test $# -eq 1 ); then

    file=$1
    getfilename $1

    nname=$getfilenameout


elif ( test $# -eq 2 ); then

    file=$1
    getfilename $1

    nname=$2
    echo ${nname}


elif ( test $# -gt 2 ); then

    printError

fi

filename=$getfilenameout".job"

echo "#" > $filename
echo "#BSUB -J ${nname}" >> $filename
echo "#BSUB -oo ${nname}.o" >> $filename
#echo "#BSUB -e $nname.e " >> $filename
echo "#BSUB -W 24:00" >> $filename # was set to 36h
echo "#BSUB -n 10" >> $filename
echo "#BSUB -sp 100" >> $filename
echo "#BSUB -R rusage[scratch=600]" >> $filename
echo "" >> $filename
echo "# Executing GROMACS" >> $filename
echo "cd $PWD" >> $filename
echo "mpirun mdrun_mpi -s $file -deffnm ${getfilenameout}-run -noappend -cpi ${getfilenameout}-run.cpt" >> $filename
echo "" >> $filename

