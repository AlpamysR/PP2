# Game constants and configuration
import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GREEN= (0, 100, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)

# Game settings
INITIAL_SPEED = 5
SPEED_BOOST_MULTIPLIER = 1.5
SLOW_MOTION_MULTIPLIER = 0.5
POWERUP_DURATION = 5000  # 5 seconds in milliseconds
POWERUP_SPAWN_TIME = 8000  # 8 seconds before disappearing

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Database configuration
DB_CONFIG = {
    'dbname': 'Snake',
    'user': 'postgres',
    'password': '15022008',
    'host': 'localhost',
    'port': '5432'
}