# Move map represents:
# By doing move m:
#  edge  i goes to  edge  MOVE_MAP[m]["edge"][i]
# corner i goes to corner MOVE_MAP[m]["corner"][i]
MOVE_MAP = (
    # L, L', L2
    { "edge": [0, 4, 2, 3, 9, 1, 6, 7, 8, 5, 10, 11], "corner": [4, 0, 2, 3, 5, 1, 6, 7] },
    { "edge": [0, 5, 2, 3, 1, 9, 6, 7, 8, 4, 10, 11], "corner": [1, 5, 2, 3, 0, 4, 6, 7] },
    { "edge": [0, 9, 2, 3, 5, 4, 6, 7, 8, 1, 10, 11], "corner": [5, 4, 2, 3, 1, 0, 6, 7] },
    # R, R', R2
    { "edge": [0, 1, 2, 6, 4, 5, 11, 3, 8, 9, 10, 7], "corner": [0, 1, 6, 2, 4, 5, 7, 3] },
    { "edge": [0, 1, 2, 7, 4, 5, 3, 11, 8, 9, 10, 6], "corner": [0, 1, 3, 7, 4, 5, 2, 6] },
    { "edge": [0, 1, 2, 11, 4, 5, 7, 6, 8, 9, 10, 3], "corner": [0, 1, 7, 6, 4, 5, 3, 2] },
    # D, D', D2
    { "edge": [0, 1, 2, 3, 4, 5, 6, 7, 11, 8, 9, 10], "corner": [0, 1, 2, 3, 7, 4, 5, 6] },
    { "edge": [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8], "corner": [0, 1, 2, 3, 5, 6, 7, 4] },
    { "edge": [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 8, 9], "corner": [0, 1, 2, 3, 6, 7, 4, 5] },
    # U, U', U2
    { "edge": [1, 2, 3, 0, 4, 5, 6, 7, 8, 9, 10, 11], "corner": [1, 2, 3, 0, 4, 5, 6, 7] },
    { "edge": [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11], "corner": [3, 0, 1, 2, 4, 5, 6, 7] },
    { "edge": [2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11], "corner": [2, 3, 0, 1, 4, 5, 6, 7] },
    # F, F', F2
    { "edge": [7, 1, 2, 3, 0, 5, 6, 8, 4, 9, 10, 11], "corner": [3, 1, 2, 7, 0, 5, 6, 4] },
    { "edge": [4, 1, 2, 3, 8, 5, 6, 0, 7, 9, 10, 11], "corner": [4, 1, 2, 0, 7, 5, 6, 3] },
    { "edge": [8, 1, 2, 3, 7, 5, 6, 4, 0, 9, 10, 11], "corner": [7, 1, 2, 4, 3, 5, 6, 0] },
    # B, B', B2
    { "edge": [0, 1, 5, 3, 4, 10, 2, 7, 8, 9, 6, 11], "corner": [0, 5, 1, 3, 4, 6, 2, 7] },
    { "edge": [0, 1, 6, 3, 4, 2, 10, 7, 8, 9, 5, 11], "corner": [0, 2, 6, 3, 4, 1, 5, 7] },
    { "edge": [0, 1, 10, 3, 4, 6, 5, 7, 8, 9, 2, 11], "corner": [0, 6, 5, 3, 4, 2, 1, 7] },
)

def identify_corner_twist(move):
    # Corner twist by source position
    corner_twist = [0] * 8

    if move == 0:      # L
        corner_twist[0] = 1
        corner_twist[1] = 2
        corner_twist[4] = 2
        corner_twist[5] = 1
    elif move == 1:    # L'
        corner_twist[0] = 2
        corner_twist[1] = 1
        corner_twist[4] = 1
        corner_twist[5] = 2
    elif move == 3:    # R
        corner_twist[2] = 1
        corner_twist[3] = 2
        corner_twist[6] = 2
        corner_twist[7] = 1
    elif move == 4:    # R'
        corner_twist[2] = 2
        corner_twist[3] = 1
        corner_twist[6] = 1
        corner_twist[7] = 2
    elif move == 12:   # F
        corner_twist[0] = 2
        corner_twist[3] = 1
        corner_twist[4] = 1
        corner_twist[7] = 2
    elif move == 13:   # F'
        corner_twist[0] = 1
        corner_twist[3] = 2
        corner_twist[4] = 2
        corner_twist[7] = 1
    elif move == 15:   # B
        corner_twist[1] = 1
        corner_twist[2] = 2
        corner_twist[5] = 2
        corner_twist[6] = 1
    elif move == 16:   # B'
        corner_twist[1] = 2
        corner_twist[2] = 1
        corner_twist[5] = 1
        corner_twist[6] = 2

    return corner_twist


def generate_net(cube):
    # ----------------- START AI GENERATED -----------------
    C = {
        "U": "⬜",  # white
        "D": "🟨",  # yellow
        "F": "🟩",  # green
        "B": "🟦",  # blue
        "L": "🟧",  # orange
        "R": "🟥",  # red
    }

    # Face arrays: U, L, F, R, B, D
    faces = {
        "U": [[" " for _ in range(3)] for _ in range(3)],
        "L": [[" " for _ in range(3)] for _ in range(3)],
        "F": [[" " for _ in range(3)] for _ in range(3)],
        "R": [[" " for _ in range(3)] for _ in range(3)],
        "B": [[" " for _ in range(3)] for _ in range(3)],
        "D": [[" " for _ in range(3)] for _ in range(3)],
    }

    # Centers
    faces["U"][1][1] = C["U"]
    faces["D"][1][1] = C["D"]
    faces["F"][1][1] = C["F"]
    faces["B"][1][1] = C["B"]
    faces["L"][1][1] = C["L"]
    faces["R"][1][1] = C["R"]

    # Edge position -> its two face locations
    edge_pos = {
        0: (("U", 2, 1), ("F", 0, 1)),  # UF
        1: (("U", 1, 0), ("L", 0, 1)),  # UL
        2: (("U", 0, 1), ("B", 0, 1)),  # UB
        3: (("U", 1, 2), ("R", 0, 1)),  # UR

        4: (("F", 1, 0), ("L", 1, 2)),  # FL
        5: (("B", 1, 2), ("L", 1, 0)),  # BL
        6: (("B", 1, 0), ("R", 1, 2)),  # BR
        7: (("F", 1, 2), ("R", 1, 0)),  # FR

        8: (("D", 0, 1), ("F", 2, 1)),  # DF
        9: (("D", 1, 0), ("L", 2, 1)),  # DL
        10: (("D", 2, 1), ("B", 2, 1)), # DB
        11: (("D", 1, 2), ("R", 2, 1)), # DR
    }

    # Edge id -> solved colors in the same order as edge_pos
    edge_colors = {
        0: (C["U"], C["F"]),
        1: (C["U"], C["L"]),
        2: (C["U"], C["B"]),
        3: (C["U"], C["R"]),

        4: (C["F"], C["L"]),
        5: (C["B"], C["L"]),
        6: (C["B"], C["R"]),
        7: (C["F"], C["R"]),

        8: (C["D"], C["F"]),
        9: (C["D"], C["L"]),
        10: (C["D"], C["B"]),
        11: (C["D"], C["R"]),
    }

    # Corner position -> its three face locations.
    # Order is always: U/D axis, F/B axis, L/R axis
    corner_pos = {
        0: (("U", 2, 0), ("F", 0, 0), ("L", 0, 2)),  # UFL
        1: (("U", 0, 0), ("B", 0, 2), ("L", 0, 0)),  # ULB
        2: (("U", 0, 2), ("B", 0, 0), ("R", 0, 2)),  # UBR
        3: (("U", 2, 2), ("F", 0, 2), ("R", 0, 0)),  # URF

        4: (("D", 0, 0), ("F", 2, 0), ("L", 2, 2)),  # DFL
        5: (("D", 2, 0), ("B", 2, 2), ("L", 2, 0)),  # DLB
        6: (("D", 2, 2), ("B", 2, 0), ("R", 2, 2)),  # DBR
        7: (("D", 0, 2), ("F", 2, 2), ("R", 2, 0)),  # DRF
    }

    # Corner id -> solved colors.
    # Same order: U/D color, F/B color, L/R color
    corner_colors = {
        0: (C["U"], C["F"], C["L"]),  # UFL
        1: (C["U"], C["B"], C["L"]),  # ULB
        2: (C["U"], C["B"], C["R"]),  # UBR
        3: (C["U"], C["F"], C["R"]),  # URF

        4: (C["D"], C["F"], C["L"]),  # DFL
        5: (C["D"], C["B"], C["L"]),  # DLB
        6: (C["D"], C["B"], C["R"]),  # DBR
        7: (C["D"], C["F"], C["R"]),  # DRF
    }

    # Place edges
    for pos, edge in enumerate(cube.edge_state):
        edge_id = edge & 0b01111
        orientation = edge >> 4

        colors = edge_colors[edge_id]
        if orientation:
            colors = (colors[1], colors[0])

        for sticker, color in zip(edge_pos[pos], colors):
            face, row, col = sticker
            faces[face][row][col] = color

    # Axis order:
    # 0 = U/D axis, sign + = U, sign - = D
    # 1 = F/B axis, sign + = F, sign - = B
    # 2 = L/R axis, sign + = R, sign - = L
    corner_signs = {
        0: (+1, +1, -1),  # UFL
        1: (+1, -1, -1),  # ULB
        2: (+1, -1, +1),  # UBR
        3: (+1, +1, +1),  # URF

        4: (-1, +1, -1),  # DFL
        5: (-1, -1, -1),  # DLB
        6: (-1, -1, +1),  # DBR
        7: (-1, +1, +1),  # DRF
    }

    axis_perms = (
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0),
    )

    def parity(perm):
        inversions = 0
        for i in range(3):
            for j in range(i + 1, 3):
                if perm[i] > perm[j]:
                    inversions += 1
        return -1 if inversions % 2 else +1

    def corner_perm_for(corner_id, pos, orientation):
        home = corner_signs[corner_id]
        dest = corner_signs[pos]

        for axis_perm in axis_perms:
            # orientation says where the cubie's U/D sticker axis currently is
            if axis_perm[0] != orientation:
                continue

            sign_product = 1
            for local_axis, world_axis in enumerate(axis_perm):
                sign_product *= dest[world_axis] * home[local_axis]

            # Only proper cube rotations are allowed.
            if parity(axis_perm) * sign_product == +1:
                slot_to_color = [None, None, None]
                for local_axis, world_axis in enumerate(axis_perm):
                    slot_to_color[world_axis] = local_axis
                return tuple(slot_to_color)

        raise ValueError(
            f"Invalid corner orientation: corner={corner_id}, pos={pos}, orientation={orientation}"
        )

    # Place corners
    for pos, corner in enumerate(cube.corner_state):
        corner_id = corner & 0b00111
        orientation = corner >> 3

        colors = corner_colors[corner_id]
        perm = corner_perm_for(corner_id, pos, orientation)

        for sticker, color_index in zip(corner_pos[pos], perm):
            face, row, col = sticker
            faces[face][row][col] = colors[color_index]

    def row(face, r):
        return "".join(faces[face][r])

    lines = []

    # T-shaped / unfolded net:
    #
    #         U
    #   L  F  R  B
    #         D

    for r in range(3):
        lines.append("        " + row("U", r))
    lines.append("")

    for r in range(3):
        lines.append(
            row("L", r) + "  " +
            row("F", r) + "  " +
            row("R", r) + "  " +
            row("B", r)
        )

    lines.append("")
    for r in range(3):
        lines.append("        " + row("D", r))

    return "\n".join(lines)
    
    # ----------------- END AI GENERATED -----------------