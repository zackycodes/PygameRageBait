import pygame
import random
import sys
import math

# Set up Pygame
pygame.init()

# Set fullscreen mode
try:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
except:
    screen = pygame.display.set_mode((1280, 720))

window_size = screen.get_size()
W, H = window_size[0], window_size[1]

score = 0
pygame.display.set_caption("Collision Detection")
clock = pygame.time.Clock()

# Sprites
sprite1 = pygame.sprite.Sprite() # Red AI
sprite2 = pygame.sprite.Sprite() # Green Player
sprite1.rect = pygame.Rect(W // 2, H // 2, 50, 50)
sprite2.rect = pygame.Rect(200, 200, 50, 50)

# Speeds
sprite1_speed = 5
sprite2_speed = 7
ai_dir = [random.uniform(-1, 1), random.uniform(-1, 1)]

# Power-up setup
power_up = pygame.sprite.Sprite()
power_up.rect = pygame.Rect(random.randint(50, W-50), random.randint(50, H-50), 20, 20)
power_up_active = False
power_up_timer = 0

# Debuffs
debuff_particles = [] # Yellow
inversion_particles = [] # Purple
inversion_active = False
inversion_timer = 0

game_time = 60
start_ticks = pygame.time.get_ticks()

def get_dist(rect1, rect2):
    return math.sqrt((rect1.centerx - rect2.centerx)**2 + (rect1.centery - rect2.centery)**2)

while True:
    # 1. Timing & Events
    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
    time_left = max(0, int(game_time - elapsed_time))
    if time_left <= 0: break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    # 2. Player Movement
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w]: dy -= sprite2_speed
    if keys[pygame.K_s]: dy += sprite2_speed
    if keys[pygame.K_a]: dx -= sprite2_speed
    if keys[pygame.K_d]: dx += sprite2_speed

    if inversion_active:
        sprite2.rect.x -= dx
        sprite2.rect.y -= dy
    else:
        sprite2.rect.x += dx
        sprite2.rect.y += dy

    sprite2.rect.clamp_ip(screen.get_rect())

    # 3. Smart AI Movement with Corner Escape
    dist = get_dist(sprite1.rect, sprite2.rect)
    
    if dist < 450: # Flee Mode
        run_x = sprite1.rect.centerx - sprite2.rect.centerx
        run_y = sprite1.rect.centery - sprite2.rect.centery
        
        # --- CORNER ESCAPE LOGIC ---
        # If AI is hitting a wall, inject "sideways" movement so it doesn't stick
        if sprite1.rect.left < 50 or sprite1.rect.right > W - 50:
            run_y += 100 if run_y > 0 else -100 # Prioritize moving vertically away
        if sprite1.rect.top < 50 or sprite1.rect.bottom > H - 50:
            run_x += 100 if run_x > 0 else -100 # Prioritize moving horizontally away
            
        mag = math.sqrt(run_x**2 + run_y**2)
        if mag != 0:
            # Add a tiny bit of noise/jitter so it's never perfectly still
            ai_dir = [(run_x / mag) + random.uniform(-0.1, 0.1), 
                      (run_y / mag) + random.uniform(-0.1, 0.1)]
    
    # Apply Movement
    sprite1.rect.x += ai_dir[0] * sprite1_speed
    sprite1.rect.y += ai_dir[1] * sprite1_speed

    # Hard Boundary Bounce
    if sprite1.rect.left <= 0:
        sprite1.rect.left = 0
        ai_dir[0] = abs(ai_dir[0]) # Force move right
    elif sprite1.rect.right >= W:
        sprite1.rect.right = W
        ai_dir[0] = -abs(ai_dir[0]) # Force move left
        
    if sprite1.rect.top <= 0:
        sprite1.rect.top = 0
        ai_dir[1] = abs(ai_dir[1]) # Force move down
    elif sprite1.rect.bottom >= H:
        sprite1.rect.bottom = H
        ai_dir[1] = -abs(ai_dir[1]) # Force move up

    # 4. Collisions
    if sprite1.rect.colliderect(sprite2.rect):
        score += 1
        sprite1_speed += 0.4
        sprite1.rect.topleft = (random.randint(100, W-100), random.randint(100, H-100))

    if sprite2.rect.colliderect(power_up.rect):
        power_up_active = True
        power_up_timer = pygame.time.get_ticks()
        sprite2_speed = 12
        power_up.rect.topleft = (random.randint(50, W-50), random.randint(50, H-50))

    # Particles logic
    for p in debuff_particles[:]:
        if sprite2.rect.colliderect(p):
            sprite2_speed = max(3, sprite2_speed - 2)
            debuff_particles.remove(p)
    
    for i in inversion_particles[:]:
        if sprite2.rect.colliderect(i):
            inversion_active = True
            inversion_timer = pygame.time.get_ticks()
            inversion_particles.remove(i)

    # Spawning
    if len(debuff_particles) < 3 and random.random() < 0.01:
        debuff_particles.append(pygame.Rect(random.randint(50,W-50), random.randint(50,H-50), 15, 15))
    if len(inversion_particles) < 1 and random.random() < 0.005:
        inversion_particles.append(pygame.Rect(random.randint(50,W-50), random.randint(50,H-50), 20, 20))

    # Timer Resets
    now = pygame.time.get_ticks()
    if power_up_active and now - power_up_timer > 5000:
        power_up_active = False
        sprite2_speed = 7
    if inversion_active and now - inversion_timer > 4000:
        inversion_active = False

    # 5. Drawing (No Keyword Arguments)
    screen.fill((0, 0, 0))
    
    pygame.draw.rect(screen, (255, 0, 0), (sprite1.rect.x, sprite1.rect.y, 50, 50))
    pygame.draw.rect(screen, (0, 255, 0), (sprite2.rect.x, sprite2.rect.y, 50, 50))
    pygame.draw.rect(screen, (0, 0, 255), (power_up.rect.x, power_up.rect.y, 20, 20))
    
    for p in debuff_particles: pygame.draw.rect(screen, (255, 255, 0), (p.x, p.y, p.width, p.height))
    for i in inversion_particles: pygame.draw.rect(screen, (160, 32, 240), (i.x, i.y, i.width, i.height))

    # UI
    font = pygame.font.SysFont(None, 36)
    score_txt = font.render("Score: " + str(score), True, (255, 255, 255))
    time_txt = font.render("Time: " + str(time_left), True, (255, 0, 0) if time_left < 10 else (255, 255, 255))
    screen.blit(score_txt, (10, 10))
    screen.blit(time_txt, (10, 50))

    if inversion_active:
        big_f = pygame.font.SysFont(None, 72)
        warn = big_f.render("CONTROLS INVERTED!", True, (160, 32, 240))
        screen.blit(warn, (W//2 - warn.get_width()//2, 100))
        pygame.draw.rect(screen, (160, 32, 240), (0, 0, W, H), 10)

    pygame.display.flip()
    clock.tick(120)

pygame.quit()