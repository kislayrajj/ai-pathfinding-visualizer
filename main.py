import pygame
import sys
from visualizer import PathfindingVisualizer
from constants import WIDTH, ROWS 

# --- Run the Application ---
if __name__ == "__main__":
    # Initialize Pygame first
    pygame.init()

    # Set up the display window
    WIN = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("AI Pathfinding Algorithms Visualization")

    # Create and run the visualizer
    visualizer_app = PathfindingVisualizer(WIN, WIDTH, ROWS)
    visualizer_app.main_loop() # Start the main event loop
