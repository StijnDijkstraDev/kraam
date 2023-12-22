from game import Game, VertId, parse_game, parse_solution, solution_size

import argparse
parser = argparse.ArgumentParser(
    prog='solsize',
    description='solsize is a tool that can determine the dominion of a parity game strategy given the game and the stategy'   
)

parser.add_argument('gamefile')
parser.add_argument('solfile')

args = parser.parse_args()

gamefile = open(args.gamefile, "r")
parity = int(gamefile.readline().strip("\n\r; ").split()[1])

game: Game = parse_game(args.gamefile)
solution: dict[VertId, VertId] = parse_solution(args.solfile)

print(str(parity) + ", " + str(solution_size(game, solution)))