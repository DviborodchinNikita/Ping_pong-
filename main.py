from random import choice

from pygame import *

init()
mixer.init()
font.init()


class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, x, y, width, height, speed):
        super().__init__()
        self.speed = speed
        self.image = transform.scale(image.load(sprite_image), (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        virtual_surface.blit(self.image, (self.rect.x, self.rect.y))


class Ball(GameSprite):
    def __init__(self):
        super().__init__("images/ball.png", WIDTH // 2 - 25, HEIGHT // 2 - 25, 50, 50, 10)
        self.speed_x = self.speed
        self.speed_y = self.speed
        self.disable = False
        self.current_disable_frames = 0
        self.max_disable_frames = 60

    def update(self, player_left, player_right):
        if not self.disable:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

            if self.rect.bottom > HEIGHT:
                self.speed_y *= -1
            if self.rect.top < 0:
                self.speed_y *= -1

            if sprite.collide_rect(self, player_right):
                self.speed_x *= -1.1
                self.rect.x = player_right.rect.x - self.rect.w

            if sprite.collide_rect(self, player_left):
                self.speed_x *= -1.1
                self.rect.x = player_left.rect.right

            if self.rect.left > WIDTH:
                player_left.score.increase_score(1)
                self.respawn()

            if self.rect.right < 0:
                player_right.score.increase_score(1)
                self.respawn()
        else:
            self.current_disable_frames -= 1
            if self.current_disable_frames <= 0:
                self.disable = False

    def respawn(self):
        self.rect.x = WIDTH // 2 - 25
        self.rect.y = HEIGHT // 2 - 25
        self.speed_x = choice((-self.speed, self.speed))
        self.speed_y = choice((-self.speed, self.speed))
        self.disable = True
        self.current_disable_frames = self.max_disable_frames


class Racket(GameSprite):
    def __init__(self, player_num):
        self.player_num = player_num
        super().__init__("images/platform.png", 0, 0, 150, 30, 15)
        if player_num == 1:
            self.image = transform.rotate(self.image, -90)
            x = 100
        else:
            self.image = transform.rotate(self.image, 90)
            x = 1150

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = (HEIGHT - 150) // 2
        self.score = Score()
        
    def update(self):
        keys = key.get_pressed()
        if self.player_num == 1:
            if keys[K_w] and self.rect.y > 0:
                self.rect.y -= self.speed
            if keys[K_s] and self.rect.y < HEIGHT - self.rect.height:
                self.rect.y += self.speed

        if self.player_num == 2:
            if keys[K_UP] and self.rect.y > 0:
                self.rect.y -= self.speed
            if keys[K_DOWN] and self.rect.y < HEIGHT - self.rect.height:
                self.rect.y += self.speed


class Score:
    def __init__(self):
        self.points = 0
        self.font = font.Font(None, 100)
        self.update_text()

    def increase_score(self, amount):
        self.points += amount
        self.update_text()

    def restore(self):
        self.points = 0
        self.update_text()

    def update_text(self):
        self.text = str(self.points)
        self.interface_text = self.font.render(self.text, True, (0, 0, 0))


WIDTH = 1280
HEIGHT = 720
ASPECT_RATIO = WIDTH / HEIGHT

FPS = 60

window = display.set_mode((WIDTH, HEIGHT), RESIZABLE)
display.set_caption("Ping-pong")
clock = time.Clock()

virtual_surface = Surface((WIDTH, HEIGHT))
current_size = window.get_size()


ball = Ball()
player_1 = Racket(1)
player_2 = Racket(2)


game = True
finish = False
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    game = False
        if e.type == VIDEORESIZE:
            new_width = e.w
            new_height = int(new_width / ASPECT_RATIO)
            window = display.set_mode((new_width, new_height), RESIZABLE)
            current_size = window.get_size()

    if not finish:
        virtual_surface.fill((159, 178, 235))

        ball.reset()
        ball.update(player_1, player_2)

        player_1.reset()
        player_1.update()

        virtual_surface.blit(player_1.score.interface_text, (WIDTH // 2 - 120, 30))
        virtual_surface.blit(player_2.score.interface_text, (WIDTH // 2 + 80, 30))

    scaled_surfase = transform.scale(virtual_surface, current_size)
    window.blit(scaled_surfase, (0, 0))
    clock.tick(FPS)
    display.update()