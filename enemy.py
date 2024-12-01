from pico2d import *
import game_framework
import game_world
from stage_select import draw_text


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
            distance_to_next = (dx ** 2 + dy ** 2) ** 0.5

            move_distance = self.speed * game_framework.frame_time

            if move_distance >= distance_to_next:
                self.x, self.y = next_x, next_y
                self.path.pop(0)

                # 목표 지점에 도달 시
                if len(self.path) == 1:  # 마지막 지점에 도달했을 때
                    if self.type == 'Boss':
                        game_framework.player_health -= 10  # Boss 도달 시 체력 10 감소
                        print(f"Boss reached the castle! Health: {game_framework.player_health}")
                    else:
                        game_framework.player_health -= 1  # 일반 적은 체력 1 감소
                        print(f"Castle hit! Health: {game_framework.player_health}")

                    # 체력이 0 이하일 경우 게임오버
                    if game_framework.player_health <= 0:
                        game_framework.check_game_over()

                    # Castle에 도달한 적은 삭제
                    self.alive = False
                    game_world.remove_object(self)
            else:
                self.x += dx / distance_to_next * move_distance
                self.y += dy / distance_to_next * move_distance

    def draw(self):
        if self.alive:
            if self.type == 'Boss':
                self.image.draw(self.x, self.y)
            else:
                self.image.draw(self.x, self.y, 20, 20)

            # 체력 표시
            draw_rectangle(self.x - 15, self.y + 15, self.x + 15, self.y + 20)
            draw_text(f"{self.health}", self.x - 10, self.y + 15, (255, 0, 0))

    def get_bb(self):
        return self.x - 10, self.y - 10, self.x + 10, self.y + 10
        # 적의 충돌 박스

    def handle_collision(self, group, other):
        if group == 'enemy:bullet':
            print(f"Collision detected with bullet: {other}")  # 디버깅 메시지
            self.health -= other.damage
            print(f"{self.type} enemy hit! Remaining health: {self.health}")  # 체력 감소 디버깅

            if self.health <= 0 and self.alive:
                self.alive = False
                game_world.remove_object(self)

                # 적 처치 시 골드 지급
                gold_reward = {'Basic': 5, 'Tough': 10, 'Fast': 7, 'Boss': 50}.get(self.type, 0)
                game_framework.add_gold(gold_reward)
                print(f"{self.type} enemy defeated! Gold rewarded: {gold_reward}")  # 디버깅 메시지