import pygame
import random
import math
import sys
import cv2

# Initialize Pygame
pygame.init()
pygame.mixer.init()
click_sound = pygame.mixer.Sound("camera_sound.mp3")
game_over_sound = pygame.mixer.Sound("game_over.wav")
pygame.mixer.music.load("bg_sound.mp3")
pygame.mixer.music.play(-1) 


# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GHOST_MIN_TIME = 4000  # 2 seconds in milliseconds
GHOST_MAX_TIME = 7000  # 5 seconds in milliseconds
GHOST_SIZE = 100
CROSSHAIR_SIZE = 40
INITIAL_AMMO = 3
video = cv2.VideoCapture("horror_house_bg.mp4")


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

class Ghost:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(100,150)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = random.randint(GHOST_MIN_TIME, GHOST_MAX_TIME)
        
    def update(self):
        pass        
        
    def draw(self, screen):
        ghost_img = pygame.transform.scale(ghost_image, (self.size, self.size))
        screen.blit(ghost_img, (self.x - self.size // 2, self.y - self.size // 2))
    
    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime
    
    def is_hit(self, mouse_pos):
        distance = math.sqrt((self.x - mouse_pos[0])**2 + (self.y - mouse_pos[1])**2)

        return distance <= self.size // 2

class Crosshair:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("camera.png").convert_alpha(),(120,120))
        self.rect = self.image.get_rect()

    def draw(self, screen, pos):
        self.rect.center = pos
        screen.blit(self.image, self.rect)

def load_high_score():
    try:
        with open("highscore.txt", "r") as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    with open("highscore.txt", "w") as file:
        file.write(str(score))

        
class GhostHunterGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ghost Hunter")
        self.clock = pygame.time.Clock()

        global ghost_image
        ghost_image = pygame.image.load("ghost_snake.png").convert_alpha()
        
        # Hide default cursor and create custom crosshair
        pygame.mouse.set_visible(False)
        self.crosshair = Crosshair()
        
        # Game state
        self.ghosts = []
        self.in_main_menu = True
        self.high_score = load_high_score()
        self.ammo = INITIAL_AMMO
        self.score = 0
        self.game_over = False
        self.paused = False
        self.last_ghost_spawn = 0
        self.next_ghost_delay = random.randint(1000, 3000)# 1-3 seconds
        self.crosshair_x = SCREEN_WIDTH // 2
        self.crosshair_y = SCREEN_HEIGHT // 2
        self.crosshair_speed = 10
        self.escaped_ghosts = 0
        self.max_escaped_ghosts = 10
        self.flash_duration = 200  
        self.flash_start_time = None

        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
    def spawn_ghost(self):
        # Spawn ghost at random position (not too close to edges)
        margin = GHOST_SIZE
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin, SCREEN_HEIGHT - margin)
        self.ghosts.append(Ghost(x, y))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.shoot((self.crosshair_x, self.crosshair_y))

                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_p and not self.in_main_menu and not self.game_over:
                    self.paused = not self.paused
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()

                    if self.in_main_menu:
                        if self.start_button_rect.collidepoint(mouse_pos):
                            self.in_main_menu = False
                            self.restart_game()
                    elif self.game_over:
                        if self.menu_button_rect.collidepoint(mouse_pos):
                            self.in_main_menu = True
                            self.game_over = False
                            if self.score > self.high_score:
                                self.high_score = self.score
                                save_high_score(self.high_score)
                    elif not self.in_main_menu and not self.game_over:
                        self.shoot(mouse_pos)

        
        return True
    
    def shoot(self, mouse_pos):
        if self.ammo <= 0:
            pygame.mixer.Sound.play(game_over_sound)
            self.game_over = True
            
        hit = False
        for ghost in self.ghosts[:]:  # Create a copy to iterate safely
            if ghost.is_hit(mouse_pos):
                pygame.mixer.Sound.play(click_sound)
                self.ghosts.remove(ghost)
                self.score += 10
                hit = True
                break
        
        if not hit:
            pygame.mixer.Sound.play(click_sound)
            self.ammo -= 1
            if self.ammo <= 0:
                pygame.mixer.Sound.play(game_over_sound)
                if self.score < 100:
                    self.game_over_reason = "Your aim is bad"
                elif self.score < 300:
                    self.game_over_reason = "Your aim is decent"
                else:
                    self.game_over_reason = "Your aim is good"
                self.game_over = True
        
        self.flash_start_time = pygame.time.get_ticks()
        
    def update(self):
        if self.game_over or self.paused:
            return "Game over:Ran out of ammo"
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.crosshair_y -= self.crosshair_speed
        if keys[pygame.K_s]:
            self.crosshair_y += self.crosshair_speed
        if keys[pygame.K_a]:
            self.crosshair_x -= self.crosshair_speed
        if keys[pygame.K_d]:
            self.crosshair_x += self.crosshair_speed

        # Keep within screen bounds
        self.crosshair_x = max(0, min(self.crosshair_x, SCREEN_WIDTH))
        self.crosshair_y = max(0, min(self.crosshair_y, SCREEN_HEIGHT))

            
        current_time = pygame.time.get_ticks()
        
        # Spawn new ghosts
        if current_time - self.last_ghost_spawn > self.next_ghost_delay and len(self.ghosts) == 0:
            self.spawn_ghost()
            self.last_ghost_spawn = current_time
            self.next_ghost_delay = random.randint(1000, 3000)
        
        # Update existing ghosts
        for ghost in self.ghosts[:]:
            ghost.update()
            if ghost.is_expired():
                self.ghosts.remove(ghost)
                self.escaped_ghosts += 1  # Increment escaped counter
                if self.escaped_ghosts >= self.max_escaped_ghosts:
                    self.game_over_reason = "Too many ghosts escaped"
                    self.game_over = True
                    if self.score>self.high_score:
                        self.high_score=self.score
                        save_high_score(self.high_score)
                    
    def draw_main_menu(self):
        self.screen.fill((15, 15, 30))
        title = self.font_large.render("Ghost Hunter", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        #Creator name
        creator_text = self.font_medium.render("By:Yadnesh Mhatre",True,YELLOW)
        creator_rect = creator_text.get_rect(center=(SCREEN_WIDTH // 2,200))
        self.screen.blit(creator_text,creator_rect)
        
        # Start Button
        start_text = self.font_medium.render("Start Game", True, BLACK)
        self.start_button_rect = pygame.Rect(0, 0, 200, 50)
        self.start_button_rect.center = (SCREEN_WIDTH // 2, 300)
        pygame.draw.rect(self.screen, GREEN, self.start_button_rect,border_radius=20)
        self.screen.blit(start_text, start_text.get_rect(center=self.start_button_rect.center))

        # High Score
        hs_text = self.font_medium.render(f"High Score: {self.high_score}", True, YELLOW)
        hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(hs_text, hs_rect)


        pygame.display.flip()

    
    def draw(self):
        if self.in_main_menu:
            pygame.mouse.set_visible(True)
            self.draw_main_menu()
            return

        if self.game_over:
            pygame.mouse.set_visible(True)
            self.draw_game_over()
            pygame.display.flip()
            return
        
        pygame.mouse.set_visible(False)

        
        # Clear screen with dark background
        ret, frame = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video
            ret, frame = video.read()
        
        # Draw background pattern
        frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        self.screen.blit(frame_surface, (0, 0))

        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw crosshair (always on top)
        if not self.game_over:
            self.crosshair.draw(self.screen, (self.crosshair_x, self.crosshair_y))

        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()

        # Show pause overlay if paused
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            pause_text = self.font_large.render("Paused", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(pause_text, pause_rect)

            resume_text = self.font_small.render("Press 'P' to Resume", True, GRAY)
            resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
            self.screen.blit(resume_text, resume_rect)
            
        # Flash overlay
        if self.flash_start_time:
            elapsed = pygame.time.get_ticks() - self.flash_start_time
            if elapsed < self.flash_duration:
                alpha = 255 * (1 - elapsed / self.flash_duration)  # fade out
                flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash.fill((255, 255, 255, int(alpha)))
                self.screen.blit(flash, (0, 0))
            else:
                self.flash_start_time = None

        
        pygame.display.flip()
    
    def draw_ui(self):
        # Draw ammo counter
        ammo_text = self.font_medium.render(f"Ammo: {self.ammo}", True, WHITE)
        self.screen.blit(ammo_text, (10, 10))
        
        # Draw score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        # Draw ammo bullets visualization
        for i in range(INITIAL_AMMO):
            color = YELLOW if i < self.ammo else GRAY
            pygame.draw.circle(self.screen, color, (200 + i * 30, 25), 8)
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10))
        self.screen.blit(final_score_text, final_score_rect)

        # Reason for game over
        reason_text = self.font_small.render(self.game_over_reason, True, YELLOW)
        reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(reason_text, reason_rect)

        # Return to main menu
        menu_text = self.font_small.render("Main Menu", True, BLACK)
        self.menu_button_rect = pygame.Rect(0, 0, 200, 40)
        self.menu_button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
        pygame.draw.rect(self.screen, GREEN, self.menu_button_rect,border_radius=20)
        self.screen.blit(menu_text, menu_text.get_rect(center=self.menu_button_rect.center))
        
    
    def restart_game(self):
        if self.score>self.high_score:
            self.high_score=self.score
            save_high_score(self.high_score)
        self.ghosts.clear()
        self.ammo=INITIAL_AMMO
        self.score=0
        self.escaped_ghosts=0
        self.game_over=False
        self.last_ghost_spawn=0
        self.next_ghost_delay=random.randint(1000, 3000)
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        video.release()
        pygame.quit()
        sys.exit()

if __name__=="__main__":
    game=GhostHunterGame()
    game.run()

