
import unittest

from flat_board_state import flat_board_state


class TestFlatBoardState(unittest.TestCase):

    # Helper: create a state from a 2D board
    def create_state(self, board):
        rows = len(board)
        cols = len(board[0])

        flat_board = tuple(
            cell
            for row in board
            for cell in row
        )

        state = flat_board_state()
        state.board = flat_board
        state.rows = rows
        state.cols = cols

        return state

    # Helper: get neighbors as a dictionary
    def get_neighbors_dict(self, state):
        return {
            neighbor.board: cost
            for neighbor, cost in state.get_neighbors()
        }

    # 1. Goal state tests
    def test_goal_state(self):
        self.assertTrue(
            flat_board_state.is_goal_state((1, 1, 2, 1, 2))
        )

        self.assertFalse(
            flat_board_state.is_goal_state((1, 3, 2, 1))
        )

        self.assertTrue(
            flat_board_state.is_goal_state(())
        )

    # 2. A cube can move in all four directions
    def test_all_four_directions(self):
        state = self.create_state([
            [1, 1, 1],
            [1, 3, 1],
            [1, 1, 1]
        ])

        neighbors = self.get_neighbors_dict(state)

        expected_boards = {
            (1, 3, 1, 1, 1, 1, 1, 1, 1),  # UP
            (1, 1, 1, 1, 1, 1, 1, 3, 1),  # DOWN
            (1, 1, 1, 3, 1, 1, 1, 1, 1),  # LEFT
            (1, 1, 1, 1, 1, 3, 1, 1, 1)   # RIGHT
        }

        self.assertEqual(set(neighbors.keys()), expected_boards)

    # 3. A cube cannot move through a wall
    def test_wall_blocks_movement(self):
        state = self.create_state([
            [1, 1, 1],
            [1, 3, 2],
            [1, 1, 1]
        ])

        neighbors = self.get_neighbors_dict(state)

        # Moving right is blocked by the wall
        right_blocked = (
            1, 1, 1,
            1, 3, 2,
            1, 1, 1
        )

        self.assertNotIn(right_blocked, neighbors)

        # The other three directions are possible
        self.assertEqual(len(neighbors), 3)

    # 4. A cube cannot move outside the board
    def test_board_boundaries(self):
        state = self.create_state([
            [3, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ])

        neighbors = self.get_neighbors_dict(state)

        # UP and LEFT are blocked by boundaries
        self.assertEqual(len(neighbors), 2)

    # 5. A cube disappears when entering a hole
    def test_cube_fills_hole(self):
        state = self.create_state([
            [1, 1, 1],
            [1, 3, 0],
            [1, 1, 1]
        ])

        neighbors = self.get_neighbors_dict(state)

        expected_board = (
            1, 1, 1,
            1, 1, 1,
            1, 1, 1
        )

        self.assertIn(expected_board, neighbors)
        self.assertEqual(neighbors[expected_board], 1)

    # 6. Multiple cubes can move in the same direction
    def test_multiple_cubes(self):
        state = self.create_state([
            [3, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 3, 1]
        ])

        neighbors = self.get_neighbors_dict(state)

        # Both cubes move one cell to the right
        expected_right = (
            1, 3, 1, 1,
            1, 1, 1, 1,
            1, 1, 1, 3
        )

        self.assertIn(expected_right, neighbors)

    # 7. The original state should not be returned as a neighbor
    def test_original_state_not_in_neighbors(self):
        state = self.create_state([
            [1, 1, 1],
            [1, 3, 2],
            [1, 1, 1]
        ])

        neighbors = self.get_neighbors_dict(state)

        self.assertNotIn(state.board, neighbors)

    # 8. All transitions have cost 1
    def test_transition_cost(self):
        state = self.create_state([
            [1, 1, 1],
            [1, 3, 1],
            [1, 1, 1]
        ])

        neighbors = state.get_neighbors()

        for neighbor, cost in neighbors:
            self.assertEqual(cost, 1)

    # 9. No duplicate neighbors
    def test_no_duplicate_neighbors(self):
        state = self.create_state([
            [1, 1, 1],
            [1, 3, 1],
            [1, 1, 1]
        ])

        neighbors = state.get_neighbors()

        boards = [neighbor.board for neighbor, cost in neighbors]

        self.assertEqual(len(boards), len(set(boards)))

    # 10. Child states should preserve board dimensions
    def test_child_dimensions(self):
        state = self.create_state([
            [1, 1, 1],
            [1, 3, 1],
            [1, 1, 1]
        ])

        neighbors = state.get_neighbors()

        for neighbor, cost in neighbors:
            self.assertEqual(neighbor.rows, 3)
            self.assertEqual(neighbor.cols, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
