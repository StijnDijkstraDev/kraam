#!/usr/bin/bash
cd ~/testdata/examples
for file in *
do
    old="$(python3 ~/kraam/solsize.py "$file" ../examples_sol/"$file".sol)"
    if test -f ../reduced_sol/"$file"/subgame.pg
    then
        sdsi="$(python3 ~/kraam/solsize.py ../SDSI/"$file"/subgame.pg ../SDSI/"$file"/subgame.pg.sol)"
        sdsibi="$(python3 ~/kraam/solsize.py ../SDSI-BI/"$file"/subgame.pg ../SDSI-BI/"$file"/subgame.pg.sol)"
        sdsirev="$(python3 ~/kraam/solsize.py ../SDSI-REV/"$file"/subgame.pg ../SDSI-REV/"$file"/subgame.pg.sol)"
        echo "$file"
        echo "original: $old, sdsi: $sdsi, sdsi-bi: $sdsibi, sdsi-rev: $sdsirev"
    fi
done