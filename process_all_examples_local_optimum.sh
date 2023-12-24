#!/usr/bin/bash
cd ~/testdata/examples
for file in *
    #do echo "$file"
    do
    timeout 100s python3 ~/kraam/kraam_local_optimum.py ~/testdata/examples/"$file" ~/testdata/local_optimum/"$file"
    #timeout 10s python3 ~/kraam/kraam_local_optimum.py ~/testdata/examples/"$file" ~/testdata/local_optimum_sda/"$file" -sda

done