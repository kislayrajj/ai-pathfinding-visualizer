# --- Configuration ---
WIDTH = 700
ROWS = 50
DEFAULT_MAX_DEPTH_LDS = ROWS * 1 # Default, can be overridden by user input

# --- Colors ---
RED = (255, 0, 0)       # Closed Set
GREEN = (0, 255, 0)     # Open Set
BLUE = (64, 224, 208)   # End Node (Turquoise)
YELLOW = (255, 255, 0)  # Input Box Background
WHITE = (255, 255, 255) # Default / Reset
BLACK = (0, 0, 0)       # Barrier / Text
PURPLE = (128, 0, 128)  # Path
GREY = (128, 128, 128)  # Grid Lines
TURQUOISE = (64, 224, 208) # End Node
ORANGE = (255, 165, 0)  # Start Node
CYAN = (0, 255, 255)    # Current node in DFS/IDS/LDS
LIGHT_GREY = (211, 211, 211) # Background for help/input box