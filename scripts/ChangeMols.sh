#!/bin/bash

# takes all .top files and changes no of molecules from $old to $new

old=" 1"
new=" 1000"
WD=$PWD

for i in *.top
do
  no_line=`cat $i | wc -l`
  IFS=$' ' line=($(sed -n "${no_line}p" "$i"))
  line_new[0]=${line[0]}
  line_new[1]=$new
  echo ${line_new[*]}
  sed -i "${no_line}s/.*/${line_new[*]}/g" "$i"
  line_new=""
done

exit 0
