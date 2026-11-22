# Flat Board Puzzle — Heuristic Search (A*)

A Python 3.10 implementation of the **A\* Heuristic Search** algorithm designed to solve the **Flat Board ("לוח-שטוח")** grid puzzle in the minimum number of moves.

---

## 🎮 Game Description & Rules

**Flat Board** is a grid-based puzzle game played on an $N \times M$ rectangular board containing filled tiles, walls, missing tiles (holes), and movable cubes.

### Board Representation (State Space)
Each cell in the $N \times M$ grid holds an integer value between `0` and `3`:
* **`0` — Hole (Missing Tile):** An empty gap in the board that needs to be filled.
* **`1` — Filled Tile:** A standard walkable tile on the board.
* **`2` — Wall:** An impassable obstacle (board boundaries also act as walls).
* **`3` — Cube:** A movable block initially resting on top of a filled tile.

*(Note: In any valid initial board, the number of cubes equals the number of holes).*

### Mechanics & Operators
At each step, the player chooses one of **4 actions**: `Up`, `Down`, `Left`, or `Right`.

* **Simultaneous Movement:** Whenever an action is selected, **all cubes** on the board attempt to slide **one step** in that chosen direction simultaneously.
* **Collisions:** A cube stays in its current position if moving in the chosen direction would cause it to hit:
  * A wall (`2`),
  * The outer boundary of the board, or
  * Another cube (`3`) that is blocked and cannot move.
* **Filling Holes:** If a cube slides onto a hole (`0`), it plugs the hole—both the cube and the hole disappear, turning that cell into a regular filled tile (`1`).

### Objective (Goal State)
Find the **shortest sequence of moves** required to plug all holes on the board. A state is considered a **Goal State** when there are no remaining holes (`0`) on the board (i.e., the board consists solely of filled tiles `1` and walls `2`).

---

## 🧠 Search & Heuristics

The solver uses the **A\*** search algorithm ($f(n) = g(n) + h(n)$) to guarantee an optimal (shortest-path) solution:

1. **Base Heuristic (`base_heuristic`):**
   * For each remaining hole on the board, computes the minimum Manhattan distance from any active cube to that hole, and returns the maximum among these minimum distances.
2. **Advanced Heuristic (`advanced_heuristic`):**
   * An admissible, improved heuristic designed to prune the search space more effectively, reducing runtime and the number of generated/expanded nodes while preserving optimality.

---

## 📁 Project Structure

```text
flat_board_state/
│
├── flat_board_state.py   # State representation, goal check, and neighbor generation (move logic)
├── heuristics.py         # Base and advanced admissible heuristic functions
├── search.py             # A* search loop, OPEN and CLOSED set management
├── search_node.py        # Search tree node wrapper (tracks g, h, f, and parent pointers)
└── main.py               # Entry point for running tests and sample boards
```

---

## 🚀 Getting Started

### Prerequisites
* Python **3.10** or higher

### Running the Solver
Run the main script from the project root:
```bash
python flat_board_state/main.py
```