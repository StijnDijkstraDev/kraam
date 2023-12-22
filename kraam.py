from threading import Thread
from game import Game, VertId, Priority, export_to_file, flatten_game, realise_subgame
from game import parse_game, find_problems
from sdsi import SDSI
from sdsi_bidirectional import SDSI_bidirectional
from sdsi_reverse import SDSI_reverse
import cProfile
import argparse
import os
import shutil

def parse_process_export(algo_to_use):
    # empty or create destination folder
    if os.path.exists(args.outputfolder):
        for file in os.listdir(args.outputfolder):
            os.remove(os.path.join(args.outputfolder, file))
    else:
        os.mkdir(args.outputfolder)
    
    
    game = parse_game(args.inputfile)
    #print(game)

    (parentVerts, _, _, _, _, _) = game
    parentlen = len(parentVerts)
    algo : algo_to_use = algo_to_use(game, VertId(0))
    
    subgameconf = algo.prune()
    subgamelen = len(subgameconf)
    size = 1
    while algo.increase_reach(1):
        size += 1
        subgameconf = algo.prune_subset_optimized()
        subgamelen = len(subgameconf)
        if subgamelen == parentlen:
            break
        
        if subgamelen <= 1:
            continue
        
        if args.multithreaded:
            print("new thread started")
            thread = Thread(target=export_subgame_config, args=(game, subgameconf, args.outputfolder + "/" + str(size) + ".pg"))
            thread.start()
        else:
            export_subgame_config(game, subgameconf, args.outputfolder + "/" + str(size) + ".pg")
    
def parse_findsolution_export(algo_to_use):
    # empty or create destination folder
    if os.path.exists(args.outputfolder):
        for file in os.listdir(args.outputfolder):
            os.remove(os.path.join(args.outputfolder, file))
    else:
        os.mkdir(args.outputfolder)
    
    # temporary directory unique to this process
    pid = os.getpid()
    temp_path = "./kraam_temp_" + str(pid)
    os.mkdir(temp_path)
    
    
    
    game: Game = parse_game(args.inputfile)
    
    (parentVerts, _, _, _, _, _) = game
    parentlen = len(parentVerts)
    algo : algo_to_use = algo_to_use(game, VertId(0))
    
    subgameconf = algo.prune()
    subgamelen = len(subgameconf)
    size = 1
    while algo.increase_reach(1):
        size += 1
        subgameconf = algo.prune_subset_optimized()
        subgamelen = len(subgameconf)
        
        if subgamelen <= 1:
            continue
        
        # no multithreading possible
        export_subgame_config(game, subgameconf, temp_path + "/subgame.pg")
        
        # check if solvable
        os.system("oink '" + temp_path + "/subgame.pg' '" + temp_path + "/subgame.pg.sol'")
        solfile = open(temp_path + "/subgame.pg.sol", "r")
        solfile.readline()
        winner_int = solfile.readline().strip("\n\r;").split()[1]
        print("winner int: " + winner_int)
        if winner_int == "0":
            print("found winner")
            print("copied solution to: " + args.outputfolder)
            # solution found, storing in desired location
            shutil.copyfile(
                temp_path + "/subgame.pg",
                args.outputfolder + "/subgame.pg"
            )
            shutil.copyfile(
                temp_path + "/subgame.pg.sol",
                args.outputfolder + "/subgame.pg.sol"
            )
            break
        
        if subgamelen == parentlen:
            break

    shutil.rmtree(temp_path)
    
    
        
    
    
    

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