import random
import pygame
import math
from pygame import mixer
import sys
import time

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders - Project')

player_img = pygame.image.load('images/player.png')
enemy_img = [
    pygame.image.load('images/enemy.png'),
    pygame.image.load('images/enemy2.png'),
    pygame.image.load('images/enemy3.png')
]
bullet_img = pygame.image.load('images/bullet.png')
enemy_bullet_img = pygame.image.load('images/enemy_bullet.png')
background = pygame.image.load('images/background.png').convert()
mixer.music.load('audio/background.wav')

playerX = 370
playerY = 480
playerX_change = 0
bulletX = 0
bulletY = 480
bullet_state = 'ready'
score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)
wave_number = 1
base_enemy_speed = 1.0
base_enemy_y_increment = 30
game_paused = False 

enemies = []
enemy_alive = []
enemy_bullets = []
last_shot_times = {}



def reset_game():
    global game_paused, playerX, playerY, playerX_change, bulletX, bulletY, bullet_state
    global score_value, wave_number, enemies, enemy_alive, enemy_bullets
    
    game_paused = False
    playerX = 370
    playerY = 480
    playerX_change = 0
    bulletX = 0
    bulletY = 480
    bullet_state = 'ready'
    score_value = 0
    wave_number = 1
    enemies = []
    enemy_alive = []
    enemy_bullets = []

def init_game():
    global enemies, enemy_alive, last_shot_times
    enemies = []
    enemy_alive = []
    last_shot_times = {}
    
    total_enemies = 6 + wave_number
    
    if wave_number < 4:
        type2_count = max(1, wave_number - 1)
        type1_count = total_enemies - type2_count
        
        for _ in range(type1_count):
            spawn_enemy(0)
        for _ in range(type2_count):
            spawn_enemy(1)
    else:
        type3_count = max(2, wave_number - 3)
        type2_count = total_enemies - type3_count
        
        for _ in range(type2_count):
            spawn_enemy(1)
        for _ in range(type3_count):
            spawn_enemy(2)

def spawn_enemy(enemy_type):
    current_speed = base_enemy_speed * (1 + 0.1 * (wave_number - 1))
    health = 1
    if enemy_type == 1:
        health = 2
    elif enemy_type == 2:
        health = 3
    
    enemies.append({
        "x": random.randint(0, 736),
        "y": random.randint(0, 150),
        "speed": current_speed,
        "direction": random.choice([-1, 1]),
        "type": enemy_type,
        "health": health,
        "max_health": health,
        "last_shot": time.time()
    })
    enemy_alive.append(True)

def handle_enemy_shooting():
    if game_paused:
        return
        
    current_time = time.time()
    for i, enemy in enumerate(enemies):
        if enemy_alive[i] and enemy["type"] == 2:
            if current_time - enemy["last_shot"] > 2:
                enemy_bullets.append({
                    "x": enemy["x"] + 16,
                    "y": enemy["y"] + 10,
                    "speed": 3
                })
                enemy["last_shot"] = current_time
                shot_sound = mixer.Sound('audio/enemy_laser.mp3')
                shot_sound.play()

def draw_health_bar(enemy):
    if enemy["max_health"] > 1:
        bar_width = 40
        bar_height = 5
        fill = (enemy["health"] / enemy["max_health"]) * bar_width
        outline_rect = pygame.Rect(enemy["x"], enemy["y"] - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(enemy["x"], enemy["y"] - 10, fill, bar_height)
        pygame.draw.rect(screen, (255,0,0), fill_rect)
        pygame.draw.rect(screen, (255,255,255), outline_rect, 1)

def show_score():
    score = font.render(f'Score: {score_value} | Wave: {wave_number}', True, (255,255,255))
    screen.blit(score, (10, 10))

def game_over():
    over_font = pygame.font.Font('freesansbold.ttf', 64)
    over_text = over_font.render('GAME OVER!', True, (255, 255, 255))
    screen.blit(over_text, (200, 250))
    
    pygame.display.update()
    start_time = time.time()
    while time.time() - start_time < 2:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def draw_pause_menu():
    btn_font = pygame.font.Font('freesansbold.ttf', 32)
    buttons = [
        {"rect": pygame.Rect(300, 300, 200, 50), "color": (0,200,0), "text": "Resume"},
        {"rect": pygame.Rect(300, 380, 200, 50), "color": (0,0,200), "text": "Main Menu"}
    ]
    
    s = pygame.Surface((800,600), pygame.SRCALPHA)
    s.fill((0,0,0,128))
    screen.blit(s, (0,0))
    
    pause_font = pygame.font.Font('freesansbold.ttf', 64)
    pause_text = pause_font.render('PAUSED', True, (255,255,255))
    screen.blit(pause_text, (300, 200))
    
    for btn in buttons:
        pygame.draw.rect(screen, btn["color"], btn["rect"])
        text_surface = btn_font.render(btn["text"], True, (255,255,255))
        text_width = text_surface.get_width()
        text_x = btn["rect"].x + (btn["rect"].width - text_width) // 2
        text_y = btn["rect"].y + 10
        screen.blit(text_surface, (text_x, text_y))
    
    pygame.display.update()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if buttons[0]["rect"].collidepoint(mouse_pos):
                    return "resume"
                elif buttons[1]["rect"].collidepoint(mouse_pos):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"

def victory_screen():
    btn_font = pygame.font.Font('freesansbold.ttf', 32)
    buttons = [
        {"rect": pygame.Rect(300, 300, 200, 50), "color": (0,200,0), "text": "Restart"},
        {"rect": pygame.Rect(300, 380, 200, 50), "color": (0,0,200), "text": "Next Wave"}
    ]
    
    while True:
        screen.fill((0,0,0))
        victory_text = font.render(f'WAVE {wave_number} CLEARED!', True, (0,255,0))
        screen.blit(victory_text, (250, 200))
        
        for btn in buttons:
            pygame.draw.rect(screen, btn["color"], btn["rect"])
            text_surface = btn_font.render(btn["text"], True, (255,255,255))
            text_width = text_surface.get_width()
            text_x = btn["rect"].x + (btn["rect"].width - text_width) // 2
            text_y = btn["rect"].y + 10
            screen.blit(text_surface, (text_x, text_y))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if buttons[0]["rect"].collidepoint(mouse_pos): 
                    return "restart"
                elif buttons[1]["rect"].collidepoint(mouse_pos):
                    return "next"

def game_loop():
    global game_paused, playerX, playerY, playerX_change, bulletX, bulletY, bullet_state
    global score_value, wave_number, base_enemy_speed, base_enemy_y_increment, enemy_bullets
    
    init_game()
    mixer.music.play(-1)
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(60)
        screen.fill((0,0,0))
        screen.blit(background, (0,0)) 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_paused = not game_paused
                    if game_paused:
                        mixer.music.pause()
                    else:
                        mixer.music.unpause()
                
                if not game_paused:
                    if event.key == pygame.K_LEFT:
                        playerX_change = -2.5
                    if event.key == pygame.K_RIGHT:
                        playerX_change = 2.5
                    if event.key == pygame.K_SPACE and bullet_state == 'ready':
                        bullet_sound = mixer.Sound('audio/laser.wav')
                        bullet_sound.play()
                        bulletX = playerX
                        bullet_state = 'fire'
            
            if event.type == pygame.KEYUP and not game_paused:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    playerX_change = 0

        if game_paused:
            action = draw_pause_menu()
            if action == "resume":
                game_paused = False
                mixer.music.unpause()
            elif action == "menu":
                return "menu"
            continue

        playerX = max(0, min(playerX + playerX_change, 736))
        
        if bullet_state == 'fire':
            screen.blit(bullet_img, (bulletX + 16, bulletY + 10))
            bulletY -= 15
            if bulletY <= 0:
                bullet_state = 'ready'
                bulletY = 480
        
        handle_enemy_shooting()
        for bullet in enemy_bullets[:]:
            screen.blit(enemy_bullet_img, (bullet["x"], bullet["y"]))
            bullet["y"] += bullet["speed"]
            
            if (playerX < bullet["x"] < playerX + 64 and
                playerY < bullet["y"] < playerY + 64):
                game_over()
                return "game_over"
            
            if bullet["y"] > screen_height:
                enemy_bullets.remove(bullet)
        
        # Enemies
        active_enemies = 0
        for i, enemy in enumerate(enemies):
            if enemy_alive[i]:
                active_enemies += 1
                enemy["x"] += enemy["speed"] * enemy["direction"]
                
                if enemy["x"] <= 0 or enemy["x"] >= 736:
                    enemy["direction"] *= -1
                    enemy["y"] += base_enemy_y_increment + 5 * (wave_number - 1)
                
                # Bullet collision
                if bullet_state == 'fire' and math.hypot(enemy["x"]-bulletX, enemy["y"]-bulletY) < 27:
                    explosion_sound = mixer.Sound('audio/explosion.wav')
                    explosion_sound.play()
                    bullet_state = 'ready'
                    bulletY = 480
                    enemy["health"] -= 1
                    
                    if enemy["health"] <= 0:
                        enemy_alive[i] = False
                        score_value += 50 if enemy["type"] == 0 else 150 if enemy["type"] == 1 else 250
                
                screen.blit(enemy_img[enemy["type"]], (enemy["x"], enemy["y"]))
                draw_health_bar(enemy)
        
        if active_enemies == 0:
            result = victory_screen()
            if result == "restart":
                return "restart"
            elif result == "next":
                return "next"
        
        if any(en["y"] > 440 for en, alive in zip(enemies, enemy_alive) if alive):
            game_over()
            return "game_over"
        
        screen.blit(player_img, (playerX, playerY))
        show_score()
        pygame.display.update()

def main_menu():
    global base_enemy_speed, base_enemy_y_increment
    
    menu_font = pygame.font.Font("freesansbold.ttf", 50)
    btn_font = pygame.font.Font("freesansbold.ttf", 30)
    buttons = [
        {"y": 250, "text": "Easy", "color": (0,200,0)},
        {"y": 330, "text": "Medium", "color": (255,165,0)},
        {"y": 410, "text": "Hard", "color": (200,0,0)},
        {"y": 490, "text": "Exit", "color": (100,100,100)}
    ]
    
    while True:
        screen.blit(background, (0,0))
        title = menu_font.render("SPACE INVADERS", True, (255,255,255))
        screen.blit(title, (200, 100))
        
        for btn in buttons:
            rect = pygame.Rect(300, btn["y"], 200, 50)
            pygame.draw.rect(screen, btn["color"], rect)
            text = btn_font.render(btn["text"], True, (255,255,255))
            text_width = text.get_width()
            text_x = rect.x + (rect.width - text_width) // 2
            screen.blit(text, (text_x, rect.y + 10))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                for i, btn in enumerate(buttons):
                    rect = pygame.Rect(300, btn["y"], 200, 50)
                    if rect.collidepoint(mouse):
                        if i == 3:
                            pygame.quit()
                            sys.exit()
                        else:
                            if i == 0:
                                base_enemy_speed = 1.0
                                base_enemy_y_increment = 30
                            elif i == 1:
                                base_enemy_speed = 1.5
                                base_enemy_y_increment = 40
                            elif i == 2:
                                base_enemy_speed = 2.0
                                base_enemy_y_increment = 50
                            return

def show_splash_screen():
    clock = pygame.time.Clock()
    splash_duration = 7
    fade_duration = 2.5

    title_text = "Space War"
    team_text = "Development by:"
    members_text = [
        "Yuones Fakhari",
       
    ]
    course_text = "Game Development Project V=1.0"
    
    start_time = time.time()
    current_stage = 0
    typewriter_delay = 0.08
    current_title = ""
    current_team = ""
    current_members = [""]*5
    current_course = ""
    alpha = 255

    while True:
        elapsed = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))

        # محاسبه پیشرفت انیمیشن
        if current_stage == 0:
            chars_to_add = int(elapsed / typewriter_delay)
            
            # آپدیت عنوان
            if len(current_title) < len(title_text):
                current_title = title_text[:chars_to_add]
            
            # آپدیت تیم
            elif len(current_team) < len(team_text):
                current_team = team_text[:chars_to_add - len(title_text)]
            
            # آپدیت اعضا
            else:
                remaining_chars = chars_to_add - len(title_text) - len(team_text)
                for i in range(1):
                    member_len = len(members_text[i])
                    if remaining_chars > 0:
                        show_chars = min(remaining_chars, member_len)
                        current_members[i] = members_text[i][:show_chars]
                        remaining_chars -= member_len + 1  # +1 برای فاصله خطوط
            
            # آپدیت درس
            if all(len(m) == len(t) for m, t in zip(current_members, members_text)):
                current_course = course_text[:chars_to_add - len(title_text) - len(team_text) - sum(len(m) for m in members_text) - 5]
            
            # بررسی اتمام همه متن‌ها
            if len(current_course) == len(course_text):
                current_stage = 1
                start_time = time.time()

        elif current_stage == 1:
            if elapsed > 3:
                current_stage = 2
                start_time = time.time()

        elif current_stage == 2:
            progress = min(elapsed / fade_duration, 1.0)
            alpha = int(255 * (1 - progress))
            if progress >= 1.0:
                return

        # ایجاد سطوح متن
        title_surface = pygame.font.Font('freesansbold.ttf', 45).render(current_title, True, (0, 255, 255))
        team_surface = pygame.font.Font('freesansbold.ttf', 28).render(current_team, True, (255, 255, 255))
        member_surfaces = [
            pygame.font.Font('freesansbold.ttf', 22).render(m, True, (200, 200, 0))
            for m in current_members
        ]
        course_surface = pygame.font.Font('freesansbold.ttf', 26).render(current_course, True, (255, 100, 100))

        # تنظیم آلفا
        if current_stage == 2:
            for surface in [title_surface, team_surface, *member_surfaces, course_surface]:
                surface.set_alpha(alpha)

        # محاسبه موقعیت‌ها
        y_pos = 100
        title_rect = title_surface.get_rect(center=(screen_width/2, y_pos))
        y_pos += 80
        
        screen.blit(title_surface, title_rect)
        
        team_rect = team_surface.get_rect(center=(screen_width/2, y_pos))
        y_pos += 50
        screen.blit(team_surface, team_rect)
        
        for member in member_surfaces:
            member_rect = member.get_rect(center=(screen_width/2, y_pos))
            screen.blit(member, member_rect)
            y_pos += 35
        
        y_pos += 30
        course_rect = course_surface.get_rect(center=(screen_width/2, y_pos))
        screen.blit(course_surface, course_rect)

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    show_splash_screen()  
    while True:
        reset_game()
        main_menu()
        
        while True:
            result = game_loop()
            
            if result == "restart":
                reset_game()
            elif result == "next":
                wave_number += 1
            elif result == "menu":
                break
            else: # game_over
                reset_game()
                break