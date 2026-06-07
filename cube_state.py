from copy import copy

from misc import *



class CubeRestriction:
    """Specify which pieces should move and where, as well as which ones to keep in place and which do not matter."""
    def __init__(self, 
            # Starts as a solved cube
            locked_edges=[], 
            locked_corners=[], 
            edge_id=[], 
            edge_destination=[], 
            edge_orientation=[], 
            corner_id=[], 
            corner_destination=[], 
            corner_orientation=[]
        ):
        self.target_edges = bytearray([255] * 12)
        self.target_corners = bytearray([255] * 8)

        for id in locked_edges:
            self.target_edges[id] = id
        for id in locked_corners:
            self.target_corners[id] = id
        for id, dest, oriented in zip(edge_id, edge_destination, edge_orientation):
            self.target_edges[dest] = oriented << 4 | id 
        for id, dest, orientation in zip(corner_id, corner_destination, corner_orientation):
            self.target_corners[dest] = orientation << 3 | id 
        
        

        # self.locked_edges = bytearray()
        # self.locked_corners = bytearray()


class CubeState:
    """Cube object that holds a position and is able to turn"""
    # Format: (0bOEEEE) x12 where O=orientation and EEEE=edge num
    # Represents that edge #0 is in position 0 (with orientation 0), #1 in 1 (0), etc.
    SOLVED_EDGE_STATE = bytearray([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ])
    # Format: (0bOOCCC) x8 where OO=orientation and CCC=corner num
    # Represents that corner #0 is in position 0 (with orientation 00), #1 in 1 (00), etc.
    SOLVED_CORNER_STATE = bytearray([ 0, 1, 2, 3, 4, 5, 6, 7 ])

    def __init__(self, edge_state=None, corner_state=None):
        """CubeState contructor - leave empty for solved position"""
        if edge_state:
            if not isinstance(edge_state, bytearray): raise TypeError("edge_state must be a bytearray")
            self.edge_state = edge_state
        else:
            self.edge_state = copy(self.SOLVED_EDGE_STATE)

        if corner_state:
            if not isinstance(corner_state, bytearray): raise TypeError("corner_state must be a bytearray")
            self.corner_state = corner_state
        else:
            self.corner_state = copy(self.SOLVED_CORNER_STATE)

    def __str__(self):
        return generate_net(self)
    


    def is_solved(self):
        """Get whether the CubeState is in a solved position"""
        return (self.edge_state == self.SOLVED_EDGE_STATE) and (self.corner_state == self.SOLVED_CORNER_STATE)
    
    def matches_state(self, state):
        return (self.edge_state == state.edge_state) and (self.corner_state == state.corner_state)
    
    def matches_restriction(self, restriction: CubeRestriction):
        # Self format:
        # edges/corners: [idx 0: edgeid]
        # Restriction format
        # target edges/corners: [idx 0: None | int]
        # None means it shouldn't care about it. It may or may not be messed up
        # id == idx means that it should be unaffected
        # id != idx means that id should move to idx

        for idx, restricted_edge in enumerate(restriction.target_edges):
            self_edge = self.edge_state[idx]
            if restricted_edge != 255: # If it is None, we don't care about it
                if self_edge != restricted_edge:
                    return False # We wanted this to be equal
                
        for idx, restricted_corner in enumerate(restriction.target_corners):
            self_corner = self.corner_state[idx]
            if restricted_corner != 255: # If it is None, we don't care about it
                if self_corner != restricted_corner:
                    return False # We wanted this to be equal
        
        return True
        


        # return (self.edge_state == state.edge_state) and (self.corner_state == state.corner_state)
    
    def reset_cube(self):
        """Set the CubeState to a solved position"""
        self.edge_state = self.SOLVED_EDGE_STATE
        self.corner_state = self.SOLVED_CORNER_STATE
    
    def set_edge(self, id, value):
        """Update a single edge on the CubeState"""
        self.edge_state[id] = value
        
    def set_corner(self, id, value):
        """Update a single corner on the CubeState"""
        self.corner_state[id] = value
    
    def copy(self):
        return CubeState(self.edge_state, self.corner_state)

    def make_move(self, move):
        """Update a single corner on the CubeState"""
        # To permute:
        # 1. Create temporary empty states
        # 2. Loop over piece in the original state
        # 3. Set each edge
        # 
        # To orient
        # 1. Take the current state and apply the permutations according to move_map
        # 2. If edge and is one of [12, 13, 15, 16], then flip orientation (front and back quarter turns)
        # 3. If corner, then U/D: (0 -> 0), (1 -> 2), (2 -> 1) L/R: (0 -> 1), (1 -> 0), (2 -> 2) F/B: (0 -> 2), (1 -> 1), (2 -> 0) but half turns don't affect orientation

        new_edge_state = bytearray([0] * 12)
        new_corner_state = bytearray([0] * 8)

        # Edge orientation depends only on if move is a F, F', B, or B'
        is_edge_flipping = move in [12, 13, 15, 16]
        # Corner orientation is more complex
        # orientation 0: White/Yellow faces U/D
        # orientation 1: White/Yellow faces F/R
        # orientation 2: White/Yellow faces L/R
        if move in [6, 7, 9, 10]: # U, U', D, D'
            corner_flip_map = (0, 2, 1) # 0->0, 1->2, 2->1
        elif move in [0, 1, 3, 4]: # L, L', R, R'
            corner_flip_map = (1, 0, 2) # 0->1, 1->0, 2->2
        elif move in [12, 13, 15, 16]: # F, F', B, B'
            corner_flip_map = (2, 1, 0) # 0->2, 1->1, 2->0
        else: # Half turns don't change orientation 
            corner_flip_map = (0, 1, 2) # 0->0, 1->1, 2->2
        
        # Permute and orient edges
        for from_idx, edge in enumerate(self.edge_state):
            to_idx = MOVE_MAP[move]["edge"][from_idx]

            # Mask out just the edge ID
            original_edge_id = edge & 0b01111
            # Shift over the orientation
            original_orientation = edge >> 4

            is_affected = from_idx != to_idx
            if is_affected and is_edge_flipping:
                new_orientation = not original_orientation
            else:
                new_orientation = original_orientation

            # Concat the orientation and edge ID
            new_value = new_orientation << 4 | original_edge_id
            
            # Update the new state with the edge that goes there
            new_edge_state[to_idx] = new_value
        
        # Permute and orient corners
        for from_idx, corner in enumerate(self.corner_state):
            to_idx = MOVE_MAP[move]["corner"][from_idx]
            
            # Mask out just the corner ID
            original_corner_id = corner & 0b00111
            # Shift over the orientation
            original_orientation = corner >> 3

            is_affected = from_idx != to_idx
            if is_affected:
                new_orientation = corner_flip_map[original_orientation]
            else:
                new_orientation = original_orientation

            # Concat the orientation and corner ID
            new_value = new_orientation << 3 | original_corner_id
            
            # Update the new state with the corner that goes there
            new_corner_state[to_idx] = new_value
        
        self.edge_state = new_edge_state
        self.corner_state = new_corner_state
    
    def make_moves(self, moves):
        MOVE_NAMES = ("L", "L'", "L2", "R", "R'", "R2", "D", "D'", "D2",
                      "U", "U'", "U2", "F", "F'", "F2", "B", "B'", "B2")
        
        for move in moves:
            if isinstance(move, int):
                self.make_move(move)
            elif isinstance(move, str):
                if move in MOVE_NAMES:
                    self.make_move(MOVE_NAMES.index(move.upper()))
            else:
                raise TypeError("Moves must contain only ints or valid move strings")




if __name__ == "__main__":
    cube = CubeState()

    # for move, name in zip(range(18), ("L", "L'", "L2", "R", "R'", "R2", "D", "D'", "D2", "U", "U'", "U2", "F", "F'", "F2", "B", "B'", "B2")):
    # for move, name in zip(range(6, 12), ("D", "D'", "D2", "U", "U'", "U2")):
    #     cube.reset_cube()

    #     print(f"\n\nPerforming {name} ({move})")
    #     cube.make_move(move)
    #     print(cube)
    #     for i, corner in enumerate(cube.corner_state):
    #         print(f"Corner {corner&0b00111} at {i}: {corner>>3}", end=" | ")
    #         pass
        # print([i for i in cube.SOLVED_CORNER_STATE])


    print("\n\nPerforming R U R' U'")
    cube.make_move(3)
    cube.make_move(9)
    cube.make_move(4)
    cube.make_move(10)
    print(cube)