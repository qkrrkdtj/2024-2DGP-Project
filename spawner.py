import game_framework
import game_world
from enemy import Enemy


class Spawner:
    def __init__(self, path, spawn_interval=1, round_duration=25, round_health_increment=1):
        self.path = path[:]  # 경로 복사
        self.spawn_interval = spawn_interval  # 적 생성 간격 (0.5초)
        self.round_duration = round_duration  # 라운드 지속 시간 (25초)
        self.round_health_increment = round_health_increment

        self.spawn_timer = 0  # 적 생성 타이머
        self.round_timer = 0  # 라운드 타이머
        self.current_round = 0

        # 적 스폰 시퀀스
        self.spawn_sequences = [
            {'enemy_type': 'Basic', 'count': 5},    # 1라운드
            {'enemy_type': 'Tough', 'count': 3},    # 2라운드
            {'enemy_type': 'Fast', 'count': 8}      # 3라운드
        ]

        # 각 적 유형별 누적 등장 횟수
        self.enemy_type_counts = {
            'Basic': 0,
            'Tough': 0,
            'Fast': 0
        }

        # 현재 라운드 정보
        self.current_sequence = None
        self.remaining_enemies = 0

    def update(self):
        # 프레임 시간 추가
        self.spawn_timer += game_framework.frame_time
        self.round_timer += game_framework.frame_time

        # 라운드 종료 확인 (25초)
        if self.round_timer >= self.round_duration:
            self.round_timer = 0
            self.spawn_timer = 0
            self.current_round += 1

            # 다음 라운드 준비
            if self.current_round > 0 and (self.current_round - 1) % 3 == 0:
                # 각 몬스터 유형 등장 2번마다 1마리 추가
                for enemy_type in self.enemy_type_counts:
                    self.enemy_type_counts[enemy_type] += 1

            # 현재 라운드의 스폰 시퀀스 설정
            current_index = (self.current_round - 1) % len(self.spawn_sequences)
            self.current_sequence = self.spawn_sequences[current_index]

            # 스폰할 적 수 설정 (기본 개수 + 추가된 개수)
            base_count = self.current_sequence['count']
            additional_count = self.enemy_type_counts[self.current_sequence['enemy_type']]
            self.remaining_enemies = base_count + additional_count

            print(f"라운드 {self.current_round} 시작: {self.current_sequence['enemy_type']} {self.remaining_enemies}마리")

        # 0.5초마다 적 생성
        if self.spawn_timer >= self.spawn_interval and self.remaining_enemies > 0:
            self.spawn_timer = 0
            self.spawn_enemy()

    def spawn_enemy(self):
        if self.remaining_enemies <= 0:
            return

        # 적 유형별 기본 체력과 속도
        enemy_type = self.current_sequence['enemy_type']
        base_health = {'Basic': 5, 'Tough': 10, 'Fast': 3}[enemy_type]
        speed = {'Basic': 10, 'Tough': 5, 'Fast': 20}[enemy_type]

        # 라운드에 따른 체력 증가
        health = base_health + (self.current_round // len(self.spawn_sequences)) * self.round_health_increment

        # 적 생성 및 월드에 추가
        enemy = Enemy(self.path[0][0], self.path[0][1], enemy_type, health, speed, self.path)
        game_world.add_object(enemy, 1)

        # 남은 적 수 감소
        self.remaining_enemies -= 1

    def draw(self):
        pass