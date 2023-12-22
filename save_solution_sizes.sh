#!/usr/bin/bash
cd ~/testdata/examples
for file in *
    #do echo "$file"
    do
    python3 ~/kraam/solsize.py ~/testdata/examples/"$file" ~/testdata/examples_sol/"$file".sol
done