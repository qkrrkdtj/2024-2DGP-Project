from pico2d import *
import game_framework

class Enemy:
    def __init__(self, x, y, enemy_type, health, speed, path):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.health = health
        self.speed = speed * 1.5  # 이동 속도 증가
        self.path = path[:]
        self.alive = True
        self.image = self.load_image(enemy_type)

    def load_image(self, enemy_type):
        if enemy_type == 'Basic':
            return load_image('round.png')
        elif enemy_type == 'Tough':
            return load_image('square.png')
        elif enemy_type == 'Fast':
            return load_image('triangle.png')
        elif enemy_type == 'Boss':
            return load_image('snow.png')

    def update(self):
        if not self.alive:
            return

        if self.path and len(self.path) > 1:
            next_x, next_y = self.path[1]
            dx, dy = next_x - self.x, next_y - self.y
            distance_to_next = (dx**2 + dy**2) ** 0.5

            move_distance = self.speed * game_framework.frame_time

            if move_distance >= distance_to_next:
                self.x, self.y = next_x, next_y
                self.path.pop(0)
            else:
                self.x += dx / distance_to_next * move_distance
                self.y += dy / distance_to_next * move_distance

    def draw(self):
        if self.alive:
            self.image.draw(self.x, self.y, 20, 20)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False