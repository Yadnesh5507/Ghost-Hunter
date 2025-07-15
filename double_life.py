import pygame
import random
import math
import sys
import cv2
import textwrap

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


        
class GhostHunterGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Double Life")
        self.clock = pygame.time.Clock()

        global ghost_image
        ghost_image = pygame.image.load("asian_ghost_girl.png").convert_alpha()
        
        # Hide default cursor and create custom crosshair
        pygame.mouse.set_visible(False)
        self.crosshair = Crosshair()
        
        # Game state
        self.ghosts = []
        self.in_main_menu = True
        self.high_score = 0
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
        self.game_mode = None
        self.in_endless_menu = False
        self.camera_clicks = 0
        self.camera_clicks = 0
        self.successful_ghost_hits = 0

        
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

    def fade_in(self):
        fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade.fill(BLACK)
        for alpha in range(0, 255, 10):
            self.screen.fill(BLACK)
            fade.set_alpha(alpha)
            self.screen.blit(fade, (0, 0))
            pygame.display.flip()
            pygame.time.wait(15)

    def show_story_intro(self):
        story_lines = [
            "My name is Damien Hollow.I used to be a detective... a good one,I think.I lived with my wife and daughter in a isolated apartment building—just the three of us.",
            "There’s something wrong with me.Every day, after 6 PM,I lose all memory of what happens by the time I wake up at 6 AM.",
            "One night, my wife disappeared.I searched everywhere but told no one,not even my own daughter.I didn't wanted her to feel sorrow for it.",
            "A week later,I came back home from my search operation and saw my daughter dying in front of my home.I found her lying at the foot of the stairs bleeding.Before I could call for help,I blacked out again.",
            "He woke up at 6 AM,her body was cold.I decided to bury her in a forest nearby cause I didn't wanted anyone to know about her death.",
            "I isolated myself from the society,I had no hope left,it felt like I was just a dead body but alive,until that day...",
            "I thought there is no hope in living and took a knife to free myself from this living hell,as I kept the knife on my wrist to slice it...",
            "The TV in the room suddenly turned on,as my eyes gazed upon it,I saw her...,my daughter... she was on the screen,as I took a closer look,I noticed her head was bleeding just like that day...",
            "Before I could say anything,my digital camera fell into my hand,as I removed it's lens cap to look through the camera I saw my daughter inside my room...",
            "And then suddenly,the old radio in my room started playing an ad:'This camera can release trapped souls to the afterlife.Click 20 pictures of the ghost through this camera and set her free'.",
            "Now,it's my responsibility to free her soul to afterlife and then join her."
        ]

        self.screen.fill(BLACK)
        pygame.mouse.set_visible(True)
        
        for paragraph in story_lines:
            self.fade_in()
            
            
            wrapped_lines = textwrap.wrap(paragraph, width=60)  
            
            waiting = True
            while waiting:
                self.screen.fill(BLACK)

                
                for i, line in enumerate(wrapped_lines):
                    text = self.font_medium.render(line, True, WHITE)
                    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + i * 40))
                    self.screen.blit(text, text_rect)

                continue_text = self.font_small.render("Press any key to continue...", True, GRAY)
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + len(wrapped_lines)*40))
                self.screen.blit(continue_text, continue_rect)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False

            
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
                if event.button == 1:  
                    mouse_pos = pygame.mouse.get_pos()

                    if self.in_main_menu:
                        if self.story_button_rect.collidepoint(mouse_pos):
                            self.in_main_menu = False
                            self.in_endless_menu = False
                            self.story_mode = True
                            self.show_story_intro()
                            self.restart_game()
                        elif self.endless_button_rect.collidepoint(mouse_pos):
                            self.in_main_menu = False
                            self.in_endless_menu = True

                    elif self.in_endless_menu:
                        if self.start_button_rect.collidepoint(mouse_pos):
                            self.in_endless_menu = False
                            self.story_mode = False  # This means endless mode
                            self.restart_game()
                        elif self.back_button_rect.collidepoint(mouse_pos):
                            self.in_endless_menu = False
                            self.in_main_menu = True

                    elif self.game_over:
                        if self.menu_button_rect.collidepoint(mouse_pos):
                            self.in_main_menu = True
                            self.game_over = False
                            if self.score > self.high_score:
                                self.high_score = self.score
                    elif not self.in_main_menu and not self.game_over:
                        self.shoot(mouse_pos)

        
        return True
    

    def shoot(self, mouse_pos):
        if self.story_mode:
            self.camera_clicks += 1
            pygame.mixer.Sound.play(click_sound)

            hit = False
            for ghost in self.ghosts[:]:
                if ghost.is_hit(mouse_pos):
                    self.ghosts.remove(ghost)
                    self.score += 10
                    self.successful_ghost_hits += 1
                    hit = True
                    break

            # Check for good ending condition at 20 successful hits
            if self.successful_ghost_hits >= 20 and not self.good_ending:
                self.good_ending = True
                self.game_over = True
                self.game_over_reason = "You freed your daughter's soul."

            # Stop after 20 successful hits
            if self.successful_ghost_hits >= 20:
                self.ghosts.clear()  # Remove remaining ghosts

        else:
            # Endless Mode shooting
            if self.ammo <= 0:
                pygame.mixer.Sound.play(game_over_sound)
                self.game_over = True
                return

            hit = False
            for ghost in self.ghosts[:]:
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
                        self.game_over_reason = "Your aim is bad."
                    elif self.score <= 300:
                        self.game_over_reason = "Your aim is decent."
                    else:
                        self.game_over_reason = "Your aim is good."
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

    def draw_main_menu(self):
        self.screen.fill((15, 15, 30))
        
        title = self.font_large.render("Double Life", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Creator name
        creator_text = self.font_medium.render("By: Yadnesh Mhatre", True, YELLOW)
        creator_rect = creator_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(creator_text, creator_rect)

        # Story Mode Button
        story_text = self.font_medium.render("Story Mode", True, BLACK)
        self.story_button_rect = pygame.Rect(0, 0, 200, 50)
        self.story_button_rect.center = (SCREEN_WIDTH // 2, 300)
        pygame.draw.rect(self.screen, GREEN, self.story_button_rect, border_radius=20)
        self.screen.blit(story_text, story_text.get_rect(center=self.story_button_rect.center))

        # Endless Mode Button
        endless_text = self.font_medium.render("Endless Mode", True, BLACK)
        self.endless_button_rect = pygame.Rect(0, 0, 200, 50)
        self.endless_button_rect.center = (SCREEN_WIDTH // 2, 380)
        pygame.draw.rect(self.screen, GRAY, self.endless_button_rect, border_radius=20)
        self.screen.blit(endless_text, endless_text.get_rect(center=self.endless_button_rect.center))

        pygame.display.flip()

    def draw_endless_menu(self):
        self.screen.fill((20, 20, 35))

        title = self.font_large.render("Endless Mode", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        # High Score
        hs_text = self.font_medium.render(f"High Score: {self.high_score}", True, YELLOW)
        self.screen.blit(hs_text, hs_text.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        # Start Button
        start_text = self.font_medium.render("Start Endless", True, BLACK)
        self.start_button_rect = pygame.Rect(0, 0, 200, 50)
        self.start_button_rect.center = (SCREEN_WIDTH // 2, 300)
        pygame.draw.rect(self.screen, GREEN, self.start_button_rect, border_radius=20)
        self.screen.blit(start_text, start_text.get_rect(center=self.start_button_rect.center))

        # Back Button
        back_text = self.font_small.render("Back to Main Menu", True, BLACK)
        self.back_button_rect = pygame.Rect(0, 0, 200, 40)
        self.back_button_rect.center = (SCREEN_WIDTH // 2, 400)
        pygame.draw.rect(self.screen, GRAY, self.back_button_rect, border_radius=20)
        self.screen.blit(back_text, back_text.get_rect(center=self.back_button_rect.center))

        pygame.display.flip()

    
    def draw(self):
        if self.in_endless_menu:
            pygame.mouse.set_visible(True)
            self.draw_endless_menu()
            return

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
        if self.story_mode:
            self.draw_story_ui()
        else:
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

    def draw_story_ui(self):
        camera_text = self.font_medium.render(f"Camera: {self.camera_clicks}/30", True, WHITE)
        self.screen.blit(camera_text, (10, 10))

    def show_good_ending(self):
        lines = [
            "My name is Damien Hollow.I used to be a detective... a good one,I think.I lived with my wife and daughter in a isolated apartment building—just the three of us.",
            "There’s something wrong with me.Every day, after 6 PM,I lose all memory of what happens by the time I wake up at 6 AM.",
            "One night, my wife disappeared.I searched everywhere but told no one,not even my own daughter.I didn't wanted her to feel sorrow for it.",
            "A week later,I came back home from my search operation and saw my daughter dying in front of my home.I found her lying at the foot of the stairs bleeding.Before I could call for help,I blacked out again.",
            "He woke up at 6 AM,her body was cold.I decided to bury her in a forest nearby cause I didn't wanted anyone to know about her death.",
            "I isolated myself from the society,I had no hope left,it felt like I was just a dead body but alive,until that day...",
            "I thought there is no hope in living and took a knife to free myself from this living hell,as I kept the knife on my wrist to slice it...",
            "The TV in the room suddenly turned on,as my eyes gazed upon it,I saw her...,my daughter... she was on the screen,as I took a closer look,I noticed her head was bleeding just like that day...",
            "Before I could say anything,my digital camera fell into my hand,as I removed it's lens cap to look through the camera I saw my daughter inside my room...",
            "And then suddenly,the old radio in my room started playing an ad:'This camera can release trapped souls to the afterlife.Click 20 pictures of the ghost through this camera and set her free'.",
            "Now,it's my responsibility to free her soul to afterlife and then join her."
        ]

        self.screen.fill(BLACK)
        pygame.mouse.set_visible(True)
        
        for paragraph in lines:
            self.fade_in()
            
            
            wrapped_lines = textwrap.wrap(paragraph, width=60)  
            
            waiting = True
            while waiting:
                self.screen.fill(BLACK)

                
                for i, line in enumerate(wrapped_lines):
                    text = self.font_medium.render(line, True, WHITE)
                    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + i * 40))
                    self.screen.blit(text, text_rect)

                continue_text = self.font_small.render("Press any key to continue...", True, GRAY)
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + len(wrapped_lines)*40))
                self.screen.blit(continue_text, continue_rect)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                        waiting = False

    
    def draw_ui(self):
        # Ammo counter
        ammo_text = self.font_medium.render(f"Ammo: {self.ammo}", True, WHITE)
        self.screen.blit(ammo_text, (10, 10))
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 50))
        
        # Ammo Bullets
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

