# you can add global params

class flat_board_state:
    def __init__(self, instance_map=None, *args, **kwargs):
        # you can use the init function for several purposes
        self.board = tuple(instance_map) if instance_map else ()

    @staticmethod
    def is_goal_state(_flat_board_state):
        return all(cell in (1,2) for cell in _flat_board_state)

    # each state has 4 neighbors - moving left, right, up, down

    def get_neighbors(self):
        neighbors = []
        board = self.board
        rows = self.rows
        cols = self.cols

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
                #calculate new row and column
                nr, nc = r + dr, c + dc

                #if the cude does run into a wall or another cube, it cannot be moved
                if not (0 <= nr < rows and 0 <= nc < cols) or current_grid[nr * cols + nc] == 2:
                    final_cube_positions.append((r, c))
                #if the cube filled a hole, it should be gone
                elif current_grid[nr * cols + nc] == 0:
                    current_grid[nr * cols + nc] = 1
                elif (nr, nc) in final_cube_positions:
                    final_cube_positions.append((r, c))
                else:
                    final_cube_positions.append((nr, nc))

            for r, c in final_cube_positions:
                #add the cubes in their current position
                current_grid[r * cols + c] = 3

            new_flat_board = tuple(current_grid)

            if new_flat_board != board:
                neighbor_state = type(self)(new_flat_board, rows=rows, cols=cols)
                neighbors.append((neighbor_state, 1))

        return neighbors


    # you can change the body of the function if you want
    # def __hash__(self):

    # you can change the body of the function if you want
    # def __eq__(self, other):
    # you can change the body of the function if you want

    def get_state_board(self):
        cols = self.cols
        return [list(self.board[i:i + cols]) for i in range(0, len(self.board), cols)]


    def get_state_str(self):
        return str(self.board)

    # you can add helper functions
