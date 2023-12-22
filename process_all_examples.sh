#!/usr/bin/bash
cd ~/testdata/examples
for file in ./*
    #do echo "$file"
    do
    python3 ~/kraam/kraam.py ~/testdata/examples/"$file" ~/testdata/SDSI/"$file" -algo "SDSI" -p
    python3 ~/kraam/kraam.py ~/testdata/examples/"$file" ~/testdata/SDSI-BI/"$file" -algo "SDSI-BI" -p
    python3 ~/kraam/kraam.py ~/testdata/examples/"$file" ~/testdata/SDSI-REV/"$file" -algo "SDSI-REV" -p
done