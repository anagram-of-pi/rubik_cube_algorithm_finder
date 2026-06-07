from cube_state import CubeState
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
    start_state, target_state, max_depth, move = args

    # Assign a new Searcher
    searcher = Searcher(start_state, target_state, max_depth)
    # Start the search with a first move of x
    visited_states = searcher.start_search(max_depth, move)
    
    # Return the list of visited nodes
    return visited_states

def print_solution(path):
    for move in path:
        print(MOVE_NAMES[move], end=" ")
    print()



class Searcher:
    def __init__(self, start_state: CubeState, target_state: CubeState=CubeState(), depth=4):
        self.start_state = start_state
        self.target_state = target_state
        self.node_count = 0
        self.solutions = []
    
    def start_search(self, depth, first_move=0):
        self.node_count = 0
        allowed_moves = range(18)
        self.solutions = []

        start_state = self.start_state.copy()
        start_state.make_move(first_move)
        self.visited_states = self.search(start_state, depth - 1, path=[first_move], allowed_moves=allowed_moves)

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

                self.node_count += 1

                # Add child branch to queue
                q.append((child, new_path, depth + 1))

        return seen


class ParallelSearch:
    """Runs a parallel meet-in-the-middle search starting from different moves."""
    def __init__(self, start_state: CubeState, target_state: CubeState, max_depth):
        self.start_state = start_state
        self.target_state = target_state
        self.max_depth = max_depth
        # self.start_parallel_search()

    def start_parallel_search(self):
        work = [
            (self.start_state, self.target_state, self.max_depth, move)
            for move in range(18)
        ]


        # Run this with 18 proccesses at once, each with a unique first move
        with multiprocessing.Pool() as pool:
            results = pool.map(init_searcher, work)
        
        return results


if __name__ == "__main__":
    solved_cube = CubeState()

    scrambled_cube = CubeState()
    scrambled_cube.make_moves("F R U' B' D' R' L F' B U' B".split())

    depth = 6

    forward_search = ParallelSearch(scrambled_cube, solved_cube, depth)
    backward_search = ParallelSearch(solved_cube, scrambled_cube, depth)

    start = time.perf_counter()
    forward_results = forward_search.start_parallel_search() # Parallel search forwards
    forward_states = flatten(forward_results)
    backward_results = backward_search.start_parallel_search() # Parallel search backwards
    backward_states = flatten(backward_results)
    end = time.perf_counter()

    # solved_key = state_key(solved_cube)
    # solutions = []

    solutions = []
    # Loop over every state explored forwards
    for key, f_path in forward_states.items():
        b_path = backward_states.get(key)
        # If state also exists in backward visited states
        if b_path is not None:
            # Then this is a solution
            solutions.append(f_path + invert_path(b_path))


    # for searcher_result in forward_results:
    #     path = searcher_result.get(solved_key)
    #     if path is not None:
    #         solutions.append(path)

    print(f"Executed in {end - start:0.4f} seconds")
    print(f"Solutions found: {len(solutions)}")
    print(f"Shortest solution: {min([len(x) for x in solutions])}")
    print(f"Average length: {round(sum([len(x) for x in solutions])/len(solutions), 2)}")

    for sol in solutions:
        print_solution(sol)
