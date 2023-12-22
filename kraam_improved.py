import itertools
from threading import Thread
from game import Game, VertId, Priority, export_to_file, find_problems_on_specified_verts, flatten_game, parse_solution, realise_subgame, solution_domain, solution_size
from game import parse_game, find_problems
from sdsi import SDSI
from sdsi_bidirectional import SDSI_bidirectional
from sdsi_reverse import SDSI_reverse
import cProfile
import argparse
import os
import shutil
import math

CMD_NO_OUT_STR: str = " >/dev/null 2>&1"

def parse_findsolution_export(algo_to_use):
    # temporary directory unique to this process
    pid = os.getpid()
    temp_dir = "./kraam_temp_" + str(pid)
    os.mkdir(temp_dir)
    temp_path = temp_dir + "/temp"
    
    winning_subgames: set[frozenset[VertId]] = set()
    subgame_stack: list[set[VertId]] = list()
    
    game: Game = parse_game(args.inputfile)
    
    (vertices, init, priority, owned, outEdges, incEdges) = game
    subgame_stack.append(set(vertices))
    
    # solve, the size of the solution will be used as the max size of any future subgames
    totalsize: int = len(vertices)
    best_subgame: set[VertId] = get_solution_domain(game, vertices, temp_path)
    best_solsize: int = len(best_subgame)
    found_smallest = False
    
    
    while True:
        subgames_checked: set[frozenset[VertId]] = set()
        improvement = False
        # init vertex is removed and then added back so that each subgraph contains the init vertex
        # subtract 2 from minsize. One because the init vertex will be added,
        # the other because we are only looking for _smaller_ subgraphs
        print("best_solsize: " + str(best_solsize))
        num_options = math.factorial(totalsize) / (math.factorial(best_solsize) * math.factorial(totalsize - best_solsize))
        print("that means " + str(num_options) + " options")
        for sg in set(itertools.combinations(vertices - {VertId(0)}, best_solsize - 2)):
            subgraph: set[VertId] = set(sg)
            subgraph.add(VertId(0))
            subgame = prune(game, subgraph)
            if len(subgame) < 2:
                continue
            
            if frozenset(subgame) in subgames_checked:
                continue
            
            subgames_checked.add(frozenset(subgame))
            
            if not check_solvable(game, subgame, temp_path):
                continue
            
            best_subgame = get_solution_domain(game, subgame, temp_path + ".sol")
            best_solsize = len(best_subgame)
            improvement = True
            break
        
        # exit condition: no improvement in last run
        if not improvement:
            break
            
    print("solution size: " + str(best_solsize))
    print("solution: " + str(best_subgame))
    export_subgame_config(game, best_subgame, args.outputfolder)

    shutil.rmtree(temp_dir)
    
        
    
def check_solvable(game: Game, subgameconf: set[VertId], temp_path: str) -> bool:
    export_subgame_config(game, subgameconf, temp_path)
    os.system("oink " + temp_path + " " + temp_path + ".sol" + CMD_NO_OUT_STR)
    solfile = open(temp_path + ".sol", "r")
    solfile.readline() # skip first line
    # tempfile does not need to be deleted, will be overwritten and deleted at the end
    return solfile.readline().strip("\n\r;").split()[1] == "0"

def get_solution_size(game: Game, subgameconf: set[VertId], temp_path: str) -> int:
    export_subgame_config(game, subgameconf, temp_path)
    os.system("oink " + temp_path + " " + temp_path + ".sol" + CMD_NO_OUT_STR)
    return solution_size(game, parse_solution(temp_path + ".sol"))

def get_solution_domain(game: Game, subgameconf: set[VertId], temp_path: str) -> set[VertId]:
    export_subgame_config(game, subgameconf, temp_path)
    os.system("oink " + temp_path + " " + temp_path + ".sol" + CMD_NO_OUT_STR)
    return solution_domain(game, parse_solution(temp_path + ".sol"))
    
    
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