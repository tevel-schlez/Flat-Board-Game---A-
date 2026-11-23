from search_node import search_node
from flat_board_state import flat_board_state
from itertools import count
from heapq import heappush
from heapq import heappop

count_generated = 0
count_expanded = 0

def create_open_set():
    return [], {}, count()

def create_closed_set():
    return {}

#helper
def _state_key(vn):
    state = vn.state
    return state.rows, state.cols, state.board


def add_to_open(vn, open_set):
    heap, active_nodes, insertion_order = open_set
    key = _state_key(vn)

    active_nodes[key] = vn
    priority = vn.g + vn.h
    heappush(heap, (priority, next(insertion_order), key, vn))


def open_not_empty(open_set):
    _, active_nodes, _ = open_set
    return bool(active_nodes)


def get_best(open_set):
    heap, active_nodes, _ = open_set

    while heap:
        _, _, key, node = heappop(heap)

        if active_nodes.get(key) is node:
            del active_nodes[key]
            return node

    raise IndexError("OPEN is empty")


def add_to_closed(vn, closed_set):
    closed_set[_state_key(vn)] = vn.g


def duplicate_in_open(vn, open_set):
    _, active_nodes, _ = open_set
    key = _state_key(vn)
    previous_node = active_nodes.get(key)

    if previous_node is None:
        return False

    if previous_node.g <= vn.g:
        return True

    del active_nodes[key]
    return False


def duplicate_in_closed(vn, closed_set):
    key = _state_key(vn)
    previous_g = closed_set.get(key)

    if previous_g is None:
        return False

    if previous_g <= vn.g:
        return True

    del closed_set[key]
    return False

# helps to debug sometimes..
def print_path(path):
    for i in range(len(path)-1):
        print(f"[{path[i].state.get_state_str()}]", end=", ")
    print(path[-1].state.state_str)

def get_gen_exp_count():
    global count_generated
    global count_expanded
    return count_generated, count_expanded

def search(start_state, heuristic):
    global count_generated
    global count_expanded
    count_generated = 0
    count_expanded = 0
    open_set = create_open_set()
    closed_set = create_closed_set()
    start_node = search_node(start_state, 0, heuristic(start_state))
    add_to_open(start_node, open_set)

    while open_not_empty(open_set):

        current = get_best(open_set)

        if flat_board_state.is_goal_state(current.state):
            path = []
            while current:
                path.append(current)
                current = current.prev
            path.reverse()
            return path

        add_to_closed(current, closed_set)
        count_expanded += 1

        for neighbor, edge_cost in current.get_neighbors():
            curr_neighbor = search_node(neighbor, current.g + edge_cost, heuristic(neighbor), current)
            if not duplicate_in_open(curr_neighbor, open_set) and not duplicate_in_closed(curr_neighbor, closed_set):
                add_to_open(curr_neighbor, open_set)
                count_generated += 1

    return None




