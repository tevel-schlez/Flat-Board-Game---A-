import unittest
from statistics import median
from time import perf_counter

from flat_board_state import flat_board_state
from heuristics import (
    _distances_from_hole,
    advanced_heuristic,
    base_heuristic,
)
from search import get_gen_exp_count, search
import os

class TestHeuristicBenchmark(unittest.TestCase):
    REPEATS = 3

    @staticmethod
    def make_two_corridors(rows, cols, distance, opposite_directions):
        """Build two isolated corridors inside a large rectangular board."""
        board = [[2] * cols for _ in range(rows)]
        top = 1
        bottom = rows - 2
        start = 1
        end = start + distance

        for row in (top, bottom):
            for col in range(start, end + 1):
                board[row][col] = 1

        board[top][start] = 3
        board[top][end] = 0

        if opposite_directions:
            board[bottom][start] = 0
            board[bottom][end] = 3
        else:
            board[bottom][start] = 3
            board[bottom][end] = 0

        return flat_board_state(board)

    @staticmethod
    def make_wall_detour(rows, cols, distance):
        """Build a U-shaped path between a cube and a hole."""
        board = [[2] * cols for _ in range(rows)]
        start = 1
        end = start + distance

        # The cube and hole are in row 1. The corridor is in row 3.
        for col in range(start, end + 1):
            board[3][col] = 1

        board[2][start] = 1
        board[2][end] = 1
        board[1][start] = 3
        board[1][end] = 0

        return flat_board_state(board)

    def benchmark(self, name, state, expected_cost):
        print(f"\n{name} | {state.rows} x {state.cols}")
        print(f"{'heuristic':<22}{'median ms':>12}{'generate':>12}"
              f"{'expand':>12}{'cost':>8}")

        for heuristic in (base_heuristic, advanced_heuristic):
            with self.subTest(heuristic=heuristic.__name__):
                times_ms = []
                counts = []

                for _ in range(self.REPEATS):
                    # Cold cache between runs. Cache hits within a run still count.
                    _distances_from_hole.cache_clear()

                    started = perf_counter()
                    path = search(state, heuristic)
                    times_ms.append((perf_counter() - started) * 1000)

                    # search() resets the counters on every call.
                    generated, expanded = get_gen_exp_count()
                    counts.append((generated, expanded))

                    self.assertIsNotNone(path, "Search did not find a solution")
                    self.assertTrue(flat_board_state.is_goal_state(path[-1].state))
                    self.assertEqual(path[-1].g, expected_cost)

                generated, expanded = counts[0]
                self.assertTrue(
                    all(count == counts[0] for count in counts),
                    f"Search counts varied between runs: {counts}",
                )

                print(f"{heuristic.__name__:<22}{median(times_ms):>12.2f}"
                      f"{generated:>12}{expanded:>12}{expected_cost:>8}")

    def test_large_board_same_direction(self):
        distance = 20
        state = self.make_two_corridors(250, 400, distance, False)

        # Each RIGHT command advances both cubes.
        self.benchmark("Same direction", state, expected_cost=distance)

    def test_large_board_opposite_directions(self):
        distance = 20
        state = self.make_two_corridors(400, 500, distance, True)

        # One cube needs 20 RIGHT commands and the other needs 20 LEFT.
        self.benchmark("Opposite directions", state, expected_cost=2 * distance)

    def test_large_board_wall_detour(self):
        distance = 30
        state = self.make_wall_detour(400, 500, distance)

        # Two DOWN commands, 30 RIGHT commands, and two UP commands.
        self.benchmark("Wall detour", state, expected_cost=distance + 4)

    def test_huge_board_with_misleading_dead_end(self):
        rows, cols = 500, 500
        board = [[2] * cols for _ in range(rows)]

        top_row = 1
        start_col = 1
        horizontal_distance = 120
        detour_depth = 40

        goal_col = start_col + horizontal_distance
        bottom_row = top_row + detour_depth

        # Carve the real U-shaped route to the hole.
        for row in range(top_row, bottom_row + 1):
            board[row][start_col] = 1
            board[row][goal_col] = 1

        for col in range(start_col, goal_col + 1):
            board[bottom_row][col] = 1

        # Carve a dead end that points directly toward the hole.
        # Leave one wall cell between the dead end and the hole.
        for col in range(start_col + 1, goal_col - 1):
            board[top_row][col] = 1

        board[top_row][start_col] = 3
        board[top_row][goal_col] = 0

        state = flat_board_state(board)
        expected_cost = horizontal_distance + 2 * detour_depth

        self.assertEqual(base_heuristic(state), 120)
        self.assertEqual(advanced_heuristic(state), 200)
        self.benchmark("Huge board with dead end", state, expected_cost)

    def test_huge_board_with_10000_misleading_states(self):
        board = [[2] * 106 for _ in range(112)]
        start_row, start_col = 1, 1
        goal_col = 104
        bottom_row = 111

        # A 100 x 100 room with a single entrance.
        for row in range(1, 101):
            for col in range(3, 103):
                board[row][col] = 1

        board[1][2] = 1

        # The real route goes down, across, and back up.
        for row in range(start_row, bottom_row + 1):
            board[row][start_col] = 1
            board[row][goal_col] = 1

        for col in range(start_col, goal_col + 1):
            board[bottom_row][col] = 1

        board[start_row][start_col] = 3
        board[start_row][goal_col] = 0

        state = flat_board_state(board)
        expected_cost = 110 + 103 + 110

        self.assertEqual(base_heuristic(state), 103)
        self.assertEqual(advanced_heuristic(state), expected_cost)
        self.benchmark("Huge board with 10,000 misleading states", state, expected_cost)

    def test_100000_misleading_states(self):
        room_height = 200
        room_width = 500
        start_row, start_col = 1, 1
        goal_col = room_width + 4
        bottom_row = room_height + 11

        board = [[2] * (goal_col + 2) for _ in range(bottom_row + 1)]

        # Dead-end room with exactly 100,000 cells and a single entrance.
        for row in range(1, room_height + 1):
            for col in range(3, 3 + room_width):
                board[row][col] = 1

        board[start_row][2] = 1

        # The only route to the hole runs around the room.
        for row in range(start_row, bottom_row + 1):
            board[row][start_col] = 1
            board[row][goal_col] = 1

        for col in range(start_col, goal_col + 1):
            board[bottom_row][col] = 1

        board[start_row][start_col] = 3
        board[start_row][goal_col] = 0

        state = flat_board_state(board)
        expected_cost = 2 * (bottom_row - start_row) + goal_col - start_col

        self.assertEqual(expected_cost, 923)
        self.assertEqual(base_heuristic(state), 503)
        self.assertEqual(advanced_heuristic(state), 923)

        cases = [(advanced_heuristic, 924, 923)]
        if os.getenv("RUN_100K_BASE") == "1":
            cases.append((base_heuristic, 100_924, 100_924))

        for heuristic, expected_generated, expected_expanded in cases:
            with self.subTest(heuristic=heuristic.__name__):
                _distances_from_hole.cache_clear()

                started = perf_counter()
                path = search(state, heuristic)
                elapsed = perf_counter() - started
                generated, expanded = get_gen_exp_count()

                print(
                    f"\n{heuristic.__name__}: {elapsed:.3f}s | "
                    f"generate={generated:,} | expand={expanded:,}",
                    flush=True,
                )

                self.assertIsNotNone(path)
                self.assertTrue(flat_board_state.is_goal_state(path[-1].state))
                self.assertEqual(path[-1].g, expected_cost)
                self.assertEqual(generated, expected_generated)
                self.assertEqual(expanded, expected_expanded)

if __name__ == "__main__":
    unittest.main(verbosity=2)