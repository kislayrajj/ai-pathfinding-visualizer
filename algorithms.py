import pygame 
import math
from queue import PriorityQueue, Queue
from node import Node # Need Node class for type hinting / checks if desired
from constants import * # Need colors, ROWS

# --- Helper Functions ---
def h(p1, p2):
    """Heuristic function (Manhattan distance)."""
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw_func, start_node):
    """Draws the path from end to start by changing node colors."""
    path_nodes = []
    temp = current
    while temp in came_from:
        temp = came_from[temp]
        if temp != start_node: # Don't color the start node purple
             path_nodes.append(temp)
        # Safety break
        if len(path_nodes) > ROWS * ROWS: # Use ROWS from constants
            print("Error: Path reconstruction exceeded maximum possible length.")
            break

    for node in reversed(path_nodes):
        if node != start_node:
            node.make_path()
            # time.sleep(0.01) # Optional delay
            draw_func() # Call the draw function passed from visualizer
            pygame.display.update() # Update display immediately to see path build


# --- Algorithm Implementations ---
# All algorithms accept 'visualizer' object to access draw, stop_requested, check_for_quit

def a_star(visualizer, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty() and not visualizer.stop_requested:
        visualizer.check_for_quit()
        if visualizer.stop_requested: break

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, visualizer.draw, start)
            if not visualizer.stop_requested:
                end.make_end()
                start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end: neighbor.make_open()

        visualizer.draw()
        if current != start:
            current.make_closed()

    return False

def dijkstra(visualizer, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start)) # (distance, count, node)
    came_from = {}
    distance = {node: float("inf") for row in grid for node in row}
    distance[start] = 0
    open_set_hash = {start}

    while not open_set.empty() and not visualizer.stop_requested:
        visualizer.check_for_quit()
        if visualizer.stop_requested: break

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, visualizer.draw, start)
            if not visualizer.stop_requested:
                end.make_end()
                start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_distance = distance[current] + 1
            if temp_distance < distance[neighbor]:
                came_from[neighbor] = current
                distance[neighbor] = temp_distance
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((distance[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end: neighbor.make_open()

        visualizer.draw()
        if current != start:
            current.make_closed()

    return False


def bfs(visualizer, grid, start, end):
    queue = Queue()
    queue.put(start)
    came_from = {}
    visited = {start}

    while not queue.empty() and not visualizer.stop_requested:
        visualizer.check_for_quit()
        if visualizer.stop_requested: break

        current = queue.get()

        if current == end:
            reconstruct_path(came_from, end, visualizer.draw, start)
            if not visualizer.stop_requested:
                end.make_end()
                start.make_start()
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.put(neighbor)
                if neighbor != end: neighbor.make_open()

        visualizer.draw()
        if current != start:
            current.make_closed()

    return False


def dfs(visualizer, grid, start, end):
    stack = [start]
    came_from = {}
    visited = {start}

    while stack and not visualizer.stop_requested:
        visualizer.check_for_quit()
        if visualizer.stop_requested: break

        current = stack.pop()

        if current != start and current != end:
            current.make_current()
        visualizer.draw()
        # time.sleep(0.01)

        if current == end:
            visualizer.clear_search_visualization(clear_only_search=True, keep_current_algo_colors=True)
            reconstruct_path(came_from, end, visualizer.draw, start)
            if not visualizer.stop_requested:
                end.make_end()
                start.make_start()
            return True

        for neighbor in reversed(current.neighbors):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)
                if neighbor != end: neighbor.make_open()

        if current != start and current != end and not current.is_path():
             current.make_closed()

    return False


def hill_climbing(visualizer, grid, start, end):
    current = start
    came_from = {}
    path_nodes_visited = {start}

    while current != end and not visualizer.stop_requested:
        visualizer.check_for_quit()
        if visualizer.stop_requested: break

        neighbors = current.neighbors
        valid_neighbors = [n for n in neighbors if n not in path_nodes_visited]

        if not valid_neighbors:
            print("Hill Climbing Stuck: No unvisited neighbors.")
            if current != start: current.make_closed()
            visualizer.draw()
            return False

        valid_neighbors.sort(key=lambda neighbor: h(neighbor.get_pos(), end.get_pos()))
        best_neighbor = valid_neighbors[0]

        if h(best_neighbor.get_pos(), end.get_pos()) >= h(current.get_pos(), end.get_pos()):
            print(f"Hill Climbing Stuck: Best h={h(best_neighbor.get_pos(), end.get_pos())}, Current h={h(current.get_pos(), end.get_pos())}")
            if current != start: current.make_closed()
            visualizer.draw()
            return False

        came_from[best_neighbor] = current
        if current != start:
            current.make_closed()

        current = best_neighbor
        path_nodes_visited.add(current)
        if current != end:
            current.make_open()

        visualizer.draw()

    if current == end:
        reconstruct_path(came_from, end, visualizer.draw, start)
        if not visualizer.stop_requested:
            end.make_end()
            start.make_start()
        return True

    return False


# --- DLS / IDS ---
def dls_recursive(visualizer, node, end, limit, visited, came_from, start):
    visualizer.check_for_quit()
    if visualizer.stop_requested:
        return False, came_from, True # Found, CameFrom, Stopped

    if node == end:
        return True, came_from, False # Found, CameFrom, Not Stopped

    if limit <= 0:
        return False, came_from, False # Not Found, CameFrom, Not Stopped

    visited.add(node)
    if node != start and node != end:
        node.make_current()
    visualizer.draw()
    #time.sleep(0.005)

    found = False
    stopped = False
    for neighbor in node.neighbors:
        if visualizer.stop_requested:
             stopped = True
             break

        if neighbor not in visited:
            came_from[neighbor] = node
            found, came_from, stopped = dls_recursive(visualizer, neighbor, end, limit - 1, visited, came_from, start)
            if found or stopped:
                return found, came_from, stopped

    if node != start and node != end and not node.is_path():
        node.make_closed()

    return False, came_from, stopped

def lds(visualizer, grid, start, end, max_depth):
    visualizer.clear_search_visualization(clear_only_search=True)
    came_from = {}
    visited = set()

    print(f"LDS: Starting search with depth limit {max_depth}")
    found, came_from_result, stopped = dls_recursive(visualizer, start, end, max_depth, visited, came_from, start)

    visualizer.clear_search_visualization(clear_only_search=True, keep_current_algo_colors=True) # Clear cyan

    if stopped:
        print(f"LDS: Search stopped by user at depth limit {max_depth}.")
        return False

    if found:
        print(f"LDS: Path found within depth {max_depth}")
        reconstruct_path(came_from_result, end, visualizer.draw, start)
        end.make_end()
        start.make_start()
        return True
    else:
        print(f"LDS: Path not found within depth {max_depth}")
        if start: start.make_start()
        if end: end.make_end()
        visualizer.draw()
        return False


def ids(visualizer, grid, start, end):
    max_grid_depth = ROWS * ROWS # Use ROWS from constants
    for depth in range(max_grid_depth):
        if visualizer.stop_requested:
            print("IDS: Search stopped by user.")
            return False

        print(f"IDS: Trying depth {depth}")
        visualizer.clear_search_visualization(clear_only_search=True)
        start.make_start()
        end.make_end()
        visualizer.draw()
        # time.sleep(0.1)

        came_from = {}
        visited = set()

        found, came_from_result, stopped = dls_recursive(visualizer, start, end, depth, visited, came_from, start)

        visualizer.clear_search_visualization(clear_only_search=True, keep_current_algo_colors=True) # Clear cyan

        if stopped:
            print(f"IDS: Search stopped by user during depth {depth}.")
            return False

        if found:
            print(f"IDS: Path found at depth {depth}")
            reconstruct_path(came_from_result, end, visualizer.draw, start)
            end.make_end()
            start.make_start()
            return True

        visualizer.check_for_quit()

    print("IDS: Path not found (reached max possible depth)")
    return False