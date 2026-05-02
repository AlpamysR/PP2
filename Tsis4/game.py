import pygame
import random
from config import *
from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class FoodType(Enum):
    NORMAL = 1
    POISON = 2
    POWERUP_SPEED = 3
    POWERUP_SLOW = 4
    POWERUP_SHIELD = 5

class PowerUp:
    def __init__(self, power_type, position, spawn_time):
        self.type = power_type
        self.position = position
        self.spawn_time = spawn_time
        
class Snake:
    def __init__(self, settings):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.grow_count = 0
        self.speed = INITIAL_SPEED
        self.shield_active = False
        self.speed_boost_end = 0
        self.slow_motion_end = 0
        self.color = tuple(settings.get('snake_color', GREEN))
        
    def move(self):
        head = self.positions[0]
        x, y = head
        
        if self.direction == Direction.UP:
            y -= 1
        elif self.direction == Direction.DOWN:
            y += 1
        elif self.direction == Direction.LEFT:
            x -= 1
        elif self.direction == Direction.RIGHT:
            x += 1
            
        new_head = (x, y)
        self.positions.insert(0, new_head)
        
        if self.grow_count > 0:
            self.grow_count -= 1
        else:
            self.positions.pop()
            
    def grow(self, amount=1):
        self.grow_count += amount
        
    def shrink(self, amount=2):
        for _ in range(amount):
            if len(self.positions) > 1:
                self.positions.pop()
                
    def check_collision(self, obstacles=[]):
        head = self.positions[0]
        
        # Wall collision
        if (head[0] < 0 or head[0] >= GRID_WIDTH or 
            head[1] < 0 or head[1] >= GRID_HEIGHT):
            if self.shield_active:
                self.shield_active = False
                return False
            return True
            
        # Self collision
        if head in self.positions[1:]:
            if self.shield_active:
                self.shield_active = False
                return False
            return True
            
        # Obstacle collision
        if head in obstacles:
            if self.shield_active:
                self.shield_active = False
                return False
            return True
            
        return False

class Game:
    def __init__(self, settings):
        self.settings = settings
        self.snake = Snake(settings)
        self.foods = []
        self.powerups = []
        self.obstacles = []
        self.score = 0
        self.level = 1
        self.game_over = False
        self.current_powerup = None
        self.powerup_spawn_time = 0
        
        # Generate initial food
        self.spawn_food()
        
    def spawn_food(self):
        """Spawn food items"""
        # Spawn normal food
        if len([f for f in self.foods if f[1] == FoodType.NORMAL]) < 3:
            pos = self.get_random_position()
            if pos:
                # Weight system for different food types
                food_type = random.choices(
                    [FoodType.NORMAL],
                    weights=[1.0]
                )[0]
                self.foods.append((pos, food_type))
                
        # Spawn poison food (20% chance)
        if random.random() < 0.2 and len([f for f in self.foods if f[1] == FoodType.POISON]) < 1:
            pos = self.get_random_position()
            if pos:
                self.foods.append((pos, FoodType.POISON))
                
    def spawn_powerup(self):
        """Spawn a power-up if none exists"""
        if self.current_powerup is None:
            power_types = [FoodType.POWERUP_SPEED, FoodType.POWERUP_SLOW, FoodType.POWERUP_SHIELD]
            power_type = random.choice(power_types)
            pos = self.get_random_position()
            if pos:
                self.current_powerup = PowerUp(power_type, pos, pygame.time.get_ticks())
                
    def get_random_position(self):
        """Get random position not occupied by snake, obstacles, or other items"""
        attempts = 0
        while attempts < 100:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            pos = (x, y)
            
            # Check if position is free
            if (pos not in self.snake.positions and 
                pos not in self.obstacles and
                pos not in [f[0] for f in self.foods] and
                (self.current_powerup is None or pos != self.current_powerup.position)):
                
                # Check if position doesn't trap the snake
                if self.is_position_safe(pos):
                    return pos
            attempts += 1
        return None
        
    def is_position_safe(self, pos):
        """Ensure spawn position doesn't surround the snake"""
        x, y = pos
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        snake_head = self.snake.positions[0]
        # Check if at least one neighbor is free
        for neighbor in neighbors:
            if (0 <= neighbor[0] < GRID_WIDTH and 
                0 <= neighbor[1] < GRID_HEIGHT and 
                neighbor not in self.obstacles):
                return True
        return False
        
    def spawn_obstacles(self):
        """Spawn obstacles starting from level 3"""
        if self.level >= 3:
            num_obstacles = (self.level - 2) * 2  # Increases with level
            self.obstacles = []
            
            attempts = 0
            while len(self.obstacles) < num_obstacles and attempts < 200:
                pos = self.get_random_position()
                if pos:
                    # Don't place obstacles right next to snake head
                    head = self.snake.positions[0]
                    if abs(pos[0] - head[0]) > 2 or abs(pos[1] - head[1]) > 2:
                        self.obstacles.append(pos)
                attempts += 1
                
    def update(self):
        """Update game state"""
        current_time = pygame.time.get_ticks()
        
        # Check power-up effects
        if self.snake.speed_boost_end > 0 and current_time > self.snake.speed_boost_end:
            self.snake.speed = INITIAL_SPEED
            self.snake.speed_boost_end = 0
            
        if self.snake.slow_motion_end > 0 and current_time > self.snake.slow_motion_end:
            self.snake.speed = INITIAL_SPEED
            self.snake.slow_motion_end = 0
            
        # Check if power-up should disappear
        if (self.current_powerup and 
            current_time - self.current_powerup.spawn_time > POWERUP_SPAWN_TIME):
            self.current_powerup = None
            
        # Move snake
        self.snake.move()
        
        # Check snake head position for food/power-up collection
        head = self.snake.positions[0]
        
        # Check food collection
        for food in self.foods[:]:
            if food[0] == head:
                if food[1] == FoodType.NORMAL:
                    self.score += 10
                    self.snake.grow()
                elif food[1] == FoodType.POISON:
                    self.snake.shrink(2)
                    if len(self.snake.positions) <= 1:
                        self.game_over = True
                self.foods.remove(food)
                
        # Check power-up collection
        if self.current_powerup and self.current_powerup.position == head:
            if self.current_powerup.type == FoodType.POWERUP_SPEED:
                self.snake.speed = int(INITIAL_SPEED * SPEED_BOOST_MULTIPLIER)
                self.snake.speed_boost_end = current_time + POWERUP_DURATION
            elif self.current_powerup.type == FoodType.POWERUP_SLOW:
                self.snake.speed = int(INITIAL_SPEED * SLOW_MOTION_MULTIPLIER)
                self.snake.slow_motion_end = current_time + POWERUP_DURATION
            elif self.current_powerup.type == FoodType.POWERUP_SHIELD:
                self.snake.shield_active = True
            self.current_powerup = None
            
        # Check collision
        if self.snake.check_collision(self.obstacles):
            self.game_over = True
            
        # Level progression
        new_level = (self.score // 50) + 1
        if new_level > self.level:
            self.level = new_level
            self.spawn_obstacles()
            
        # Spawn new items
        self.spawn_food()
        if random.random() < 0.01:  # 1% chance each frame
            self.spawn_powerup()
            
    def handle_input(self, event):
        """Handle player input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.snake.direction != Direction.DOWN:
                self.snake.direction = Direction.UP
            elif event.key == pygame.K_DOWN and self.snake.direction != Direction.UP:
                self.snake.direction = Direction.DOWN
            elif event.key == pygame.K_LEFT and self.snake.direction != Direction.RIGHT:
                self.snake.direction = Direction.LEFT
            elif event.key == pygame.K_RIGHT and self.snake.direction != Direction.LEFT:
                self.snake.direction = Direction.RIGHT