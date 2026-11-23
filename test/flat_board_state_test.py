import unittest

from flat_board_state import flat_board_state


class TestFlatBoardState(unittest.TestCase):
    def test_constructor_flattens_rectangular_board(self):
        board = [
            [3, 1, 0],
            [1, 2, 1],
        ]
        state = flat_board_state(board)

        self.assertEqual(state.board, (3, 1, 0, 1, 2, 1))
        self.assertEqual((state.rows, state.cols), (2, 3))
        self.assertEqual(state.get_state_board(), board)

    def test_goal_state(self):
        solved = flat_board_state([[1, 2], [1, 1]])
        unsolved = flat_board_state([[3, 2], [1, 0]])

        self.assertTrue(flat_board_state.is_goal_state(solved))
        self.assertFalse(flat_board_state.is_goal_state(unsolved))
        self.assertTrue(flat_board_state.is_goal_state(solved.board))
        self.assertFalse(flat_board_state.is_goal_state(unsolved.board))

    def test_cube_can_move_in_all_four_directions(self):
        state = flat_board_state([
            [0, 1, 1],
            [1, 3, 1],
            [1, 1, 1],
        ])

        actual = [
            (neighbor.board, cost)
            for neighbor, cost in state.get_neighbors()
        ]
        expected = [
            ((0, 3, 1, 1, 1, 1, 1, 1, 1), 1),  # UP
            ((0, 1, 1, 1, 1, 1, 1, 3, 1), 1),  # DOWN
            ((0, 1, 1, 3, 1, 1, 1, 1, 1), 1),  # LEFT
            ((0, 1, 1, 1, 1, 3, 1, 1, 1), 1),  # RIGHT
        ]

        self.assertCountEqual(actual, expected)

    def test_wall_blocks_movement(self):
        state = flat_board_state([
            [0, 1, 1],
            [1, 3, 2],
            [1, 1, 1],
        ])

        actual = [neighbor.board for neighbor, _ in state.get_neighbors()]
        expected = [
            (0, 3, 1, 1, 1, 2, 1, 1, 1),  # UP
            (0, 1, 1, 1, 1, 2, 1, 3, 1),  # DOWN
            (0, 1, 1, 3, 1, 2, 1, 1, 1),  # LEFT
        ]

        self.assertCountEqual(actual, expected)

    def test_board_boundaries_block_movement(self):
        state = flat_board_state([
            [3, 1, 0],
            [1, 1, 1],
        ])

        actual = [neighbor.board for neighbor, _ in state.get_neighbors()]

        self.assertCountEqual(actual, [
            (1, 3, 0, 1, 1, 1),  # RIGHT
            (1, 1, 0, 3, 1, 1),  # DOWN
        ])

    def test_cube_fills_hole_and_disappears(self):
        state = flat_board_state([[3, 0]])

        neighbors = state.get_neighbors()

        self.assertEqual(len(neighbors), 1)
        neighbor, cost = neighbors[0]
        self.assertEqual(neighbor.board, (1, 1))
        self.assertEqual(cost, 1)
        self.assertTrue(flat_board_state.is_goal_state(neighbor))
        self.assertEqual(state.board, (3, 0))

    def test_multiple_cubes_move_together_and_preserve_dimensions(self):
        state = flat_board_state([
            [3, 1, 1, 1],
            [0, 1, 1, 0],
            [1, 1, 3, 1],
        ])

        neighbors = state.get_neighbors()
        expected_right = (
            1, 3, 1, 1,
            0, 1, 1, 0,
            1, 1, 1, 3,
        )

        self.assertIn(expected_right, [neighbor.board for neighbor, _ in neighbors])
        for neighbor, _ in neighbors:
            self.assertEqual((neighbor.rows, neighbor.cols), (3, 4))

    def test_cube_can_move_into_cell_vacated_by_another_cube(self):
        state = flat_board_state([[3, 3, 0, 0]])

        actual = [neighbor.board for neighbor, _ in state.get_neighbors()]

        self.assertEqual(actual, [(1, 3, 1, 0)])

    def test_blocked_cube_also_blocks_cube_behind_it(self):
        state = flat_board_state([[3, 3, 2, 0, 0]])

        self.assertEqual(state.get_neighbors(), [])

    def test_flat_tuple_with_explicit_dimensions(self):
        state = flat_board_state((3, 1, 0, 1, 2, 1), rows=2, cols=3)

        self.assertEqual((state.rows, state.cols), (2, 3))
        self.assertEqual(state.get_state_board(), [[3, 1, 0], [1, 2, 1]])

    def test_tuple_of_rows_is_flattened(self):
        state = flat_board_state(((3, 1), (1, 2), (0, 1)))

        self.assertEqual(state.board, (3, 1, 1, 2, 0, 1))
        self.assertEqual((state.rows, state.cols), (3, 2))
        self.assertEqual(state.get_state_board(), [[3, 1], [1, 2], [0, 1]])

    def test_square_flat_tuple_infers_both_dimensions(self):
        state = flat_board_state((3, 1, 2, 0))

        self.assertEqual((state.rows, state.cols), (2, 2))
        self.assertEqual(state.get_state_board(), [[3, 1], [2, 0]])

    def test_flat_tuple_infers_rows_from_cols(self):
        state = flat_board_state((3, 1, 0, 1, 2, 1), cols=3)

        self.assertEqual((state.rows, state.cols), (2, 3))

    def test_flat_tuple_infers_cols_from_rows(self):
        state = flat_board_state((3, 1, 0, 1, 2, 1), rows=3)

        self.assertEqual((state.rows, state.cols), (3, 2))

    def test_flat_tuple_rejects_incorrect_dimensions(self):
        with self.assertRaises(ValueError):
            flat_board_state((3, 1, 0, 1, 2, 1), rows=2, cols=4)

    def test_rectangular_flat_tuple_requires_a_dimension(self):
        with self.assertRaises(ValueError):
            flat_board_state((3, 1, 0, 1, 2, 1))

    def test_tuple_of_rows_rejects_uneven_row_lengths(self):
        with self.assertRaises(ValueError):
            flat_board_state(((3, 1, 0), (1, 2)))

    def test_empty_tuple_is_a_goal_and_has_no_neighbors(self):
        state = flat_board_state(())

        self.assertEqual(state.get_state_board(), [])
        self.assertTrue(flat_board_state.is_goal_state(state))
        self.assertEqual(state.get_neighbors(), [])

    def test_movement_does_not_wrap_between_rows(self):
        # The cube is at the right edge of the first row.
        state = flat_board_state((1, 1, 3, 0, 1, 1), rows=2, cols=3)

        actual = [
            (neighbor.board, cost)
            for neighbor, cost in state.get_neighbors()
        ]

        self.assertCountEqual(actual, [
            ((1, 3, 1, 0, 1, 1), 1),  # LEFT
            ((1, 1, 1, 0, 1, 3), 1),  # DOWN
        ])

    def test_cube_fills_hole_by_moving_up(self):
        state = flat_board_state((0, 3), rows=2, cols=1)

        actual = [
            (neighbor.board, cost)
            for neighbor, cost in state.get_neighbors()
        ]

        self.assertEqual(actual, [((1, 1), 1)])

    def test_two_cubes_fill_two_holes_in_one_move(self):
        state = flat_board_state(((3, 0), (3, 0)))

        actual = [
            (neighbor.board, cost)
            for neighbor, cost in state.get_neighbors()
        ]

        self.assertEqual(actual, [((1, 1, 1, 1), 1)])

    def test_init_rejects_uneven_row_lengths(self):
        boards = (
            ((3, 1, 0), (1, 2)),
            ((3, 1), (1, 2, 0)),
            ((3, 1, 0), ()),
        )

        for board in boards:
            with self.subTest(board=board):
                with self.assertRaisesRegex(
                    ValueError, "All board rows must have the same length"
                ):
                    flat_board_state(board)

    def test_init_rejects_dimensions_that_conflict_with_nested_board(self):
        board = ((3, 1, 0), (1, 2, 1))
        cases = (
            ({"rows": 3}, "rows does not match the board"),
            ({"cols": 2}, "cols does not match the board"),
        )

        for kwargs, message in cases:
            with self.subTest(**kwargs):
                with self.assertRaisesRegex(ValueError, message):
                    flat_board_state(board, **kwargs)

    def test_init_rejects_invalid_board_dimensions(self):
        flat = (3, 1, 0, 1, 2, 1)
        cases = (
            (flat, {}),                         # Six cells cannot form a square.
            (flat, {"rows": 2, "cols": 4}),      # Too many positions.
            (flat, {"rows": 2, "cols": 2}),      # Too few positions.
            (flat, {"rows": 4}),                 # Six is not divisible by four.
            (flat, {"cols": 4}),
            (flat, {"rows": 0}),                 # Missing cols cannot be inferred.
            (flat, {"cols": 0}),                 # Missing rows cannot be inferred.
            (flat, {"rows": 0, "cols": 3}),
            (flat, {"rows": 2, "cols": 0}),
            (flat, {"rows": -2, "cols": 3}),
            (flat, {"rows": 2, "cols": -3}),
            ((), {"rows": 1, "cols": 1}),       # No cell for the declared board.
            (((), ()), {}),                      # Rows exist but are empty.
        )

        for board, kwargs in cases:
            with self.subTest(board=board, dimensions=kwargs):
                with self.assertRaisesRegex(
                    ValueError, "Board dimensions must match the number of cells"
                ):
                    flat_board_state(board, **kwargs)

    def test_neighbors_can_shift_adjacent_cubes_left(self):
        state = flat_board_state((0, 0, 3, 3), rows=1, cols=4)

        actual = [
            (neighbor.board, cost)
            for neighbor, cost in state.get_neighbors()
        ]

        self.assertEqual(actual, [((0, 1, 3, 1), 1)])

    def test_neighbors_can_shift_adjacent_cubes_down(self):
        state = flat_board_state(((3,), (3,), (0,), (0,)))

        actual = [
            (neighbor.board, cost)
            for neighbor, cost in state.get_neighbors()
        ]

        self.assertEqual(actual, [((1, 3, 1, 0), 1)])

    def test_neighbors_can_move_one_cube_while_others_are_blocked(self):
        state = flat_board_state((
            (3, 3, 2),
            (0, 3, 1),
            (0, 1, 0),
        ))

        actual = [
            (neighbor.board, cost)
            for neighbor, cost in state.get_neighbors()
        ]

        self.assertCountEqual(actual, [
            ((3, 3, 2, 0, 1, 3, 0, 1, 0), 1),  # RIGHT
            ((1, 1, 2, 1, 3, 1, 0, 3, 0), 1),  # DOWN
            ((3, 3, 2, 1, 1, 1, 0, 1, 0), 1),  # LEFT
        ])

    def test_neighbors_can_move_through_a_previously_filled_hole(self):
        state = flat_board_state((0, 3, 3, 0), rows=1, cols=4)

        after_right = next(
            neighbor
            for neighbor, _ in state.get_neighbors()
            if neighbor.board == (0, 1, 3, 1)
        )

        actual = [
            (neighbor.board, cost)
            for neighbor, cost in after_right.get_neighbors()
        ]

        self.assertCountEqual(actual, [
            ((0, 3, 1, 1), 1),  # LEFT
            ((0, 1, 1, 3), 1),  # RIGHT, into the previously filled hole
        ])
        self.assertEqual(state.board, (0, 3, 3, 0))
        self.assertEqual(after_right.board, (0, 1, 3, 1))

    def test_solved_tuple_board_has_no_neighbors(self):
        state = flat_board_state(((1, 2, 1), (1, 1, 2)))

        self.assertEqual(state.get_neighbors(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)