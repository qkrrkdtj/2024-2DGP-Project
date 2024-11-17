from pico2d import *
import time


class GameScene:
    def __init__(self, stage_number):
        self.stage_number = stage_number
        self.player_health = 20
        self.player_gold = 100  # 시작 골드
        self.game_started = False
        self.start_time = None
        self.spawn_timer = 0

        # 게임 오브젝트 초기화
        self.map = GameMap(stage_number)  # 스테이지별 맵 로드
        self.towers = []
        self.enemies = []
        self.menu = TowerMenu()
        self.selected_tile = None

        # UI 이미지 로드
        self.health_image = load_image('health_icon.png')
        self.gold_image = load_image('gold_icon.png')
        self.boss_button = load_image('boss_button.png')

        # 게임 상태
        self.is_paused = False
        self.is_game_over = False
        self.boss_spawned = False

    def start_game(self):
        self.game_started = True
        self.start_time = time.time()

    def handle_event(self, event):
        if event.type == SDL_MOUSEBUTTONDOWN:
            x, y = event.x, get_canvas_height() - event.y

            # 보스 버튼 클릭 처리
            if self.is_boss_button_clicked(x, y):
                self.spawn_boss()
                return

            # 타일 선택 처리
            clicked_tile = self.map.get_tile_at(x, y)
            if clicked_tile:
                if clicked_tile.can_place_tower:
                    self.selected_tile = clicked_tile
                    self.menu.show(x, y)
                else:
                    self.menu.hide()
                    self.selected_tile = None

        # 타워 메뉴에서 타워 선택 처리
        elif event.type == SDL_MOUSEBUTTONDOWN:
            if self.menu.is_visible:
                selected_tower = self.menu.get_selected_tower(event.x, get_canvas_height() - event.y)
                if selected_tower and self.can_afford_tower(selected_tower):
                    self.place_tower(selected_tower)

    def update(self):
        if not self.game_started:
            if self.start_time is None:
                self.start_game()
            elif time.time() - self.start_time >= 10:  # 10초 대기
                self.game_started = True
            return

        if self.is_paused or self.is_game_over:
            return

        # 적 스폰
        self.spawn_timer += 1
        if self.spawn_timer >= 60:  # 1초마다 스폰 (60 프레임 기준)
            self.spawn_enemy()
            self.spawn_timer = 0

        # 타워 업데이트
        for tower in self.towers:
            tower.update(self.enemies)

        # 적 업데이트
        for enemy in self.enemies[:]:  # 복사본으로 순회
            enemy.update()

            # 적이 도착지점에 도달
            if enemy.has_reached_end():
                self.player_health -= 1
                self.enemies.remove(enemy)
                if self.player_health <= 0:
                    self.game_over()

            # 적이 죽음
            elif enemy.is_dead:
                self.player_gold += enemy.value
                self.enemies.remove(enemy)

    def render(self):
        clear_canvas()

        # 맵 그리기
        self.map.draw()

        # 타워 그리기
        for tower in self.towers:
            tower.draw()

        # 적 그리기
        for enemy in self.enemies:
            enemy.draw()

        # UI 그리기
        self.draw_ui()

        # 메뉴 그리기
        if self.menu.is_visible:
            self.menu.draw()

        # 게임 시작 전 카운트다운
        if not self.game_started and self.start_time:
            self.draw_countdown()

        # 게임 오버 화면
        if self.is_game_over:
            self.draw_game_over()

        update_canvas()

    def draw_ui(self):
        # 체력 표시
        self.health_image.draw(30, 570)
        draw_text(f"x {self.player_health}", 60, 570)

        # 골드 표시
        self.gold_image.draw(30, 530)
        draw_text(f"x {self.player_gold}", 60, 530)

        # 보스 버튼
        self.boss_button.draw(50, 50)

    def draw_countdown(self):
        time_left = 10 - int(time.time() - self.start_time)
        if time_left > 0:
            draw_text(f"Game starts in: {time_left}", 400, 300, (255, 255, 255))

    def draw_game_over(self):
        draw_text("Game Over!", 400, 300, (255, 0, 0))
        draw_text("Click to return to main menu", 400, 250, (255, 255, 255))

    def can_afford_tower(self, tower_type):
        return self.player_gold >= tower_type.cost

    def place_tower(self, tower_type):
        if self.selected_tile and not self.selected_tile.has_tower:
            tower = Tower(
                tower_type.image,
                self.selected_tile.x,
                self.selected_tile.y,
                tower_type.range,
                tower_type.damage,
                tower_type.fire_rate
            )
            self.towers.append(tower)
            self.selected_tile.has_tower = True
            self.player_gold -= tower_type.cost
            self.menu.hide()
            self.selected_tile = None

    def spawn_enemy(self):
        if len(self.enemies) < 20:  # 최대 동시 출현 적 수 제한
            enemy = Enemy(self.map.get_spawn_point(), self.stage_number)
            self.enemies.append(enemy)

    def spawn_boss(self):
        if not self.boss_spawned:
            boss = Boss(self.map.get_spawn_point(), self.stage_number)
            self.enemies.append(boss)
            self.boss_spawned = True

    def game_over(self):
        self.is_game_over = True
        # 게임 오버 처리 (점수 저장 등)

    def is_boss_button_clicked(self, x, y):
        return 20 <= x <= 80 and 20 <= y <= 80


def draw_text(text, x, y, color=(0, 0, 0)):
    font = load_font('ARIAL.TTF', 30)
    font.draw(x, y, text, color)