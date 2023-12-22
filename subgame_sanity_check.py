import argparse
import os
parser = argparse.ArgumentParser()

parser.add_argument('name')
args = parser.parse_args()


old = open(os.path.expanduser('~') + "/testdata/examples/" + args.name, "r")
new = open(os.path.expanduser('~') + "/testdata/reduced_sol/" + args.name + "/subgame.pg", "r")

oldparity = int(old.readline().strip("\n\r; ").split()[1])
newparity = int(new.readline().strip("\n\r; ").split()[1])

if (oldparity != newparity):
    print("FOUND PARITY DIFFERENCE!")