import math

from pico2d import load_image, draw_rectangle

import game_framework
import game_world

# bullet speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 50.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

class Bullet:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.image = load_image('bullet1.png')  # 탄환 이미지
        self.bullet_speed = RUN_SPEED_PPS

    def get_bb(self):
        return self.x - 5, self.y - 5, self.x + 5, self.y + 5  # 작은 크기의 충돌 박스 설정

    def update(self):
        if not self.target or not self.target.alive:
            game_world.remove_object(self)
            return

        dx, dy = self.target.x - self.x, self.target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance < self.bullet_speed * game_framework.frame_time:
            # 충돌 처리
            self.target.handle_collision('enemy:bullet', self)  # 충돌 처리 호출
            game_world.remove_object(self)  # 탄환 제거
        else:
            # 탄환 이동
            self.x += (dx / distance) * self.bullet_speed * game_framework.frame_time
            self.y += (dy / distance) * self.bullet_speed * game_framework.frame_time

    def handle_collision(self, group, other):
        if group == 'enemy:bullet':
            game_world.remove_collision_object(self)

    def draw(self):
        self.image.draw(self.x, self.y, 20, 20)  # 탄환 크기를 20x20으로 설정
        draw_rectangle(*self.get_bb())  # 디버깅용 충돌 박스