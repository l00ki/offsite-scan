# TITL SwapCharges.sh
# DESC swaps charges of a batch of .top files with corresponding .charg files
#      and saves them to a new *_swapped folder.
# DATE 02/11/2017
# AUTH Lukas Schreder
# USAG ./SwapCharges TOP-dir CHARG-dir
# NOTE -
# =============================================================================

#!/bin/bash

topdir=$1
chrdir=$2

swpdir="${topdir}_swapped"
chrend=".charg"
sdfdir="/cluster/work/igc/schreluk/freesolv/li_sdf"

if [ ! -d "$swpdir" ]
then
  mkdir $swpdir
fi

for i in $topdir/*.top
do
  fn=`echo $i | rev | cut -d '/' -f1 | rev`
  fn=`echo $fn | cut -d '.' -f1`
  cp $i $swpdir/${fn}.top 

  if [ ! -e "$chrdir/${fn}${chrend}" ]
  then
    echo "'${fn}${chrend}' not found"
    rm $swpdir/${fn}.top
  fi

  ncharg=$(wc -l < "${chrdir}/${fn}${chrend}")
  last=$(sed -n "${ncharg}p" "$chrdir/${fn}${chrend}")

  if [ -z $last ]
  then
    ncharg=$((ncharg-1))
  fi

  start=`grep -n -F "[ atoms ]" ${swpdir}/${fn}.top | cut -d ':' -f1`

  i=$((start+1))
  j="1"
  l=0
  line="start"
  
  while [ -n "$line" ]
  do
    i=$((i+1))
    IFS=$' ' line=($(sed -n "${i}p" "${swpdir}/${fn}.top"))
    if [ -n "${line[*]}" ]
    then
      line_new=$(sed -n "${j}p" "$chrdir/${fn}${chrend}")
      j=$((j+1))
      element_top="${line[4]//[0-9]/}"
      k=$((i-start-1+4))
      IFS=$' ' sdf=($(sed -n "${k}p" "${sdfdir}/${fn}.sdf"))
      element_sdf=${sdf[3]}
      element_sdf=`echo $element_sdf | tr /a-z/ /A-Z/`
      element_top=`echo $element_top | tr /a-z/ /A-Z/`

      if [ ! "$element_top" == "$element_sdf" ]
      then
        echo "$fn $((i-start-1)) $element_top vs $element_sdf" >> \
        "messed_order.o"
        "messed_order.o"
        l=$((l+1))
      fi

      sed -i "${i}s/${line[6]}/${line_new}/g" "${swpdir}/${fn}.top"

      line_new=""
    fi
  done

  if [ ! $((i-2-start)) = $ncharg ]
  then
    echo "Error no of atoms in .top and $chrend does not match for $fn"
    rm ${swpdir}/${fn}.top
  else
    if [ "$l" == "0" ]
    then
      echo "Swapped .top file created for $fn in $swpdir"
    else
      mess_count=$((mess_count+1))
      l="0"
      echo "Warning - molecule $fn has a messed order. Details written in to
      messed_order.o"
    fi
  fi
done

if [ ! "$mess_count" == "0" ]
then
  echo "Warning - there was/were $mess_count molecule/s omitted due to a messed
  atomic order between the .top and .sdf file. See messed_order.o for details."
else
  rm "messed_order.o"
fi

