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

        # Directions: (row_delta, col_delta) for Up, Down, Left, Right
        directions = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1)
        }

        board_list = self.get_state_board()
        rows = len(board_list)
        cols = len(board_list[0])

        for action, (dr, dc) in directions.items():
            new_board = [list(row) for row in board_list]
            cubes = []
            for r in range(rows):
                for c in range(cols):
                    #if this cude contains a cube
                    if new_board[r][c] == 3:
                        cubes.append((r, c))
            moved = True
            current_cubes = set(cubes)
            active_cubes = set(cubes)
            next_cubes_positions = {}
            blocked_cubes = set()

            proposed_moves = {}
            for (r, c) in current_cubes:
                nr, nc = r + dr, c + dc
                #if the cubes are not in the egde or if they are not beside a wall, they can be moved
                if not (0 <= nr < rows and 0 <= nc < cols) or new_board[nr][nc] == 2:
                    proposed_moves[(r, c)] = (r, c)
                else:
                    #otherwise they wont be moved
                    proposed_moves[(r, c)] = (nr, nc)

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
