import math
from collections import deque
from functools import lru_cache
from math import inf

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

@lru_cache(maxsize=1024)
def _distances_from_hole(rows, cols, walls, hole):
    """Return the shortest distance from the hole to every non-wall cell."""
    distances = [inf] * (rows * cols)
    distances[hole] = 0
    queue = deque([hole])

    while queue:
        cell = queue.popleft()
        row, col = divmod(cell, cols)
        next_distance = distances[cell] + 1

        for nr, nc in (
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ):
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor = nr * cols + nc

                if neighbor not in walls and distances[neighbor] == inf:
                    distances[neighbor] = next_distance
                    queue.append(neighbor)

    return tuple(distances)


def _has_perfect_matching(distance_matrix, limit):
    """Check whether every hole can get a distinct cube within limit."""
    candidates = [
        [
            cube_index
            for cube_index, distance in enumerate(distances)
            if distance <= limit
        ]
        for distances in distance_matrix
    ]

    # matched_hole[cube_index] is the hole currently assigned to that cube.
    matched_hole = [-1] * len(distance_matrix)

    def assign(hole_index, seen_cubes):
        for cube_index in candidates[hole_index]:
            if cube_index in seen_cubes:
                continue

            seen_cubes.add(cube_index)
            previous_hole = matched_hole[cube_index]

            if previous_hole == -1 or assign(previous_hole, seen_cubes):
                matched_hole[cube_index] = hole_index
                return True

        return False

    # Start with the holes that have the fewest candidate cubes.
    hole_order = sorted(
        range(len(candidates)),
        key=lambda hole_index: len(candidates[hole_index]),
    )

    return all(assign(hole_index, set()) for hole_index in hole_order)


def advanced_heuristic(_flat_board_state):
    board = _flat_board_state.board
    rows, cols = _flat_board_state.rows, _flat_board_state.cols

    holes = []
    cubes = []
    walls = set()

    for index, cell in enumerate(board):
        if cell == 0:
            holes.append(index)
        elif cell == 3:
            cubes.append(index)
        elif cell == 2:
            walls.add(index)

    if not holes:
        return 0

    if len(holes) != len(cubes):
        return inf

    walls = frozenset(walls)
    cube_positions = [divmod(cube, cols) for cube in cubes]
    distance_matrix = []

    # Lower bounds on the number of commands in each direction.
    up = down = left = right = 0
    nearest_hole_for_cube = [inf] * len(cubes)
    nearest_cube_bound = 0

    for hole in holes:
        hole_row, hole_col = divmod(hole, cols)
        distance_map = _distances_from_hole(rows, cols, walls, hole)
        distances = [distance_map[cube] for cube in cubes]
        distance_matrix.append(distances)

        closest_cube = min(distances)
        if closest_cube == inf:
            return inf
        nearest_cube_bound = max(nearest_cube_bound, closest_cube)

        # Use only cubes that can reach this hole around the walls.
        min_row = min_col = inf
        max_row = max_col = -inf

        for cube_index, (cube_row, cube_col) in enumerate(cube_positions):
            distance = distances[cube_index]
            if distance == inf:
                continue

            if distance < nearest_hole_for_cube[cube_index]:
                nearest_hole_for_cube[cube_index] = distance

            min_row = min(min_row, cube_row)
            max_row = max(max_row, cube_row)
            min_col = min(min_col, cube_col)
            max_col = max(max_col, cube_col)

        up = max(up, min_row - hole_row)
        down = max(down, hole_row - max_row)
        left = max(left, min_col - hole_col)
        right = max(right, hole_col - max_col)

    direction_bound = up + down + left + right
    lower_bound = max(
        direction_bound,
        nearest_cube_bound,
        max(nearest_hole_for_cube),
    )

    if lower_bound == inf:
        return inf

    if _has_perfect_matching(distance_matrix, lower_bound):
        return lower_bound

    # Only a distance appearing in the matrix can change the matching.
    thresholds = sorted({
        distance
        for distances in distance_matrix
        for distance in distances
        if lower_bound < distance < inf
    })

    low, high = 0, len(thresholds)

    while low < high:
        middle = (low + high) // 2
        if _has_perfect_matching(distance_matrix, thresholds[middle]):
            high = middle
        else:
            low = middle + 1

    return thresholds[low] if low < len(thresholds) else inf

