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


if __name__ == "__main__":
    unittest.main(verbosity=2)