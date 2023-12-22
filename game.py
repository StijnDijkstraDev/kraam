from operator import contains
from typing import TypeAlias
from typing import NewType
import sys

VertId = NewType('VertId', int)
Priority = NewType('Priority', int)
Game: TypeAlias = tuple[set[VertId], VertId, dict[VertId, Priority], set[VertId], dict[VertId, set[VertId]], dict[VertId, set[VertId]]]

def parse_game(filename: str, initVert: VertId = VertId(0)) -> Game:
    file = open(filename, 'r')
    num_vertices = int(file.readline().strip("\n\r; parity"))
    vertices = set(map(VertId, range(num_vertices)))
    priority : dict[VertId, Priority] = dict()
    owned : set[VertId] = set()
    outEdges : dict[VertId, set[VertId]] = dict()
    incEdges : dict[VertId, set[VertId]] = dict()
    
    for i in range(num_vertices):
        outEdges[VertId(i)] = set()
        incEdges[VertId(i)] = set()
    
    for i in range(num_vertices):
        line = file.readline()
        line = line.strip("\n\r;")
        splitline = line.split()
        id : VertId = VertId(int(splitline[0]))
        priority[id] = Priority(int(splitline[1]))
        if (splitline[2] == "0"):
            owned.add(id)
        
        outEdges[id] = set(map(VertId, map(int, splitline[3].split(','))))
        for otherId in outEdges[id]:
            incEdges[otherId].add(id)
        
        if len(splitline) == 5 and splitline[4] == "initial":
            initVert = id
            
    file.close()
    return (vertices, initVert, priority, owned, outEdges, incEdges)
    
def is_valid_subgame(parent: Game, cVertices: set[VertId]) -> bool:
    (pVertices, pInit, pPriority, pOwned, pOutEdges, pIncEdges) = parent
    
    # check that there are no opponent vertices with externally outgoing edges
    # only consider vertices that are _not_ owned
    oppVertices = {v for v in cVertices if v not in pOwned}
    nextFromOppVerts = set()
    for v in oppVertices:
        nextFromOppVerts |= pOutEdges[v]
    
    extVertices = pVertices - cVertices
    if len(nextFromOppVerts & extVertices) != 0:
        print("These external vertices can be reached from the subgame:")
        print(nextFromOppVerts & extVertices)
        return False
    
    # check that each even vertex has at least one outgoing edge with a destination within the subgame
    ownedVertices = {v for v in cVertices if v in pOwned}
    for v in ownedVertices:
        if len(pOutEdges[v] & cVertices) == 0:
            print("Vertex " + str(v) + " has no internally outgoing edges.")
            return False
        
    return True
    
    
def find_problems(parent: Game, cVertices: set[VertId]) -> tuple[dict[VertId, set[VertId]], set[VertId]]:
    (pVertices, pInit, pPriority, pOwned, pOutEdges, pIncEdges) = parent
    
    # check that there are no opponent vertices with externally outgoing edges
    # only consider vertices that are _not_ owned
    oppVertices = {v for v in cVertices if v not in pOwned}
    
    rule1breaks: dict[VertId, set[VertId]] = dict()
    extVertices = pVertices - cVertices
    for v in oppVertices:
        reachableExtVerts = extVertices & pOutEdges[v]
        if len(reachableExtVerts) != 0:
            rule1breaks[v] = reachableExtVerts
    
    
    # check rule 2 breaks
    rule2breaks: set[VertId] = set()
    ownedVertices = {v for v in cVertices if v in pOwned}
    for v in ownedVertices:
        if len(pOutEdges[v] & cVertices) == 0:
            rule2breaks.add(v)
            
    return (rule1breaks, rule2breaks)

def find_problems_on_specified_verts(parent: Game, cVertices: set[VertId], relevantVertices : set[VertId]) -> tuple[dict[VertId, set[VertId]], set[VertId]]:
    (pVertices, pInit, pPriority, pOwned, pOutEdges, pIncEdges) = parent
    
    # check that there are no opponent vertices with externally outgoing edges
    # only consider vertices that are _not_ owned
    oppVertices = {v for v in cVertices if v not in pOwned and v in relevantVertices}
    
    rule1breaks: dict[VertId, set[VertId]] = dict()
    extVertices = pVertices - cVertices
    for v in oppVertices:
        reachableExtVerts = extVertices & pOutEdges[v]
        if len(reachableExtVerts) != 0:
            rule1breaks[v] = reachableExtVerts
    
    
    # check rule 2 breaks
    rule2breaks: set[VertId] = set()
    ownedVertices = {v for v in cVertices if v in pOwned and v in relevantVertices}
    for v in ownedVertices:
        if len(pOutEdges[v] & cVertices) == 0:
            rule2breaks.add(v)
            
    return (rule1breaks, rule2breaks)

"""
Builds a new game object from a parent game and a list of vertices that should be included in the subgame
DOES NOT CHECK IF THE REQUESTED SUBGAME IS VALID
"""
def realise_subgame(game: Game, cVertices: set[VertId]) -> Game:
    (pVertices, pInit, pPriority, pOwned, pOutEdges, pIncEdges) = game
    cPriority = {id:p for (id,p) in pPriority.items() if id in cVertices}
    cOwned = pOwned & cVertices
    cOutEdges = {id:(dests & cVertices) for (id,dests) in pOutEdges.items() if id in cVertices}
    cIncEdges = {id:(origs & cVertices) for (id,origs) in pIncEdges.items() if id in cVertices}
    
    return (cVertices, pInit, cPriority, cOwned, cOutEdges, cIncEdges)


def flatten_game(game: Game) -> Game:
    (oldVertices, oldInit, oldPriority, oldOwned, oldOutEdges, oldIncEdges) = game
    
    # map old to new vertices (special case if initial vertex is 0)
    i = 0
    mapping : dict[VertId, VertId] = dict()
    if oldInit == VertId(0):
        mapping[VertId(0)] = VertId(0)
        i = 1
        for oldv in oldVertices:
            if oldv != VertId(0):
                mapping[oldv] = VertId(i)
                i += 1
    else:
        for oldv in oldVertices:
            mapping[oldv] = VertId(i)
            i += 1

    newVertices : set[VertId] = set(mapping.values())
    
    newInit = mapping[oldInit]
    
    newPriority : dict[VertId, Priority] = {mapping[id]:p for (id,p) in oldPriority.items()}
    
    newOwned : set[VertId] = {mapping[id] for id in oldOwned}
    
    newOutEdges : dict[VertId, set[VertId]] = {mapping[id]:({mapping[dest] for dest in dests}) for (id,dests) in oldOutEdges.items()}
    
    newIncEdges : dict[VertId, set[VertId]] = {mapping[id]:({mapping[orig] for orig in origs}) for (id,origs) in oldIncEdges.items()}
    
    return (newVertices, newInit, newPriority, newOwned, newOutEdges, newIncEdges)


def export_to_file(game: Game, filename: str) -> None:
    #print("exported to: " + filename)
    (vertices, init, priority, owned, outEdges, incEdges) = game
    file = open(filename, "w")
    file.write("parity " + str(len(vertices)) + ";\n")
    #print(game)
    for v in vertices:
        priorityStr = str(priority[v])
        ownedStr = "0" if (v in owned) else "1"
        edgesStr = ",".join(map(str, outEdges[v]))
        initString: str = (" \"initial\"" if v == init else "")
        file.write(str(v) + " " + priorityStr + " " + ownedStr + " " + edgesStr + ";\n")
    
def parse_solution(filename: str) -> dict[VertId, VertId]:
    file = open(filename, 'r')
    num_vertices = int(file.readline().strip("\n\r; paritysol"))
    solution: dict[VertId, VertId] = dict()
    for i in range(num_vertices):
        splitline = file.readline().strip("\n\r;").split()
        if (len(splitline) == 3):
            solution[VertId(int(splitline[0]))] = VertId(int(splitline[2]))
    
    return solution

def solution_size(game: Game, solution: dict[VertId, VertId]) -> int:
    return len(solution_domain(game, solution))

def solution_domain(game: Game, solution: dict[VertId, VertId]) -> set[VertId]:
    (vertices, init, priority, owned, outEdges, incEdges) = game
    dominion: set[VertId] = {init}
    prevdominion = set()
    while len(dominion) > len(prevdominion):
        newlyadded = dominion - prevdominion
        prevdominion = dominion
        for v in newlyadded:
            if v in solution:
                dominion.add(solution[v])
            else:
                dominion |= outEdges[v]
    
    return dominion
