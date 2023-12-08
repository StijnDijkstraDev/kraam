from game import Game, VertId, Priority
from game import is_valid_subgame, find_problems


class SDSI:
    def __init__(self, game: Game, start: VertId):
        self.game : Game = game
        self.start : VertId = start
        self.size : int = 1 # add 1 because the starting vertex is added by default
        self.reach : set[VertId] = {start}

    def increase_reach(self, times: int) -> bool:
        increased: bool = False
        (pVertices, pPriority, pOwned, pOutEdges, pIncEdges) = self.game
        for i in range(times):
            nextReach: set[VertId] = set()
            for v in self.reach:
                nextReach = nextReach | pOutEdges[v]
            
            if len(nextReach - self.reach) != 0:
                increased = True
            self.reach = self.reach | nextReach
            self.size += 1
        
        return increased
            
    def prune(self) -> set[VertId] :
        pruneResult = self.reach.copy()
        (rule1breaks, rule2breaks) = find_problems(self.game, pruneResult)
        while not (len(rule1breaks) == 0 and len(rule2breaks) == 0):
            pruneResult -= set(rule1breaks.keys())
            pruneResult -= rule2breaks
            (rule1breaks, rule2breaks) = find_problems(self.game, pruneResult)

        return pruneResult
    