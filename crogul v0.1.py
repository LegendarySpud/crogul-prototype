import pygame, random

print("CroGul v0.1")

class Team():
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.score = 0

class Level():
    def __init__(self, geom):
        self.geom = geom

    def draw(self, surface):
        for g in self.geom:
            if g[0] == "wall":
                pygame.draw.rect(surface, "Black", g[1])

            if g[0] == "spawn":
                if g[1] == "Crows": colour = "White"
                else: colour = "Black"
                pygame.draw.rect(surface, colour, g[2], 5)

            if g[0] == "capture":
                if g[1] == "Crows": colour = "White"
                else: colour = "Black"
                pygame.draw.rect(surface, colour, g[2], 2)

    def collide(self, rect):
        for g in self.geom:
            if g[0] == "wall" and rect.colliderect(g[1]):
                return True

        return False

    def captureCollide(self, rect, team):
        for g in self.geom:
            if g[0] == "capture" and g[1] != team.name and rect.colliderect(g[2]):
                return True

        return False


class Player(pygame.sprite.Sprite):
    def __init__(self, cls="default", team=Team("Seagulls", "White"), keys=["W","A","S","D"], lev=None):
        # Keys (positionally) are: up, left, down, right
        pygame.sprite.Sprite.__init__(self)
        self.pos = pygame.Vector2(0, 0)
        self.vel = pygame.Vector2(0, 0)
        self.cls = cls
        self.team = team
        self.keys = []
        for k in keys:
            self.keys.append(pygame.key.key_code(k))

        self.clsUpdate(self.cls)
        self.should_spawn = True
        self.spawn(lev)

    def keycheck(self, key_state, dt):
        dir = pygame.Vector2(0, 0)
        if key_state[self.keys[0]]:
            dir.y += -1

        if key_state[self.keys[1]]:
            dir.x += -1

        if key_state[self.keys[2]]:
            dir.y += 1

        if key_state[self.keys[3]]:
            dir.x += 1

        if dir != pygame.Vector2(0, 0): dir.normalize()
        if self.vel.length() < self.speed*dt: self.vel += dir*self.accel*dt

    def clsUpdate(self, cls):
        if cls == "default":
            self.cls = cls
            self.rect = pygame.Rect(0, 0, 50, 50)
            self.rect.center = self.pos
            self.speed = 300
            self.accel = 60

    def spawn(self, cur_lev):
        for g in cur_lev.geom:
            if g[0] == "spawn" and g[1] != self.team.name:
                ran_x = random.randint(0, g[2].width - self.rect.width)
                self.rect.left = ran_x + g[2].left
                ran_y = random.randint(0, g[2].height - self.rect.height)
                self.rect.top = ran_y + g[2].top
                self.pos = pygame.Vector2(self.rect.center)
                break

        self.should_spawn = False

    def update(self, key_state, dt, cur_lev, players):
        if self.should_spawn:
            self.spawn(cur_lev)
            self.should_spawn = False

        self.keycheck(key_state, dt)

        self.pos.x += self.vel.x
        self.rect.center = self.pos
        if cur_lev.collide(self.rect):
            self.pos.x -= self.vel.x
            self.rect.center = self.pos

        self.pos.y += self.vel.y
        self.rect.center = self.pos
        if cur_lev.collide(self.rect):
            self.pos.y -= self.vel.y
            self.rect.center = self.pos

        if self.vel.length_squared() != 0: self.vel *= (self.vel.length()-15*dt)/self.vel.length()

        if cur_lev.captureCollide(self.rect, self.team):
            self.team.score += 1
            print(f"{self.team.name} score: {self.team.score}")
            self.should_spawn = True

        for p in players:
            if pygame.Rect.colliderect(self.rect, p.rect) and p.team != self.team:
                self.should_spawn = True

    def draw(self):
        pygame.draw.rect(screen, self.team.colour, self.rect)

def addNorm(vec1, vec2):
    try: return (vec1 + vec2).normalize()
    except: return pygame.Vector2(0, 0)

scr_x = 1200
scr_y = 800

pygame.init()
screen = pygame.display.set_mode((scr_x, scr_y))
pygame.display.set_caption("CroGul v0.1")
clock = pygame.time.Clock()
loop = True

cro = Team("Crows", "Black")
gul = Team("Seagulls", "White")

level1 = Level([
    ["wall", pygame.Rect(0, 0, 20, scr_y)],
    ["wall", pygame.Rect(0, 0, scr_x, 20)],
    ["wall", pygame.Rect(scr_x-20, 0, 20, scr_y)],
    ["wall", pygame.Rect(0, scr_y-20, scr_x, 20)],

    ["spawn", "Crows", pygame.Rect(20, 20, 200, 200)],
    ["spawn", "Seagulls", pygame.Rect(scr_x-220, scr_y-220, 200, 200)],
    ["capture", "Crows", pygame.Rect(scr_x-220, scr_y/2-100, 200, 200)],
    ["capture", "Seagulls", pygame.Rect(20, scr_y/2-100, 200, 200)]
])
cur_level = level1

player1 = Player("default", gul, lev=cur_level)
player2 = Player("default", cro, ["up","left","down","right"], lev=cur_level)
players = [player1, player2]

while loop:
    try: dt = 1/clock.get_fps()
    except: dt = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False

    keys = pygame.key.get_pressed()
    for p in players:
        p.update(keys, dt, cur_level, players)

    screen.fill((100, 100, 100))

    for p in players:
        p.draw()

    cur_level.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()