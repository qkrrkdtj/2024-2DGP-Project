import math

from pico2d import load_image
import tile

class Tower:
    tower_size = 50

    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.angle = 0.0
        self.target = None
        self.targets = []
        self.attack_cooldown = 0
        self.selected = False  # 타워 선택 상태
        self.load_images()
        self.setup_tower_stats()
        self.upgrade_level = 1
        # self.level = 1
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
            elif self.tower_type == 'Slow':
                self.under = load_image('under_round.png')
                self.body = load_image('turret4_base.png')
                self.barrel = load_image('turret4_canon.png')

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
        elif self.tower_type == 'Slow':
            self.range = 100
            self.damage = 0
            self.attack_speed = 1.0
            self.slow_effect = 0.5  # 50% 감속
            self.cost = 120

    def draw(self):
        # 타워가 선택되었을 때 범위 표시
        if self.selected:
            # 범위 이미지를 타워의 범위에 맞게 크기 조절하여 그리기
            self.range_image.draw(self.x, self.y, self.range * 2, self.range * 2)

        # 타워 몸통 그리기
        self.under.draw(self.x, self.y, Tower.tower_size, Tower.tower_size)
        self.body.draw(self.x, self.y, Tower.tower_size, Tower.tower_size)

        # 포신을 각도에 따라 회전하여 그리기
        self.barrel.rotate_draw(math.radians(self.angle), self.x, self.y, Tower.tower_size, Tower.tower_size)

    def update(self):
        # 여기에 적 탐지 및 타겟 설정 로직 추가 가능
        pass


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
        elif self.tower_type == 'Slow':
            self.range += 10
            self.slow_effect -= 0.1  # 감속 효과 증가
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
        elif self.tower_type == 'Slow':
            return 60 + (self.upgrade_level - 1) * 10
        else:
            return 50  # 기본값