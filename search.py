from cube_state import CubeState, CubeRestriction
from collections import deque
import time
import multiprocessing

MOVE_NAMES = ("L", "L'", "L2", "R", "R'", "R2", "D", "D'", "D2",
              "U", "U'", "U2", "F", "F'", "F2", "B", "B'", "B2")

FACE_OF = [i // 3 for i in range(18)]
OPPOSITE_FACE = {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4}

INVERSE_MOVE = (
    1, 0, 2,
    4, 3, 5,
    7, 6, 8,
    10, 9, 11,
    13, 12, 14,
    16, 15, 17
)

def flatten(obj):
    if isinstance(obj[0], list):
        return [item for sublist in list for item in sublist]
    elif isinstance(obj[0], dict):
        return {k: v for d in obj for k, v in d.items()}
    else:
        raise TypeError("Unsuported type")


def state_key(cube_state):
    return (tuple(cube_state.edge_state), tuple(cube_state.corner_state))

def invert_path(path):
    return [INVERSE_MOVE[m] for m in reversed(path)]

def init_searcher(args):
    start_state, max_depth, move = args

    # Assign a new Searcher
    searcher = StateSearcher()
    # Start the search with a first move of x
    visited_states = searcher.start_search(start_state, max_depth, move)
    
    # Return the list of visited nodes
    return visited_states

def print_solution(path):
    for move in path:
        print(MOVE_NAMES[move], end=" ")
    print()



class StateSearcher:
    def __init__(self):
        pass

    def start_search(self, start_state: CubeState, depth=4, first_move=None, allowed_moves=range(18)):
        start_state = start_state.copy()

        path = []
        if first_move is not None:
            start_state.make_move(first_move)
            path = [first_move]

        self.visited_states = self.search(start_state, depth - 1, path=path, allowed_moves=allowed_moves)

        return self.visited_states

    def search(self, start_state, max_depth, path, allowed_moves=range(18)):
        """BFS up to max_depth. Keeps the shortest path for each state."""
        # Create a cache of (state_key: path)
        seen = {state_key(start_state): []}
        q = deque([(start_state, path, 0)])

        while q:
            cube, path, depth = q.popleft()
            if depth == max_depth:
                continue # End branch if past max_depth
            
            # Get the last move and face for pruning
            last = path[-1] if path else None
            last_face = FACE_OF[last] if last is not None else None

            # Branch off of each allowed move
            for move in allowed_moves:
                move_face = FACE_OF[move]

                if last is not None:
                    # But skip repeat faces
                    if move_face == last_face:
                        continue
                    # And only move opposite faces once (the other can be pruned)
                    if OPPOSITE_FACE[move_face] == last_face and move > last:
                        continue
                
                # Start child branches one move further
                child = cube.copy()
                child.make_move(move)

                # Skip already visited nodes
                key = state_key(child)
                if key in seen:
                    continue
                
                # Update path and cache
                new_path = path + [move]
                seen[key] = new_path

                # Add child branch to queue
                q.append((child, new_path, depth + 1))

        return seen


class ParallelSearcher:
    """Runs multiple parallel searches starting from different moves."""
    def __init__(self):
        pass

    def start_parallel_search(self, start_state, max_depth=4):
        work = [
            (start_state, max_depth, move)
            for move in range(18)
        ]


        # Run this with 18 proccesses at once, each with a unique first move
        with multiprocessing.Pool() as pool:
            results = pool.map(init_searcher, work)
        
        return results


class MITMSearcher:
    def __init__(self):
        pass

    def run_search(self, start_state, target_state, max_depth=5):
        searcher = ParallelSearcher()
        
        forward_results = searcher.start_parallel_search(start_state, max_depth) # Parallel search forwards
        forward_states = flatten(forward_results)
        backward_results = searcher.start_parallel_search(target_state, max_depth) # Parallel search backwards
        backward_states = flatten(backward_results)

        solutions = []

        # Loop over every state explored forwards
        for key, f_path in forward_states.items():
            b_path = backward_states.get(key)
            # If state also exists in backward visited states
            if b_path is not None:
                # Then this is a solution
                solutions.append(f_path + invert_path(b_path))
        
        return solutions


class RestrictedSearcher:
    def __init__(self):
        pass

    def run_search(self, start_state: CubeState, target_restriction: CubeRestriction=CubeRestriction(), max_depth=4):
        searcher = ParallelSearcher()

        results = searcher.start_parallel_search(start_state, max_depth) # Parallel search forwards
        states_visited = flatten(results)
        
        solutions = []
        # Loop over every state explored
        for key, path in states_visited.items():
            state = CubeState(bytearray(key[0]), bytearray(key[1]))
            # If state matches the restrictions, then it is a solution
            if state.matches_restriction(target_restriction):
                solutions.append(path)
        
        return solutions

if __name__ == "__main__":
    # Opposite edges
    target1 = CubeRestriction(
        locked_edges=[1, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        locked_corners=[0, 1, 2, 3, 4, 5, 6, 7],
        edge_id=[0, 2],
        edge_destination=[2, 0],
        edge_orientation=[0, 0]
    )
    # R U R' U' strict
    target2 = CubeRestriction(
        locked_edges=[0, 1, 4, 5, 6, 8, 9, 10, 11],
        locked_corners=[0, 4, 5, 6],
        edge_id=[3, 7, 2],
        edge_destination=[2, 3, 7],
        edge_orientation=[0, 0],
        corner_id=[],
        corner_destination=[],
        corner_orientation=[]
    )
    # Take out pair (R U R' U' relaxed)
    target3 = CubeRestriction(
        locked_edges=[4, 5, 6, 8, 9, 10, 11],
        locked_corners=[4, 5, 6],
        edge_id=[7],
        edge_destination=[3],
        edge_orientation=[0],
        corner_id=[7],
        corner_destination=[3],
        corner_orientation=[1]
    )

    solved_cube = CubeState()

    print("-"*5, "MITM Search", "-"*5)

    # Scramble cube
    scramble = "F R U' B' D' R' L F' B U'"
    scrambled_cube = CubeState()
    scrambled_cube.make_moves(scramble.split())
    print(scrambled_cube)
    print(f"Scrambled cube with: {scramble}\n")
    
    # Create MITM searcher
    mitm_searcher = MITMSearcher()
    max_depth = 5
    
    print(f"Searching with MITM up to depth {max_depth}")
    start = time.perf_counter()
    # solutions = mitm_searcher.run_search(scrambled_cube, solved_cube, max_depth=max_depth)
    solutions = []
    end = time.perf_counter()

    # MITM Results
    print(f"Executed in {end - start:0.4f} seconds")
    print(f"Solutions found: {len(solutions)}")
    print(f"Shortest solution: {min([len(x) for x in solutions], default=0)} moves")
    print(f"Average length: {round(sum([len(x) for x in solutions])/len(solutions) if solutions else 0, 2)} moves")
    solutions.sort(key=len)
    for sol in solutions[:3]: 
        print_solution(sol)
        if len(solutions) > 3:
            print("...")

    print
    print("-"*5, "Restricted Search", "-"*5)

    restricted_searcher = RestrictedSearcher()
    max_depth = 6
    
    print(f"Searching with restriction 3 up to depth {max_depth}")
    start = time.perf_counter()
    solutions = restricted_searcher.run_search(scrambled_cube, target3, max_depth=max_depth)
    end = time.perf_counter()

    # Restricted Search Results
    print(f"Executed in {end - start:0.4f} seconds")
    print(f"Solutions found: {len(solutions)}")
    print(f"Shortest solution: {min([len(x) for x in solutions], default=0)} moves")
    print(f"Average length: {round(sum([len(x) for x in solutions])/len(solutions) if solutions else 0, 2)} moves")
    solutions.sort(key=len)
    for sol in solutions[:3]: 
        print_solution(sol)
        if len(solutions) > 3:
            print("...")