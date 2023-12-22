from threading import Thread
from game import Game, VertId, Priority, export_to_file, find_problems_on_specified_verts, flatten_game, realise_subgame
from game import parse_game, find_problems
from sdsi import SDSI
from sdsi_bidirectional import SDSI_bidirectional
from sdsi_reverse import SDSI_reverse
import cProfile
import argparse
import os
import shutil



def parse_findsolution_export(algo_to_use):
    # temporary directory unique to this process
    pid = os.getpid()
    temp_path = "./kraam_temp_" + str(pid)
    os.mkdir(temp_path)
    
    winning_subgames: set[frozenset[VertId]] = set()
    subgame_stack: list[set[VertId]] = list()
    
    game: Game = parse_game(args.inputfile)
    
    (vertices, init, priority, owned, outEdges, incEdges) = game
    subgame_stack.append(set(vertices))
    
    # find all subgames configurations that have a winning strategy
    while subgame_stack:
        subgameconf = subgame_stack.pop() # get non-frozen copy of set
        print("subgame collection: " + str(len(winning_subgames)))
        print("stacksize: " + str(len(subgame_stack)))
        for v in subgameconf:
            if v == VertId(0):
                continue
            newsubgameconf: set[VertId] = prune(game, subgameconf - {v})
            if not newsubgameconf:
                # no subgame found
                continue
            
            exists = False
            for s in winning_subgames:
                if s == frozenset(newsubgameconf):
                    exists = True
                    break
            if exists: continue
            
            if frozenset(newsubgameconf) in winning_subgames:
                # allready in set
                continue
            if not check_solvable(game, newsubgameconf, temp_path + "/temp"):
                # not solvable
                continue
            
            winning_subgames.add(frozenset(newsubgameconf))
            subgame_stack.append(newsubgameconf)

    # debug print all subgames
    print("subgames found:")
    for s in winning_subgames:
        print(s)
        print("")
        
    # get smallest
    smallest: frozenset[VertId] = list(winning_subgames)[0]
    for s in winning_subgames:
        if len(s) < len(smallest):
            smallest = s
    
    print(smallest)
    export_subgame_config(game, set(smallest), args.outputfolder)
        
    shutil.rmtree(temp_path)
    
        
    
def check_solvable(game: Game, subgameconf: set[VertId], temppath: str) -> bool:
    export_subgame_config(game, subgameconf, temppath)
    os.system("oink " + temppath + " " + temppath + ".sol >/dev/null 2>&1")
    solfile = open(temppath + ".sol", "r")
    solfile.readline() # skip first line
    # tempfile does not need to be deleted, will be overwritten and deleted at the end
    return solfile.readline().strip("\n\r;").split()[1] == "0"
    
def prune(game: Game, potentialconf: set[VertId]) -> set[VertId]:
    (_, init, _, _, _, incEdges) = game
    
    pruneResult = potentialconf.copy()
    
    (rule1breaks, rule2breaks) = find_problems(game, pruneResult)
    while not (len(rule1breaks) == 0 and len(rule2breaks) == 0):
        pruneTargets = set(rule1breaks.keys()) | rule2breaks
        if init in pruneTargets:
            return set()
        pruneResult -= pruneTargets
        
        # find out which vertices may now become an issue
        newlyExposedVerts : set[VertId] = set()
        for v in pruneTargets:
            newlyExposedVerts |= incEdges[v]
        (rule1breaks, rule2breaks) = find_problems_on_specified_verts(game, pruneResult, newlyExposedVerts)

    return pruneResult

def export_subgame_config(game: Game, subgameconf: set[VertId], destfile: str):
    subgame = realise_subgame(game, subgameconf)
    #print("subgame:\n" + str(subgame) + "\n\n")
    subgame = flatten_game(subgame)
    #print("flattened subgame:\n" + str(subgame) + "\n\n")
    export_to_file(subgame, destfile)


def main_func():
    match args.algorithm:
        case 'SDSI':
            parse_findsolution_export(SDSI)
        case 'SDSI-BI':
            parse_findsolution_export(SDSI_bidirectional)
        case 'SDSI-REV':
            parse_findsolution_export(SDSI_reverse)
        case _:
            print("Algorithm not recognized!")
            print("Available: 'SDSI', 'SDSI-BI', 'SDSI-REV")


parser = argparse.ArgumentParser(
    prog='kraam',
    description='kraam is a tool that can find subgames of parity games.'
)
parser.add_argument('inputfile')
parser.add_argument('outputfolder')
parser.add_argument('-algo', '--algorithm', default = 'SDSI')
parser.add_argument('-sv', '--initialvertex', default=0)
parser.add_argument('-p', '--profile', action='store_true')
parser.add_argument('-mt', '--multithreaded', action='store_true')
parser.add_argument('-opf', '--optimizedproblemfinder', action='store_true')

args = parser.parse_args()

if (args.profile):
    cProfile.run("main_func()")
else:
    main_func()