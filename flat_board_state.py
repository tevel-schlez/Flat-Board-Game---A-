# you can add global params
from math import isqrt

class flat_board_state:
    def __init__(self, instance_map=None, *args, **kwargs):
        #we must check any invalidity withing the given flat board. we know its a square/rectangle
        cells = tuple(instance_map) if instance_map is not None else ()
        rows = kwargs.get("rows")
        cols = kwargs.get("cols")

        #basically if we got an instance map
        if cells and isinstance(cells[0], (list, tuple)):
            map_rows = len(cells)
            map_cols = len(cells[0])

            #if we got a different size of row - just checking for validity
            if any(len(row) != map_cols for row in cells):
                raise ValueError("All board rows must have the same length")
            if rows is not None and rows != map_rows:
                raise ValueError("rows does not match the board")
            if cols is not None and cols != map_cols:
                raise ValueError("cols does not match the board")

            rows, cols = map_rows, map_cols
            cells = tuple(cell for row in cells for cell in row)

        #if we get no lengths of rows and columns its a square, so we calculate the lengths
        elif rows is None and cols is None:
            rows = cols = isqrt(len(cells))

        elif rows is None and cols > 0:
            rows = len(cells) // cols

        elif cols is None and rows > 0:
            cols = len(cells) // rows

        if rows == cols == 0 and not cells:
            self.board = ()
            self.rows = self.cols = 0
            return

        if (
            rows is None or cols is None
            or rows <= 0 or cols <= 0
            or rows * cols != len(cells)
        ):
            raise ValueError("Board dimensions must match the number of cells")

        self.board = cells
        self.rows = rows
        self.cols = cols

    @staticmethod
    def is_goal_state(_flat_board_state):
        #we can just check that there are no holes left
        board = _flat_board_state.board if isinstance(_flat_board_state, flat_board_state) else _flat_board_state
        return 0 not in board

    # each state has 4 neighbors - moving left, right, up, down
    def get_neighbors(self):
        neighbors = []
        board = self.board
        rows = getattr(self, 'rows', None)
        cols = getattr(self, 'cols', None)

        if rows is None or cols is None:
            n = int(len(board) ** 0.5)
            rows = n
            cols = n

        directions = [
            ("UP", -1, 0),
            ("DOWN", 1, 0),
            ("LEFT", 0, -1),
            ("RIGHT", 0, 1)
        ]

        #finding all the cubes on the board
        cubes = [
            (i // cols, i % cols)
            for i, cell in enumerate(board)
            if cell == 3
        ]

        #we add cubes into order so that there will be no runs into
        for action, dr, dc in directions:
            if action == "UP":
                ordered_cubes = sorted(cubes, key=lambda p: p[0])
            elif action == "DOWN":
                ordered_cubes = sorted(cubes, key=lambda p: -p[0])
            elif action == "LEFT":
                ordered_cubes = sorted(cubes, key=lambda p: p[1])
            else:  # RIGHT
                ordered_cubes = sorted(cubes, key=lambda p: -p[1])

            current_grid = list(board)

            for r, c in cubes:
                current_grid[r * cols + c] = 1

            final_cube_positions = []

            for r, c in ordered_cubes:
                nr, nc = r + dr, c + dc

                #if the cubes are the edges or they are beside another cube, they cannot be moved
                if not (0 <= nr < rows and 0 <= nc < cols) or current_grid[nr * cols + nc] == 2:
                    final_cube_positions.append((r, c))
                #if the cube fills a hole
                elif current_grid[nr * cols + nc] == 0:
                    current_grid[nr * cols + nc] = 1
                elif (nr, nc) in final_cube_positions:
                    final_cube_positions.append((r, c))
                else:
                    final_cube_positions.append((nr, nc))

            #placing the cubes in their new positions
            for r, c in final_cube_positions:
                current_grid[r * cols + c] = 3

            new_flat_board = tuple(current_grid)

            if new_flat_board != board:
                #creating neighbor
                neighbor_state = type(self)(new_flat_board, rows=rows, cols=cols)
                neighbor_state.rows = rows
                neighbor_state.cols = cols
                neighbors.append((neighbor_state, 1))

        return neighbors


    # you can change the body of the function if you want
    # def __hash__(self):

    # you can change the body of the function if you want
    # def __eq__(self, other):
    # you can change the body of the function if you want

    def get_state_board(self):
        rows = getattr(self, 'rows', None)
        cols = getattr(self, 'cols', None)
        if cols is None:
            cols = int(len(self.board) ** 0.5)
        return [list(self.board[i:i + cols]) for i in range(0, len(self.board), cols)]


    def get_state_str(self):
        return str(self.board)

    # you can add helper functions
