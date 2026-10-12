import math
import random
import sys
import pygame

pygame.init()
pygame.display.set_caption("Герои Энвелла: Разлом")
W, H = 960, 600
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 22)
SMALL = pygame.font.SysFont("arial", 17)
BIG = pygame.font.SysFont("arial", 44, bold=True)

SKY = (15, 20, 49)
BLUE = (58, 128, 235)
CYAN = (85, 226, 255)
WHITE = (239, 246, 255)
GOLD = (255, 205, 88)
RED = (240, 82, 99)
GREEN = (85, 220, 150)
DARK = (18, 25, 43)

def text(s, x, y, font=FONT, color=WHITE, center=False):
    surf = font.render(s, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

def draw_background(camera):
    # Deep twilight gradient with distant layers for a richer fantasy atmosphere.
    for y in range(H):
        t = y / H
        col = (int(12 + 14*t), int(17 + 15*t), int(43 + 27*t))
        pygame.draw.line(screen, col, (0, y), (W, y))
    tick = pygame.time.get_ticks()
    # Moon and soft halo
    pygame.draw.circle(screen, (35, 57, 111), (770, 100), 61)
    pygame.draw.circle(screen, (92, 125, 198), (770, 100), 43)
    pygame.draw.circle(screen, (199, 221, 255), (770, 100), 31)
    pygame.draw.circle(screen, (222, 234, 255), (759, 91), 7)
    # Far mountains
    for i in range(8):
        x = int((i * 175 - camera * 0.12) % (W + 240)) - 120
        base = 430 + (i % 3) * 25
        pygame.draw.polygon(screen, (24, 34, 76), [(x-100,base),(x,base-135-(i%2)*35),(x+100,base)])
        pygame.draw.polygon(screen, (42, 58, 111), [(x,base-135-(i%2)*35),(x+35,base-80),(x+100,base)])
    # Floating rune-like shards
    for i in range(9):
        x = int((i * 155 - camera * 0.22) % (W + 180)) - 90
        y = 150 + (i % 3) * 48
        pygame.draw.polygon(screen, (35, 51, 98), [(x-35,y),(x+25,y-8),(x+20,y+15),(x-20,y+28)])
        pygame.draw.polygon(screen, (55, 81, 139), [(x-20,y+28),(x+20,y+15),(x+3,y+55)])
    # Twinkling stars
    for i in range(58):
        x = (i * 197 + 43) % W
        y = (i * 73 + 21) % 330
        pulse = 1 if (i + tick // 350) % 4 else 2
        color = (105, 151, 226) if i % 3 else (177, 221, 255)
        pygame.draw.circle(screen, color, (x, y), pulse)
    # Atmospheric glow near the horizon
    pygame.draw.rect(screen, (21, 37, 72), (0, 475, W, 125))

def draw_platform(rect, camera):
    r = pygame.Rect(rect.x-camera, rect.y, rect.w, rect.h)
    if r.right < -5 or r.left > W+5:
        return
    # Shadow, stone body, glowing magical rim
    shadow = r.move(0, 6)
    pygame.draw.rect(screen, (7, 11, 29), shadow, border_radius=7)
    pygame.draw.rect(screen, (31, 43, 76), r, border_radius=7)
    pygame.draw.rect(screen, (48, 75, 119), (r.x+2, r.y+7, max(0,r.w-4), max(0,r.h-9)), border_radius=5)
    pygame.draw.line(screen, (91, 230, 239), (r.x+7,r.y+2), (r.right-7,r.y+2), 3)
    pygame.draw.line(screen, (52, 132, 189), (r.x+8,r.y+10), (r.right-8,r.y+10), 1)
    for x in range(r.x+14, r.right-8, 32):
        pygame.draw.line(screen, (43, 63, 101), (x, r.y+17), (x+8, r.bottom-5), 2)
    for x in range(r.x+18, r.right-8, 70):
        pygame.draw.circle(screen, (70, 172, 207), (x, r.y+4), 2)

class Player:
    def __init__(self):
        self.x, self.y = 70.0, 390.0
        self.vx = self.vy = 0.0
        self.w, self.h = 34, 48
        self.hp = 5
        self.face = 1
        self.on_ground = False
        self.cooldown = 0
        self.invuln = 0
        self.score = 0
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)
    def update(self, keys, platforms):
        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -4.2; self.face = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = 4.2; self.face = 1
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = -11.8; self.on_ground = False
        self.x += self.vx
        self.x = max(0, min(self.x, LEVEL_W - self.w))
        self.y += self.vy
        self.vy += 0.55
        self.on_ground = False
        for p in platforms:
            pr = pygame.Rect(p.x, p.y, p.w, p.h)
            if self.rect.colliderect(pr):
                if self.vy >= 0 and self.y + self.h - self.vy <= p.y + 8:
                    self.y = p.y - self.h
                    self.vy = 0
                    self.on_ground = True
        if self.y > H + 100:
            self.hp = 0
        self.cooldown = max(0, self.cooldown-1)
        self.invuln = max(0, self.invuln-1)
    def draw(self, camera):
        x, y = int(self.x-camera), int(self.y)
        if self.invuln and self.invuln % 6 < 3:
            return
        pygame.draw.ellipse(screen, (8, 12, 27), (x-3, y+self.h-5, self.w+8, 10))
        # Subtle magical aura and layered armor
        pygame.draw.circle(screen, (27, 89, 160), (x+17, y+26), 25, 1)
        pygame.draw.rect(screen, (36, 63, 126), (x+5, y+19, 24, 24), border_radius=6)
        pygame.draw.rect(screen, (52, 92, 166), (x+8, y+22, 18, 17), border_radius=4)
        pygame.draw.polygon(screen, (98, 230, 255), [(x+17,y+22),(x+21,y+30),(x+17,y+35),(x+13,y+30)])
        pygame.draw.rect(screen, (81, 148, 242), (x+5, y+19, 24, 7), border_radius=3)
        pygame.draw.circle(screen, (241, 193, 150), (x+17, y+12), 11)
        pygame.draw.polygon(screen, (224, 239, 255), [(x+5,y+9),(x+11,y-1),(x+23,y-1),(x+29,y+9),(x+18,y+5)])
        pygame.draw.circle(screen, (26, 35, 57), (x+17+self.face*4, y+12), 2)
        pygame.draw.line(screen, CYAN, (x+8,y+29), (x+2,y+40), 4)
        pygame.draw.line(screen, (240, 194, 130), (x+26,y+29), (x+31,y+38), 4)
        pygame.draw.rect(screen, (37, 48, 78), (x+8,y+40,7,8), border_radius=2)
        pygame.draw.rect(screen, (37, 48, 78), (x+20,y+40,7,8), border_radius=2)

class Enemy:
    def __init__(self, x, y, left, right):
        self.x, self.y = float(x), float(y)
        self.left, self.right = left, right
        self.v = random.choice([-1.4, 1.4])
        self.hp = 2
        self.alive = True
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), 34, 30)
    def update(self):
        if not self.alive: return
        self.x += self.v
        if self.x < self.left or self.x > self.right:
            self.v *= -1
        self.y = 0 if self.y < 0 else self.y
    def draw(self, camera):
        if not self.alive: return
        x, y = int(self.x-camera), int(self.y)
        pygame.draw.ellipse(screen, (11, 13, 32), (x-3,y+23,40,9))
        pygame.draw.polygon(screen, (126, 69, 202), [(x+2,y+22),(x+4,y+8),(x+13,y),(x+25,y+3),(x+32,y+15),(x+29,y+25)])
        pygame.draw.circle(screen, (255, 95, 140), (x+12,y+12), 3)
        pygame.draw.circle(screen, (255, 95, 140), (x+24,y+12), 3)
        pygame.draw.line(screen, (187, 130, 255), (x+8,y+25),(x+2,y+30),3)
        pygame.draw.line(screen, (187, 130, 255), (x+27,y+25),(x+33,y+30),3)

class Bolt:
    def __init__(self, x, y, direction):
        self.x, self.y, self.v = x, y, direction*9
        self.life = 80
    @property
    def rect(self):
        return pygame.Rect(int(self.x-8), int(self.y-5), 16, 10)
    def update(self):
        self.x += self.v; self.life -= 1
    def draw(self, camera):
        x, y = int(self.x-camera), int(self.y)
        pygame.draw.ellipse(screen, (35, 121, 255), (x-12,y-7,25,14))
        pygame.draw.ellipse(screen, CYAN, (x-7,y-4,15,8))
        pygame.draw.circle(screen, WHITE, (x,y), 2)

LEVEL_W = 2500
platforms = [
    pygame.Rect(0, 510, 500, 90),
    pygame.Rect(570, 465, 230, 135),
    pygame.Rect(875, 410, 210, 190),
    pygame.Rect(1160, 470, 300, 130),
    pygame.Rect(1510, 420, 230, 180),
    pygame.Rect(1800, 465, 250, 135),
    pygame.Rect(2110, 400, 390, 200),
    pygame.Rect(260, 390, 130, 18),
    pygame.Rect(650, 340, 120, 18),
    pygame.Rect(980, 300, 120, 18),
    pygame.Rect(1280, 350, 130, 18),
    pygame.Rect(1580, 310, 120, 18),
    pygame.Rect(1900, 350, 120, 18),
]
enemies = [
    Enemy(310, 480, 80, 440), Enemy(610, 435, 590, 760),
    Enemy(920, 380, 890, 1040), Enemy(1230, 440, 1180, 1400),
    Enemy(1550, 390, 1520, 1700), Enemy(1850, 435, 1810, 2010),
    Enemy(2200, 370, 2140, 2430)
]
gems = [(330,355),(700,305),(1020,265),(1330,315),(1620,275),(1940,315),(2280,365)]
player = Player()
bolts = []
camera = 0
state = "menu"
message_timer = 0
victory = False

def reset_game():
    global player, bolts, enemies, gems, camera, state, victory
    player = Player()
    bolts = []
    enemies = [
        Enemy(310, 480, 80, 440), Enemy(610, 435, 590, 760),
        Enemy(920, 380, 890, 1040), Enemy(1230, 440, 1180, 1400),
        Enemy(1550, 390, 1520, 1700), Enemy(1850, 435, 1810, 2010),
        Enemy(2200, 370, 2140, 2430)
    ]
    gems = [(330,355),(700,305),(1020,265),(1330,315),(1620,275),(1940,315),(2280,365)]
    camera = 0
    state = "playing"
    victory = False

def draw_hud():
    pygame.draw.rect(screen, (9, 14, 34), (18, 16, 230, 70), border_radius=12)
    text("ЗДОРОВЬЕ", 31, 22, SMALL, (178, 199, 235))
    for i in range(5):
        color = RED if i < player.hp else (65, 72, 97)
        pygame.draw.rect(screen, color, (31+i*35, 49, 27, 17), border_radius=5)
    text(f"Кристаллы: {player.score}/7", 275, 27, FONT, GOLD)
    text("A/D или ←/→ — движение   ПРОБЕЛ — прыжок   J — магия", 275, 58, SMALL, (203, 218, 255))

running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == "playing": state = "pause"
                elif state == "pause": state = "playing"
                else: running = False
            if state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                reset_game()
            elif state in ("gameover", "victory") and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                reset_game()
            elif state == "pause" and event.key == pygame.K_RETURN:
                state = "playing"
            elif state == "playing" and event.key == pygame.K_j and player.cooldown == 0:
                bolts.append(Bolt(player.x + (player.w if player.face > 0 else 0), player.y+24, player.face))
                player.cooldown = 18

    if state == "playing":
        keys = pygame.key.get_pressed()
        player.update(keys, platforms)
        for e in enemies: e.update()
        for b in bolts: b.update()
        bolts = [b for b in bolts if b.life > 0 and 0 < b.x < LEVEL_W]
        for b in bolts:
            for e in enemies:
                if e.alive and b.rect.colliderect(e.rect):
                    e.hp -= 1; b.life = 0
                    if e.hp <= 0:
                        e.alive = False
                        player.score += 0
        for e in enemies:
            if e.alive and player.rect.colliderect(e.rect) and player.invuln == 0:
                player.hp -= 1
                player.invuln = 70
                player.vy = -6
        for g in gems[:]:
            gr = pygame.Rect(g[0]-10,g[1]-10,20,20)
            if player.rect.colliderect(gr):
                gems.remove(g); player.score += 1
        if player.hp <= 0: state = "gameover"
        if player.x > LEVEL_W - 100 and player.score >= 5: state = "victory"
        camera = max(0, min(LEVEL_W-W, player.x-W*0.38))

    draw_background(camera)
    for p in platforms: draw_platform(p, camera)
    portal_x = LEVEL_W - 80 - camera
    pulse = 2 + int((pygame.time.get_ticks() // 180) % 3)
    # Portal rings, core and drifting sparks
    pygame.draw.ellipse(screen, (23, 49, 110), (portal_x-32, 338, 78, 126))
    pygame.draw.ellipse(screen, (42, 73, 145), (portal_x-25, 345, 64, 112), 5)
    pygame.draw.ellipse(screen, (73, 151, 255), (portal_x-20, 350, 54, 102), 2)
    pygame.draw.ellipse(screen, CYAN, (portal_x-15, 355, 44, 92), pulse)
    pygame.draw.ellipse(screen, (41, 100, 202), (portal_x-8, 364, 30, 74), 2)
    for i in range(7):
        sx = portal_x + int(math.sin(pygame.time.get_ticks()/350 + i)*25)
        sy = 400 + int(math.cos(pygame.time.get_ticks()/420 + i)*42)
        pygame.draw.circle(screen, (132, 241, 255), (sx, sy), 2)
    for gx, gy in gems:
        x = int(gx-camera)
        bob = int(math.sin(pygame.time.get_ticks()/240 + gx)*3)
        gy2 = gy + bob
        pygame.draw.circle(screen, (103, 83, 31), (x, gy2), 17, 1)
        pygame.draw.polygon(screen, (255, 164, 55), [(x,gy2-15),(x+11,gy2),(x,gy2+15),(x-11,gy2)])
        pygame.draw.polygon(screen, GOLD, [(x,gy2-12),(x+8,gy2),(x,gy2+12),(x-8,gy2)])
        pygame.draw.polygon(screen, (255,250,207), [(x,gy2-8),(x+3,gy2-1),(x,gy2+5)])
    for e in enemies: e.draw(camera)
    for b in bolts: b.draw(camera)
    player.draw(camera)

    if state == "playing":
        draw_hud()
    elif state == "menu":
        overlay = pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((4,8,25,190)); screen.blit(overlay,(0,0))
        text("ГЕРОИ ЭНВЕЛЛА", W//2, 150, BIG, CYAN, True)
        text("РАЗЛОМ МЕЖДУ МИРАМИ", W//2, 204, FONT, GOLD, True)
        text("Собери кристаллы и доберись до портала.", W//2, 278, FONT, WHITE, True)
        text("Побеждай теневых существ магическими снарядами.", W//2, 312, FONT, WHITE, True)
        text("ENTER — НАЧАТЬ ИГРУ", W//2, 395, BIG, GREEN, True)
        text("Управление: A/D или стрелки • Пробел — прыжок • J — магия", W//2, 465, SMALL, (195,211,245), True)
        text("Фанатская мини-игра с оригинальной графикой", W//2, 530, SMALL, (138,157,200), True)
    elif state == "pause":
        overlay = pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((4,8,25,200)); screen.blit(overlay,(0,0))
        text("ПАУЗА", W//2, 230, BIG, CYAN, True)
        text("Нажми ENTER, чтобы продолжить", W//2, 300, FONT, WHITE, True)
        text("ESC — меню выхода", W//2, 340, SMALL, (195,211,245), True)
    elif state == "gameover":
        overlay = pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((4,8,25,210)); screen.blit(overlay,(0,0))
        text("ТЫ ПОТЕРЯЛ ВСЕ СИЛЫ", W//2, 220, BIG, RED, True)
        text("ENTER — попробовать снова", W//2, 305, FONT, WHITE, True)
    elif state == "victory":
        overlay = pygame.Surface((W,H), pygame.SRCALPHA); overlay.fill((4,8,25,200)); screen.blit(overlay,(0,0))
        text("ПОРТАЛ ОТКРЫТ!", W//2, 205, BIG, GOLD, True)
        text("Ты прошёл Разлом между мирами!", W//2, 270, FONT, WHITE, True)
        text(f"Собрано кристаллов: {player.score}/7", W//2, 310, FONT, CYAN, True)
        text("ENTER — сыграть ещё раз", W//2, 370, FONT, GREEN, True)
    pygame.display.flip()

pygame.quit()
sys.exit()
