from threading import Thread
from game import Game, VertId, Priority, export_to_file, flatten_game, realise_subgame
from game import parse_game, find_problems
from sdsi import SDSI
import sys
import cProfile

def parse_process_export(srcfile: str, destfile: str, startvertex : VertId, algo, multithreaded: bool):
    game = parse_game(sys.argv[1])
    print(game)

    algo : SDSI = SDSI(game, VertId(0))
    
    subgameconf = algo.prune()
    found : bool = len(subgameconf) > 0
    size = 1
    while algo.increase_reach(1):
        size += 1
        subgameconf = algo.prune()
        if len(subgameconf) > 0:
            if multithreaded:
                print("new thread started")
                thread = Thread(target=export_subgame_config, args=(game, subgameconf, startvertex, size, destfile))
                thread.start()
            else:
                export_subgame_config(game, subgameconf, startvertex, size, destfile)
    
    

def export_subgame_config(game: Game, subgameconf: set[VertId], startvertex, size, destfile):
    subgame = realise_subgame(game, subgameconf)
    subgame, startvertex = flatten_game(subgame, startvertex)
    export_to_file(subgame, sys.argv[2] + "_" + str(size))

if (len(sys.argv) == 5 and sys.argv[4] == "multithreaded") :
    cProfile.run("parse_process_export(sys.argv[1], sys.argv[2], VertId(int(sys.argv[3])), SDSI, True)")
else:
    cProfile.run("parse_process_export(sys.argv[1], sys.argv[2], VertId(int(sys.argv[3])), SDSI, False)")