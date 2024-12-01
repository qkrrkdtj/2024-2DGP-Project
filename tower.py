import math

from pico2d import load_image

import game_framework
import game_world
import tile
from bullet import Bullet
from behavior_tree import BehaviorTree, Action, Sequence, Selector, Condition

# bullet speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 50.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

animation_names = ['Walk', 'Idle']


class Tower:
    tower_size = 50

    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.angle = 90.0
        self.target = None
        self.targets = []
        self.attack_cooldown = 0
        self.selected = False  # 타워 선택 상태
        self.load_images()
        self.setup_tower_stats()
        self.upgrade_level = 1
        self.total_cost = self.cost

    def load_images(self):
        try:
            if self.tower_type == 'Normal':
                self.under = load_image('under_square.png')
                self.body = load_image('turret1_base.png')
                self.barrel = load_image('turret1_canon.png')
            elif self.tower_type == 'Sniper':
                self.under = load_image('under_triangle.png')
                self.body = load_image('turret2_base.png')
                self.barrel = load_image('turret2_canon.png')
            elif self.tower_type == 'Triple':
                self.under = load_image('under_hexa.png')
                self.body = load_image('turret3_base.png')
                self.barrel = load_image('turret3_canon.png')

            # 공격 범위 표시용 이미지 로드
            self.range_image = load_image('zone_b.png')
        except:
            print("Error loading images for tower:", self.tower_type)

    def setup_tower_stats(self):
        # 기본 스탯 설정
        if self.tower_type == 'Normal':
            self.range = 150
            self.damage = 10
            self.attack_speed = 1.0  # 초당 공격 횟수
            self.cost = 100
        elif self.tower_type == 'Sniper':
            self.range = 300
            self.damage = 30
            self.attack_speed = 0.5
            self.cost = 150
        elif self.tower_type == 'Triple':
            self.range = 120
            self.damage = 8
            self.attack_speed = 0.8
            self.max_targets = 3
            self.cost = 200

    def draw(self):
        # 타워, 범위, 탄환 그리기
        self.range_image.draw(self.x, self.y, self.range * 2, self.range * 2)
        self.under.draw(self.x, self.y, Tower.tower_size, Tower.tower_size)
        self.body.draw(self.x, self.y, Tower.tower_size, Tower.tower_size)
        self.barrel.rotate_draw(math.radians(self.angle), self.x, self.y, Tower.tower_size, Tower.tower_size)

    def distance_less_than(self, x1, y1, x2, y2):
        return (x1 - x2) ** 2 + (y1 - y2) ** 2 <= self.range ** 2

    def is_enemy_nearby(self):
        # 타겟이 범위 내에 있는지 확인
        for enemy in self.targets:
            if self.distance_less_than(enemy.x, enemy.y, self.x, self.y):
                self.target = enemy  # 타겟 설정
                return True
        return False

    def shoot_at_enemy(self):
        if self.target is None or not self.target.alive:
            self.target = None  # 타겟이 이미 죽었거나 유효하지 않으면 초기화
            return False

        if self.attack_cooldown <= 0:
            bullet = Bullet(self.x, self.y, self.target, self.damage)
            game_world.add_object(bullet, 2)  # 탄환을 월드에 추가
            self.attack_cooldown = max(0.1, self.attack_speed)  # 쿨다운 초기화
            print("Attack!")  # 공격 출력
            return True
        return False

    def shoot_at_enemies(self):
        if self.tower_type != 'Triple':
            return self.shoot_at_enemy()  # 다른 타입의 타워는 기존 단일 타겟 로직 사용

        if self.attack_cooldown > 0:
            return False  # 공격 쿨다운 중이면 공격하지 않음

        # 범위 내 적들 중 최대 3마리를 타겟팅
        targets_in_range = [enemy for enemy in self.targets if
                            self.distance_less_than(enemy.x, enemy.y, self.x, self.y) and enemy.alive]
        targets_to_attack = targets_in_range[:3]  # 최대 3마리만 공격

        if targets_to_attack:
            for target in targets_to_attack:
                bullet = Bullet(self.x, self.y, target, self.damage)
                game_world.add_object(bullet, 2)  # 탄환을 게임 월드에 추가
            self.attack_cooldown = max(0.1, self.attack_speed)  # 쿨다운 초기화
            print(f"Triple Tower attacking {len(targets_to_attack)} enemies!")  # 디버깅 메시지
            return True

        return False

    def update(self):
        self.targets = game_world.get_enemies()
        self.attack_cooldown -= game_framework.frame_time

        if self.is_enemy_nearby():
            dx, dy = self.target.x - self.x, self.target.y - self.y
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)

            # 8방향으로 근사화
            directions = [0, 45, 90, 135, 180, -135, -90, -45]
            closest_direction = min(directions, key=lambda d: abs(d - angle_deg))
            self.angle = closest_direction

            # Triple 타워인지 확인하고 다중 공격
            if self.tower_type == 'Triple':
                self.shoot_at_enemies()
            else:
                self.shoot_at_enemy()
        else:
            self.target = None

    def add_target(self, enemy):
        # 적을 targets 리스트에 추가
        if enemy not in self.targets:
            self.targets.append(enemy)

    def is_clicked(self, mouse_x, mouse_y):
        left = self.x - 50 // 2
        right = self.x + 50 // 2
        bottom = self.y - 50 // 2
        top = self.y + 50 // 2

        return left <= mouse_x <= right and bottom <= mouse_y <= top

    def upgrade(self):
        if self.upgrade_level >= 5:
            print(f"{self.tower_type} Tower is already at max level!")
            return

        upgrade_cost = self.get_upgrade_cost()
        print(f"Before upgrade - Total cost: {self.total_cost}")

        self.upgrade_level += 1
        print(f"Tower upgraded to level {self.upgrade_level}")

        # 업그레이드 효과 적용
        if self.tower_type == 'Normal':
            self.range += 20
            self.damage += 5
            self.total_cost += upgrade_cost
        elif self.tower_type == 'Sniper':
            self.range += 30
            self.damage += 10
            self.total_cost += upgrade_cost
        elif self.tower_type == 'Triple':
            self.range += 15
            self.damage += 3
            self.total_cost += upgrade_cost

        print(f"{self.tower_type} Tower upgraded to level {self.upgrade_level}!")
        print(f"New stats - Range: {self.range}, Damage: {self.damage}")

    def get_sell_value(self):
        return self.total_cost

    def get_upgrade_cost(self):
        # 타워 종류와 현재 레벨에 따라 업그레이드 비용 결정
        if self.tower_type == 'Normal':
            return 50 + (self.upgrade_level - 1) * 10
        elif self.tower_type == 'Sniper':
            return 75 + (self.upgrade_level - 1) * 15
        elif self.tower_type == 'Triple':
            return 100 + (self.upgrade_level - 1) * 20
        else:
            return 50  # 기본값