import math

#base heuristic should implement the Manhattan distance - maximum distance out of all the shortest distances of each empty cell to the closest cube
def base_heuristic(_flat_board_state):
    global_dists = []
    board = _flat_board_state.board
    rows, cols = _flat_board_state.rows, _flat_board_state.cols

    #finding all the cubes and holes on the board
    cubes = [
        (i // cols, i % cols)
        for i, cell in enumerate(board)
        if cell == 3
    ]
    holes = [
        (i // cols, i % cols)
        for i, cell in enumerate(board)
        if cell == 0
    ]

    for row, col in holes:
        local_dists = []
        for r, c in cubes:
            dist = abs(r - row) + abs(c - col)
            local_dists.append(dist)
        global_dists.append(min(local_dists))

    #0 if no holes
    return max(global_dists, default=0)

def advanced_heuristic(_flat_board_state):
    return 0

