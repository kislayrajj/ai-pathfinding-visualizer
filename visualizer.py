# visualizer.py

import pygame
import sys
import time  
from node import Node
from constants import *  #
import algorithms 
# Increase recursion depth limit
try:
    sys.setrecursionlimit(2500)
except Exception as e:
    print(f"Could not set recursion depth limit: {e}")


class PathfindingVisualizer:
    """
    Manages the Pygame window, grid, user interactions, state,
    and orchestrates the pathfinding algorithm visualization.
    """

    def __init__(self, window, width, rows):
        pygame.font.init()
        self.win_surface = window  # Store the display surface reference
        self.width = width
        self.height = width
        self.rows = rows

        self.gap = self.width // self.rows
        self.grid = self._make_grid()

        self.start_node = None
        self.end_node = None

        # State flags
        self.algorithm_running = False
        self.stop_requested = False
        self.run_flag = True
        self.is_fullscreen = False  # Fullscreen state

        # --- Result Pop-up State ---
        self.show_result_popup = False
        self.result_message = ""
        # ---------------------------

        # UI State
        self.algorithm_name = "None"
        self.show_help = True

        # DLS Input State
        self.input_mode_active = False
        self.input_prompt = ""
        self.input_string = ""
        self.input_target_func = None
        self.current_max_depth_lds = DEFAULT_MAX_DEPTH_LDS

        # Fonts
        try:
            self.font_small = pygame.font.SysFont("consolas", 16)
            self.font_medium = pygame.font.SysFont("consolas", 20)
            self.font_large = pygame.font.SysFont(
                "consolas", 28)  # Font for popup message
        except pygame.error as e:
            print(
                f"Warning: Could not load system font 'consolas'. Using default font. Error: {e}")
            self.font_small = pygame.font.Font(None, 18)
            self.font_medium = pygame.font.Font(None, 22)
            self.font_large = pygame.font.Font(None, 32)

    def _make_grid(self):
        """Creates the 2D list representing the grid of Node objects."""
        grid = []
        for i in range(self.rows):
            grid.append([])
            for j in range(self.rows):
                node = Node(i, j, self.gap, self.rows)
                grid[i].append(node)
        return grid

    def _draw_grid_lines(self):
        """Draws the light grey lines separating grid cells."""
        for i in range(self.rows + 1):
            pygame.draw.line(self.win_surface, GREY,
                             (0, i * self.gap), (self.width, i * self.gap))
            pygame.draw.line(self.win_surface, GREY,
                             (i * self.gap, 0), (i * self.gap, self.height))

    def _get_clicked_pos(self, pos):
        """Converts pixel coordinates (mouse position) to grid row and column."""
        y, x = pos
        # Adjust for potential scaling/offset in fullscreen if necessary (simple version assumes direct mapping)
        row = y // self.gap
        col = x // self.gap
        row = max(0, min(self.rows - 1, row))
        col = max(0, min(self.rows - 1, col))
        return row, col

    def draw(self):
        """Main drawing function, called each frame."""
        # Use self.win_surface for all drawing
        self.win_surface.fill(WHITE)

        for row in self.grid:
            for node in row:
                node.draw(self.win_surface)

        self._draw_grid_lines()

        # UI Text
        algo_text = self.font_medium.render(
            f"Algorithm: {self.algorithm_name}", True, BLACK)
        self.win_surface.blit(algo_text, (10, 10))

        status_text_content = ""
        status_color = BLACK
        if self.algorithm_running:
            status_text_content = "Status: Running..."
            status_color = GREEN
        # Show "Stopped" only if stop was requested but popup isn't shown yet
        elif self.stop_requested and not self.show_result_popup:
            status_text_content = "Status: Stopped"
            status_color = RED

        if status_text_content:
            status_text = self.font_medium.render(
                status_text_content, True, status_color)
            status_text_rect = status_text.get_rect(
                topright=(self.width - 10, 10))
            self.win_surface.blit(status_text, status_text_rect)

        if self.show_help:
            self._draw_help_box()

        if self.input_mode_active:
            self._draw_input_box()

        # --- Draw Result Pop-up LAST (on top) ---
        if self.show_result_popup:
            self._draw_result_popup()
        # -----------------------------------------

        pygame.display.update()  # Update the display

    def _draw_help_box(self):
        """Draws the semi-transparent help overlay."""
        box_width = 480
        box_height = 380
        win_w, win_h = self.win_surface.get_size()
        box_x = (win_w - box_width) // 2
        box_y = (win_h - box_height) // 2

        help_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        help_surface.fill((240, 240, 240, 220))
        pygame.draw.rect(help_surface, BLACK, help_surface.get_rect(), 1)

        help_text = [
            "Controls:",
            " LClick: Place Start(1st), End(2nd), Barriers",
            " RClick: Erase Node",
            "--- Algorithms (Require Start & End) ---",
            " SPACE: A* Search",
            " D: Dijkstra / UCS",
            " B: Breadth-First Search (BFS)",
            " F: Depth-First Search (DFS)",
            " I: Iterative Deepening (IDS)",
            f" L: Limited Depth Search (LDS - Cur:{self.current_max_depth_lds})",
            " K: Hill Climbing (Greedy Best-First)",
            "--- Control ---",
            " C: Clear All (Grid, Start, End)",
            " R: Reset Search (Keep Grid, Start, End)",
            " S: Stop Current Search",
            " F11: Toggle Fullscreen",  # Added Fullscreen toggle help
            " H: Toggle Help (This Box)",
            " ESC: Quit Program / Close Pop-up",  # Added ESC for pop-up
        ]
        line_height = 18
        for i, line in enumerate(help_text):
            label = self.font_small.render(line, True, BLACK)
            help_surface.blit(label, (10, 5 + line_height * i))

        self.win_surface.blit(help_surface, (box_x, box_y))

    def _draw_input_box(self):
        """Draws the input box for DLS depth."""
        box_width = 300
        box_height = 100
        win_w, win_h = self.win_surface.get_size()
        box_x = (win_w - box_width) // 2
        box_y = (win_h - box_height) // 2

        # Draw on the main window surface (self.win_surface)
        pygame.draw.rect(self.win_surface, LIGHT_GREY,
                         (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.win_surface, BLACK,
                         (box_x, box_y, box_width, box_height), 2)
        prompt_text = self.font_medium.render(self.input_prompt, True, BLACK)
        prompt_rect = prompt_text.get_rect(
            center=(box_x + box_width // 2, box_y + 30))
        self.win_surface.blit(prompt_text, prompt_rect)
        input_surface = self.font_medium.render(self.input_string, True, BLACK)
        input_rect = input_surface.get_rect(
            center=(box_x + box_width // 2, box_y + 70))
        self.win_surface.blit(input_surface, input_rect)
        if time.time() % 1 < 0.5:
            cursor_x = input_rect.right + 2
            cursor_y = input_rect.top
            cursor_height = input_rect.height
            pygame.draw.line(self.win_surface, BLACK, (cursor_x,
                             cursor_y), (cursor_x, cursor_y + cursor_height), 2)

    def _draw_result_popup(self):
        """Draws the pop-up box showing the search result."""
        box_width = 400
        box_height = 150
        win_w, win_h = self.win_surface.get_size()
        box_x = (win_w - box_width) // 2
        box_y = (win_h - box_height) // 2

        # Create a surface for the popup
        popup_surface = pygame.Surface((box_width, box_height))
        popup_surface.fill(LIGHT_GREY)  # Solid background
        pygame.draw.rect(popup_surface, BLACK,
                         popup_surface.get_rect(), 3)  # Thicker border

        # Render the main result message
        message_text = self.font_large.render(self.result_message, True, BLACK)
        message_rect = message_text.get_rect(
            center=(box_width // 2, box_height // 2 - 20))
        popup_surface.blit(message_text, message_rect)

        # Render dismiss instruction
        dismiss_text = self.font_small.render("Press ESC to close", True, GREY)
        dismiss_rect = dismiss_text.get_rect(
            center=(box_width // 2, box_height // 2 + 30))
        popup_surface.blit(dismiss_text, dismiss_rect)

        # Blit the popup onto the main window surface
        self.win_surface.blit(popup_surface, (box_x, box_y))

    def _handle_input(self, event):
        """Handles keyboard events when the DLS input box is active."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                if self.input_string.isdigit():
                    value = int(self.input_string)
                    self.input_mode_active = False
                    if self.input_target_func:
                        self.input_target_func(value)
                    self.input_string = ""
                    self.input_target_func = None
                else:
                    print("Invalid input. Please enter a number.")
                    self.input_string = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_string = self.input_string[:-1]
            elif event.unicode.isdigit():
                if len(self.input_string) < 4:
                    self.input_string += event.unicode
            elif event.key == pygame.K_ESCAPE:  # Escape also cancels input
                print("Input cancelled.")
                self.input_mode_active = False
                self.input_string = ""
                self.input_target_func = None

    def clear_all(self):
        """Resets the entire grid, start/end nodes, and algorithm state."""
        print("Clearing grid, start, end nodes.")
        self.start_node = None
        self.end_node = None
        self.grid = self._make_grid()
        self.algorithm_name = "None"
        self.algorithm_running = False
        self.stop_requested = False
        self.show_result_popup = False  # Hide popup on clear
        self.result_message = ""

    def clear_search_visualization(self, clear_only_search=False, keep_current_algo_colors=False):
        """Resets node colors related to search."""
        print("Clearing search visualization...")
        for row in self.grid:
            for node in row:
                is_special = node.is_start() or node.is_end() or node.is_barrier()
                is_search_color = node.is_open() or node.is_closed(
                ) or node.is_path() or node.is_current()
                if is_search_color:
                    node.reset()
                elif clear_only_search and is_special:
                    pass
                elif not clear_only_search and not is_special:
                    node.reset()
        if keep_current_algo_colors:
            for row in self.grid:
                for node in row:
                    if node.is_current():
                        node.make_closed()
        if self.start_node:
            self.start_node.make_start()
        if self.end_node:
            self.end_node.make_end()
        self.algorithm_name = "None"  # Reset algo name only if clearing search
        self.algorithm_running = False
        # Do not reset stop_requested or popup flags here

    def start_algorithm(self, algo_func_name, display_name, *args):
        """Prepares and runs the selected pathfinding algorithm."""
        if not self.start_node or not self.end_node:
            print("Error: Please place both Start and End nodes first.")
            return
        try:
            algo_func = getattr(algorithms, algo_func_name)
        except AttributeError:
            print(f"Error: Algorithm function '{algo_func_name}' not found.")
            return

        self.clear_search_visualization(clear_only_search=True)
        self.show_result_popup = False  # Ensure no old popup lingers
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid)

        self.algorithm_name = display_name
        print(f"Starting {self.algorithm_name}...")
        self.algorithm_running = True
        self.stop_requested = False
        found = algo_func(self, self.grid, self.start_node,
                          self.end_node, *args)
        self.algorithm_running = False

        # --- Set Result Message and Show Pop-up ---
        if self.stop_requested:
            print(f"{self.algorithm_name} Stopped.")
            self.result_message = "Search Stopped!"
            self.clear_search_visualization(
                clear_only_search=True, keep_current_algo_colors=True)
        elif found:
            print(f"{self.algorithm_name} Finished: Path found.")
            self.result_message = "Path Found!"
        else:
            print(f"{self.algorithm_name} Finished: Path not found.")
            self.result_message = "Path Not Found"
        self.show_result_popup = True
        # -----------------------------------------

    def start_lds_with_input(self, depth):
        """Callback function called after user enters depth for LDS."""
        if depth > 0:
            self.current_max_depth_lds = depth
            algo_display_name = f"Limited Depth (LDS - Depth {depth})"
            self.start_algorithm('lds', algo_display_name,
                                 self.current_max_depth_lds)
        else:
            print("Invalid depth entered for LDS (must be > 0).")

    def check_for_quit(self):
        """Helper method called by algorithms to allow quitting."""
        for event in pygame.event.get(eventtype=pygame.QUIT):
            print("Quit event detected during algorithm execution.")
            self.stop_requested = True
            self.run_flag = False

    def toggle_fullscreen(self):
        """Toggles the display between windowed and fullscreen mode."""
        if self.is_fullscreen:
            # Switch back to windowed mode
            print("Switching to windowed mode.")
            self.win_surface = pygame.display.set_mode(
                (self.width, self.height))
            self.is_fullscreen = False
        else:
            # Switch to fullscreen mode
            print("Switching to fullscreen mode.")
            # Use current desktop resolution, or keep fixed size scaled
            # Using fixed size is simpler for consistent coordinates
            self.win_surface = pygame.display.set_mode(
                (self.width, self.height), pygame.FULLSCREEN)
            # Alternative: Use desktop resolution (might need coordinate adjustments)
            # self.win_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # self.width, self.height = self.win_surface.get_size() # Update internal size if using (0,0)
            # self.gap = self.width // self.rows # Recalculate gap if size changes
            self.is_fullscreen = True
        # Optional: Redraw immediately after mode switch
        self.draw()

    def main_loop(self):
        """The main event loop of the application."""
        clock = pygame.time.Clock()

        while self.run_flag:
            # --- Event Handling ---
            for event in pygame.event.get():
                # --- Always Handle Quit ---
                if event.type == pygame.QUIT:
                    self.run_flag = False
                    break  # Exit event loop immediately

                # --- Handle Pop-up Dismissal ---
                if self.show_result_popup:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.show_result_popup = False
                            self.result_message = ""
                            self.stop_requested = False  # Allow new actions after closing popup
                            print("Result pop-up closed.")
                    # Ignore other events while pop-up is shown
                    continue  # Go to next iteration, skipping other handlers

                # --- Handle Input Mode ---
                if self.input_mode_active:
                    self._handle_input(event)
                    continue  # Skip other events during input

                # --- Handle Mouse Input (only if not running/stopped/popup) ---
                if not self.algorithm_running and not self.stop_requested:
                    if pygame.mouse.get_pressed()[0]:  # Left Click
                        pos = pygame.mouse.get_pos()
                        row, col = self._get_clicked_pos(pos)
                        node = self.grid[row][col]
                        if not self.start_node and node != self.end_node:
                            self.start_node = node
                            self.start_node.make_start()
                        elif not self.end_node and node != self.start_node:
                            self.end_node = node
                            self.end_node.make_end()
                        elif node != self.start_node and node != self.end_node:
                            node.make_barrier()
                    elif pygame.mouse.get_pressed()[2]:  # Right Click
                        pos = pygame.mouse.get_pos()
                        row, col = self._get_clicked_pos(pos)
                        node = self.grid[row][col]
                        if node == self.start_node:
                            self.start_node = None
                        elif node == self.end_node:
                            self.end_node = None
                        node.reset()

                # --- Handle Keyboard Input ---
                if event.type == pygame.KEYDOWN:
                    # --- Always Active Keys ---
                    if event.key == pygame.K_ESCAPE:  # Escape quits if no popup/input active
                        self.run_flag = False
                        break
                    if event.key == pygame.K_h:
                        self.show_help = not self.show_help
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()  # Toggle fullscreen

                    # --- Keys active only when NOT running ---
                    if not self.algorithm_running:
                        if event.key == pygame.K_c:
                            self.clear_all()
                        if event.key == pygame.K_r:
                            self.clear_search_visualization(
                                clear_only_search=True)
                            self.stop_requested = False  # Allow new search

                        # Start Algorithms
                        if self.start_node and self.end_node:
                            if event.key == pygame.K_SPACE:
                                self.start_algorithm('a_star', "A* Search")
                            elif event.key == pygame.K_d:
                                self.start_algorithm(
                                    'dijkstra', "Dijkstra / UCS")
                            elif event.key == pygame.K_b:
                                self.start_algorithm(
                                    'bfs', "Breadth-First Search (BFS)")
                            elif event.key == pygame.K_f:
                                self.start_algorithm(
                                    'dfs', "Depth-First Search (DFS)")
                            elif event.key == pygame.K_i:
                                self.start_algorithm(
                                    'ids', "Iterative Deepening (IDS)")
                            elif event.key == pygame.K_k:
                                self.start_algorithm(
                                    'hill_climbing', "Hill Climbing")
                            elif event.key == pygame.K_l:
                                self.input_prompt = "Enter LDS Depth Limit:"
                                self.input_target_func = self.start_lds_with_input
                                self.input_mode_active = True
                                self.input_string = str(
                                    self.current_max_depth_lds)
                                print(
                                    f"Input requested for LDS Depth (current: {self.current_max_depth_lds}).")

                    # --- Stop Algorithm (only if running) ---
                    if self.algorithm_running and event.key == pygame.K_s:
                        print("Stop request received!")
                        self.stop_requested = True

            # Check run flag again before drawing, in case Quit was handled
            if not self.run_flag:
                break

            # --- Update Display ---
            self.draw()

            # --- Frame Rate Control ---
            clock.tick(60)

        # --- Exit Pygame ---
        print("Exiting Pygame...")
        pygame.quit()
        sys.exit()
