import pygame
import sys
import json
from config import *
from game import Game, FoodType
from db import Database

class Button:
    def __init__(self, x, y, width, height, text, color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class InputBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.font = pygame.font.Font(None, 32)
        self.color_inactive = GRAY
        self.color_active = WHITE
        self.color = self.color_inactive
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
                
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surface = self.font.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize database
        self.db = Database()
        self.db.connect()
        
        # Game state
        self.state = "menu"  # menu, username, playing, game_over, leaderboard, settings
        self.username = ""
        self.game = None
        self.personal_best = 0
        self.input_box = InputBox(250, 300, 300, 40)
        
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_settings = {
                'snake_color': [0, 255, 0],
                'grid_overlay': True,
                'sound': True
            }
            self.save_settings(default_settings)
            return default_settings
            
    def save_settings(self, settings):
        """Save settings to JSON file"""
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)
            
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if self.state == "username":
                    self.handle_username_input(event)
                elif self.state == "playing":
                    if self.game:
                        self.game.handle_input(event)
                elif self.state == "menu":
                    self.handle_menu_input(event)
                elif self.state == "game_over":
                    self.handle_game_over_input(event)
                elif self.state == "leaderboard":
                    self.handle_leaderboard_input(event)
                elif self.state == "settings":
                    self.handle_settings_input(event)
                    
            # Update game
            if self.state == "playing" and self.game:
                self.game.update()
                if self.game.game_over:
                    self.state = "game_over"
                    self.db.save_game_session(
                        self.username, 
                        self.game.score, 
                        self.game.level
                    )
                    
            # Draw
            self.draw()
            self.clock.tick(self.game.snake.speed if self.game else INITIAL_SPEED)
            
        self.db.close()
        pygame.quit()
        sys.exit()
        
    def draw(self):
        """Draw current screen based on game state"""
        self.screen.fill(BLACK)
        
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "username":
            self.draw_username_screen()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "leaderboard":
            self.draw_leaderboard()
        elif self.state == "settings":
            self.draw_settings()
            
        pygame.display.flip()
        
    def draw_menu(self):
        """Draw main menu"""
        title = self.font.render("SNAKE GAME", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        buttons = [
            Button(300, 200, 200, 50, "Play", BLACK),
            Button(300, 270, 200, 50, "Leaderboard", BLACK),
            Button(300, 340, 200, 50, "Settings", BLACK),
            Button(300, 410, 200, 50, "Quit", RED)
        ]
        
        for button in buttons:
            button.draw(self.screen)
            
        self.menu_buttons = buttons
        
    def draw_username_screen(self):
        """Draw username input screen"""
        prompt = self.font.render("Enter your username:", True, WHITE)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(prompt, prompt_rect)
        
        self.input_box.draw(self.screen)
        
        # Enter button
        enter_button = Button(350, 370, 100, 40, "Enter", GREEN)
        enter_button.draw(self.screen)
        self.enter_button = enter_button
        
    def draw_game(self):
        """Draw game screen"""
        if not self.game:
            return
            
        # Draw grid
        if self.settings.get('grid_overlay', True):
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
                
        # Draw obstacles
        for obstacle in self.game.obstacles:
            rect = pygame.Rect(
                obstacle[0] * GRID_SIZE,
                obstacle[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            pygame.draw.rect(self.screen, GRAY, rect)
            
        # Draw snake
        for i, pos in enumerate(self.game.snake.positions):
            rect = pygame.Rect(
                pos[0] * GRID_SIZE,
                pos[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            color = self.game.snake.color
            if i == 0 and self.game.snake.shield_active:
                color = YELLOW  # Shield indicator
            pygame.draw.rect(self.screen, color, rect)
            
        # Draw foods
        for food in self.game.foods:
            rect = pygame.Rect(
                food[0][0] * GRID_SIZE,
                food[0][1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            if food[1] == FoodType.NORMAL:
                pygame.draw.rect(self.screen, RED, rect)
            elif food[1] == FoodType.POISON:
                pygame.draw.rect(self.screen, DARK_GREEN, rect)
                
        # Draw power-up
        if self.game.current_powerup:
            rect = pygame.Rect(
                self.game.current_powerup.position[0] * GRID_SIZE,
                self.game.current_powerup.position[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            if self.game.current_powerup.type == FoodType.POWERUP_SPEED:
                pygame.draw.rect(self.screen, YELLOW, rect)
            elif self.game.current_powerup.type == FoodType.POWERUP_SLOW:
                pygame.draw.rect(self.screen, PURPLE, rect)
            elif self.game.current_powerup.type == FoodType.POWERUP_SHIELD:
                pygame.draw.rect(self.screen, ORANGE, rect)
                
        # Draw HUD
        score_text = self.font.render(f"Score: {self.game.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        level_text = self.font.render(f"Level: {self.game.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        pb_text = self.font.render(f"Best: {self.personal_best}", True, WHITE)
        self.screen.blit(pb_text, (SCREEN_WIDTH - 150, 10))
        
    def draw_game_over(self):
        """Draw game over screen"""
        title = self.font.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        if self.game:
            score_text = self.font.render(f"Final Score: {self.game.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(score_text, score_rect)
            
            level_text = self.font.render(f"Level Reached: {self.game.level}", True, WHITE)
            level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, 250))
            self.screen.blit(level_text, level_rect)
            
            pb = self.db.get_personal_best(self.username)
            pb_text = self.font.render(f"Personal Best: {pb}", True, YELLOW)
            pb_rect = pb_text.get_rect(center=(SCREEN_WIDTH//2, 300))
            self.screen.blit(pb_text, pb_rect)
            
        buttons = [
            Button(250, 400, 150, 50, "Retry", GREEN),
            Button(450, 400, 150, 50, "Main Menu", BLUE)
        ]
        
        for button in buttons:
            button.draw(self.screen)
            
        self.game_over_buttons = buttons
        
    def draw_leaderboard(self):
        """Draw leaderboard screen"""
        title = self.font.render("LEADERBOARD - TOP 10", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Column headers
        headers = ["Rank", "Username", "Score", "Level", "Date"]
        x_positions = [50, 150, 350, 500, 600]
        
        for header, x in zip(headers, x_positions):
            header_text = self.small_font.render(header, True, WHITE)
            self.screen.blit(header_text, (x, 100))
            
        # Fetch and display leaderboard data
        leaderboard = self.db.get_leaderboard()
        for i, row in enumerate(leaderboard):
            y = 150 + i * 40
            data = [str(i+1), row[0], str(row[1]), str(row[2]), str(row[3])[:10]]
            
            for d, x in zip(data, x_positions):
                data_text = self.small_font.render(d, True, WHITE)
                self.screen.blit(data_text, (x, y))
                
        # Back button
        back_button = Button(350, 550, 100, 40, "Back", BLUE)
        back_button.draw(self.screen)
        self.back_button = back_button
        
    def draw_settings(self):
        """Draw settings screen"""
        title = self.font.render("SETTINGS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)
        
        # Grid toggle
        grid_text = self.font.render(f"Grid Overlay: {'ON' if self.settings['grid_overlay'] else 'OFF'}", True, WHITE)
        self.screen.blit(grid_text, (200, 150))
        grid_button = Button(550, 145, 100, 30, "Toggle", GREEN)
        grid_button.draw(self.screen)
        
        # Sound toggle
        sound_text = self.font.render(f"Sound: {'ON' if self.settings['sound'] else 'OFF'}", True, WHITE)
        self.screen.blit(sound_text, (200, 220))
        sound_button = Button(550, 215, 100, 30, "Toggle", GREEN)
        sound_button.draw(self.screen)
        
        # Snake color
        color_text = self.font.render("Snake Color:", True, WHITE)
        self.screen.blit(color_text, (200, 290))
        
        colors = [("Green", GREEN), ("Red", RED), ("Blue", BLUE), ("Purple", PURPLE)]
        color_buttons = []
        for i, (name, color) in enumerate(colors):
            btn = Button(550 + i * 60, 285, 50, 40, "", color)
            btn.draw(self.screen)
            color_buttons.append((btn, list(color)))
            
        # Save & Back button
        save_button = Button(300, 400, 200, 50, "Save & Back", GREEN)
        save_button.draw(self.screen)
        
        self.settings_buttons = {
            'grid': grid_button,
            'sound': sound_button,
            'colors': color_buttons,
            'save': save_button
        }
        
    def handle_menu_input(self, event):
        """Handle menu screen input"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.menu_buttons:
                if button.is_clicked(mouse_pos):
                    if button.text == "Play":
                        self.state = "username"
                    elif button.text == "Leaderboard":
                        self.state = "leaderboard"
                    elif button.text == "Settings":
                        self.state = "settings"
                    elif button.text == "Quit":
                        self.db.close()
                        pygame.quit()
                        sys.exit()
                        
    def handle_username_input(self, event):
        """Handle username input screen"""
        self.input_box.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.enter_button.is_clicked(pygame.mouse.get_pos()):
                if self.input_box.text.strip():
                    self.username = self.input_box.text.strip()
                    self.personal_best = self.db.get_personal_best(self.username)
                    self.game = Game(self.settings)
                    self.state = "playing"
                    
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.input_box.text.strip():
                self.username = self.input_box.text.strip()
                self.personal_best = self.db.get_personal_best(self.username)
                self.game = Game(self.settings)
                self.state = "playing"
                
    def handle_game_over_input(self, event):
        """Handle game over screen input"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.game_over_buttons:
                if button.is_clicked(mouse_pos):
                    if button.text == "Retry":
                        self.game = Game(self.settings)
                        self.personal_best = self.db.get_personal_best(self.username)
                        self.state = "playing"
                    elif button.text == "Main Menu":
                        self.state = "menu"
                        
    def handle_leaderboard_input(self, event):
        """Handle leaderboard screen input"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(pygame.mouse.get_pos()):
                self.state = "menu"
                
    def handle_settings_input(self, event):
        """Handle settings screen input"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.settings_buttons['grid'].is_clicked(mouse_pos):
                self.settings['grid_overlay'] = not self.settings['grid_overlay']
            elif self.settings_buttons['sound'].is_clicked(mouse_pos):
                self.settings['sound'] = not self.settings['sound']
            elif self.settings_buttons['save'].is_clicked(mouse_pos):
                self.save_settings(self.settings)
                self.state = "menu"
            else:
                for btn, color in self.settings_buttons['colors']:
                    if btn.is_clicked(mouse_pos):
                        self.settings['snake_color'] = color

def main():
    game = SnakeGame()
    game.run()

if __name__ == "__main__":
    main()