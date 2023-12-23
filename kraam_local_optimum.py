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
TOPSIZE = 10

def parse_findsolution_export():
    # temporary directory unique to this process
    pid = os.getpid()
    temp_dir = "./kraam_temp_" + str(pid)
    os.mkdir(temp_dir)
    temp_path = temp_dir + "/temp"
        
    game: Game = parse_game(args.inputfile)
    
    (vertices, init, priority, owned, outEdges, incEdges) = game
    
    # solve, the size of the solution will be used as the max size of any future subgames
    totalsize: int = len(vertices)
    
    subgames_evaluated: set[frozenset[VertId]] = set()
    
    subgame_perf: dict[frozenset[VertId], int] = dict()
    # set full game as initial subgame
    subgame_perf[frozenset(vertices)] = get_solution_size(game, vertices, temp_path)
    
    while True:
        last_best = min(subgame_perf.values())
        
        not_evaluated = (subgame_perf.keys() - subgames_evaluated)
        to_check = get_perf_order({k:v for k,v in subgame_perf.items() if k in not_evaluated})
        subgames_evaluated |= not_evaluated
        for i in range(min(TOPSIZE, len(to_check))):
            sg = to_check[i]

            for v in sg:
                if v == VertId(0):
                    continue
                newsg: frozenset[VertId] = frozenset(prune(game, set(sg-{v})))
                if len(newsg) < 2:
                    continue
                
                if newsg in subgame_perf.keys():
                    continue
                
                if not check_solvable(game, set(newsg), temp_path):
                    continue
                
                subgame_perf[frozenset(newsg)] = get_solution_size(game, set(newsg), temp_path)
                
        
        if not last_best > min(subgame_perf.values()):
            break
            
    
    best_perf = min(subgame_perf.values())
    best_subgames = [k for k in subgame_perf if subgame_perf[k] == best_perf]
    smallest_subgame = get_solution_domain(game, set(best_subgames[0]), temp_path)
    print("solsize: " + str(len(smallest_subgame)))
    print("smallest subgame: " + str(smallest_subgame))
    export_subgame_config(game, smallest_subgame, args.outputfolder)

    shutil.rmtree(temp_dir)
    


def get_perf_order(perf_order: dict[frozenset[VertId], int]) -> list[frozenset[VertId]]:
    return [k for k, _ in sorted(perf_order.items(), key=lambda item:item[1])]
    
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
    parse_findsolution_export()


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