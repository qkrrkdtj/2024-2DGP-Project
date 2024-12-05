from pico2d import *
import game_framework
import game_world
from game_world import draw_text
from tower import Tower


class Tile:
    tile_size = 50

    def __init__(self, x, y, tile_type):
        self.x = x
        self.y = y
        self.tile_type = tile_type

        # 각 tile_type에 맞는 이미지를 로드
        if tile_type == 'S':
            self.image_base = load_image('spawner_base.png')
            self.image = load_image('spawner.png')
        elif tile_type == 'G':
            self.image = load_image('ground.png')
        elif tile_type == 'O':
            self.image = load_image('turret_support.png')
        elif tile_type == 'C':
            self.image = load_image('castle.png')

        elif tile_type == '#':
            self.image = None  # 벽이나 장애물은 이미지를 없앰
        else:
            self.image = load_image('default_tile.png')  # 기본 이미지

    def draw(self):
        if self.tile_type == 'S' and self.image_base:  # 스포너 타일의 경우
            self.image_base.draw(self.x, self.y, Tile.tile_size, Tile.tile_size)  # base 먼저 그리기
        if self.image:  # 공통적으로 이미지를 그리기
            self.image.draw(self.x, self.y, Tile.tile_size, Tile.tile_size)

    def get_bounds(self):
        # 타일의 경계 좌표를 반환합니다.
        return (
            self.x - Tile.tile_size // 2,  # left
            self.y - Tile.tile_size // 2,  # bottom
            self.x + Tile.tile_size // 2,  # right
            self.y + Tile.tile_size // 2  # top
        )

class Stage:
    def __init__(self, file_path):
        global menu_manager

        self.tiles = []
        self.towers = []
        self.load_stage_map(file_path)
        self.menu_manager = MenuManager()  # MenuManager 인스턴스 생성
        self.health = game_framework.player_health
        self.path = []



    def load_stage_map(self, file_path):
        map_data = []
        max_width = 15  # 원본 맵의 너비

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                # 줄바꿈 문자만 제거
                current_line = line.rstrip('\n')
                # 현재 줄의 길이가 max_width보다 작으면 오른쪽에 공백 추가
                padded_line = current_line.ljust(max_width)
                map_data.append(padded_line)

        # 맵의 높이가 8줄이 되도록 빈 줄 추가
        while len(map_data) < 8:
            map_data.append(" " * max_width)

        height = len(map_data)

        # 화면 크기에 맞게 타일 위치 조정
        screen_width = 800
        screen_height = 600
        start_x = (screen_width - (max_width * Tile.tile_size)) // 2
        start_y = (screen_height - (height * Tile.tile_size)) // 2

        for y in range(height):
            for x, tile_type in enumerate(map_data[y]):
                if tile_type != ' ':
                    # 타일의 실제 픽셀 위치 계산 (중앙 정렬)
                    tile_x = start_x + (x * Tile.tile_size) + Tile.tile_size // 2
                    tile_y = start_y + ((height - y - 1) * Tile.tile_size) + Tile.tile_size // 2
                    tile = Tile(tile_x, tile_y, tile_type)
                    self.tiles.append(tile)

    def handle_events(self):
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                game_framework.quit()
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                if self.menu_manager.menu_visible:
                    self.menu_manager.hide_menu()
                else:
                    game_framework.quit()
            elif event.type == SDL_MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.x, 600 - event.y  # y좌표 변환

                if self.menu_manager.menu_visible:
                    self.menu_manager.handle_click(mouse_x, mouse_y, self)
                else:
                    for tile in self.tiles:
                        if self.is_tile_clicked(tile, mouse_x, mouse_y):
                            if tile.tile_type == 'O':  # 설치 가능한 타일
                                self.menu_manager.show_tower_build_menu(tile.x, tile.y)

                    for tower in self.towers:
                        if tower.is_clicked(mouse_x, mouse_y):
                            self.menu_manager.show_tower_menu(tower)
                            return

    def is_tile_clicked(self, tile, mouse_x, mouse_y):
        left = tile.x - Tile.tile_size // 2
        right = tile.x + Tile.tile_size // 2
        bottom = tile.y - Tile.tile_size // 2
        top = tile.y + Tile.tile_size // 2
        return left <= mouse_x <= right and bottom <= mouse_y <= top

    def draw(self):
        # 타일 그리기
        for tile in self.tiles:
            tile.draw()
        # 메뉴 그리기
        self.menu_manager.draw()
        # 타워 그리기
        for tower in self.towers:
            tower.draw()

    def update(self):
        pass

    def add_tower(self, x, y, tower_type):
        cost = self.menu_manager.tower_info[tower_type]['cost']  # 비용 확인
        if game_framework.deduct_gold(cost):  # 중앙 관리에서 골드 차감
            new_tower = Tower(x, y, tower_type)
            self.towers.append(new_tower)  # 타워 리스트에 추가
            print(f"Tower of type '{tower_type}' added at ({x}, {y}). Remaining gold: {game_framework.player_gold}")
            game_world.add_object(new_tower, 1)
            return True
        else:
            print(f"Not enough gold to build {tower_type} tower.")
            return False


class MenuManager:
    def __init__(self):
        self.tower_info = None
        self.menu_visible = False
        self.current_menu_type = None  # 'build' 또는 'upgrade'
        self.selected_position = None  # (x, y) 좌표
        self.selected_tower = None
        self.load_images()
        self.setup_tower_info()
        self.build_sound = load_wav('build.wav')
        self.build_sound.set_volume(32)
        self.sell_sound = load_wav('sell.wav')
        self.sell_sound.set_volume(32)
        self.upgrade_sound = load_wav('upgrade.wav')
        self.upgrade_sound.set_volume(32)

    def load_images(self):
        global slide, slide_back, menu_background, tower_icons
        slide = load_image('arrow2_slide_R.png')
        slide_back = load_image('arrow_slide_R.png')
        # 메뉴 배경 및 UI 이미지
        menu_background = load_image('side_menu.png')
        # 타워 아이콘 이미지
        tower_icons = {
            'Normal': load_image('turret1_select.png'),
            'Sniper': load_image('turret2_select.png'),
            'Triple': load_image('turret3_select.png'),
        }

    def setup_tower_info(self):
        self.tower_info = {
            'Normal': {
                'cost': 100,
                'description': 'Basic Tower\nDamage: 10\nRange: 150',
                'stats': {'damage': 10, 'range': 150, 'attack_speed': 1.0}
            },
            'Sniper': {
                'cost': 150,
                'description': 'Long Range Tower\nDamage: 30\nRange: 300',
                'stats': {'damage': 30, 'range': 300, 'attack_speed': 0.5}
            },
            'Triple': {
                'cost': 200,
                'description': 'Multi Target Tower\nDamage: 8\nRange: 120',
                'stats': {'damage': 8, 'range': 120, 'attack_speed': 0.8}
            },

        }

    def show_tower_build_menu(self, x, y):
        self.menu_visible = True
        self.current_menu_type = 'build'
        self.selected_position = (x, y)
        self.selected_tower = None

    def show_tower_menu(self, tower):
        self.menu_visible = True
        self.current_menu_type = 'upgrade'
        self.selected_tower = tower

    def hide_menu(self):
        self.menu_visible = False
        self.current_menu_type = None
        self.selected_position = None
        self.selected_tower = None

    def handle_click(self, click_x, click_y, stage):
        if not self.menu_visible:
            return False

        # 메뉴 영역 내 클릭 확인
        if 480 <= click_x <= 800 and 0 <= click_y <= 600:
            if self.current_menu_type == 'build':
                return self.handle_build_menu_click(click_x, click_y, stage)
            elif self.current_menu_type == 'upgrade':
                return self.handle_upgrade_menu_click(click_x, click_y, stage)
            return True

        else:
            self.hide_menu()
            return False


    def handle_build_menu_click(self, click_x, click_y, stage):
        # 각 타워 버튼의 위치와 크기
        button_size = 100
        buttons = {
            'Normal': (560, 450),
            'Sniper': (720, 450),
            'Triple': (560, 150),
        }

        for tower_type, button_pos in buttons.items():
            button_x, button_y = button_pos

            if (button_x - button_size // 2 <= click_x <= button_x + button_size // 2 and
                button_y - button_size // 2 <= click_y <= button_y + button_size // 2):
                if self.can_buy_tower(tower_type):
                    return self.build_tower(stage, tower_type)


    def can_buy_tower(self, tower_type):
        return game_framework.player_gold >= self.tower_info[tower_type]['cost']

    def build_tower(self, stage, tower_type):
        if self.selected_position:
            x, y = self.selected_position
            if stage.add_tower(x, y, tower_type):  # Stage에 설치 요청
                print(f"{tower_type} tower successfully built!")
                self.hide_menu()  # 메뉴 닫기
                self.build_sound.play()
                return True
        else:
            print("No position selected for tower placement.")
        return False

    def draw(self):
        if self.menu_visible:
            if self.current_menu_type == 'build':
                self.draw_build_menu()
            elif self.current_menu_type == 'upgrade':
                self.draw_upgrade_menu()

    def update(self):
        pass


    def draw_menu_image(self, image, x1, y1, x2, y2):
        width = x2 - x1
        height = y2 - y1
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        # 이미지를 지정된 크기와 중심 좌표로 그립니다.
        image.draw(center_x, center_y, width, height)

    def draw_menu_overlay(self):

        self.draw_menu_image(menu_background, 400, 0, 800, 600)

        self.draw_menu_image(slide_back, 410, 15, 470, 95)
        self.draw_menu_image(slide, 410, 20, 470, 100)

    def draw_build_menu(self):
        button_size = 100
        self.draw_menu_overlay()

        towers = {
            'Normal': 1,
            'Sniper': 2,
            'Triple': 3,
        }

        button_x = [560, 720, 560]
        button_y = [450, 450, 150]

        for tower, i in towers.items():
            # 아이콘 그리기
            tower_icons[tower].draw(button_x[i-1], button_y[i-1], button_size, button_size)

            # 가격 표시 (텍스트)
            cost = str(self.tower_info[tower]['cost'])
            draw_text(f"{cost}G", button_x[i - 1], button_y[i - 1] - button_size // 2 - 10)

    def handle_upgrade_menu_click(self, click_x, click_y, stage):
        # 업그레이드 또는 판매 버튼 영역 정의
        upgrade_button = (560, 150)  # 업그레이드 버튼 위치
        sell_button = (720, 150)  # 판매 버튼 위치
        button_size = 100

        if (upgrade_button[0] - button_size // 2 <= click_x <= upgrade_button[0] + button_size // 2 and
            upgrade_button[1] - button_size // 2 <= click_y <= upgrade_button[1] + button_size // 2):
            # 업그레이드 처리
            self.upgrade_tower()
            self.upgrade_sound.play()
            return True

        if (sell_button[0] - button_size // 2 <= click_x <= sell_button[0] + button_size // 2 and
            sell_button[1] - button_size // 2 <= click_y <= sell_button[1] + button_size // 2):
            # 판매 처리
            self.sell_tower(stage)
            self.sell_sound.play()
            return True

        return False

    def upgrade_tower(self):
        if self.selected_tower and self.selected_tower.upgrade_level < 5:
            upgrade_cost = self.selected_tower.get_upgrade_cost()  # 업그레이드 비용
            if game_framework.player_gold >= upgrade_cost:
                game_framework.deduct_gold(upgrade_cost)  # 골드 차감
                self.selected_tower.upgrade()
                print(f"Tower upgraded! Remaining gold: {game_framework.player_gold}")
            else:
                print("Not enough gold to upgrade!")

    def sell_tower(self, stage):
        if self.selected_tower:
            sell_value = self.selected_tower.total_cost  # 판매 가격 예시
            refund = (sell_value * 70) // 100
            game_framework.add_gold(refund)
            stage.towers.remove(self.selected_tower)
            game_world.remove_object(self.selected_tower)
            print(f"Tower sold! Gold increased by {sell_value* 70 // 100}.")
            self.hide_menu()

    def draw_upgrade_menu(self):
        button_size = 100
        self.draw_menu_overlay()
        tower = self.selected_tower
        if tower:
            stats = (f"tower type: {tower.tower_type}\ndamage: {tower.damage}\n"
                     f"range: {tower.range}\nattack speed: {tower.attack_speed}\n"
                     f"upgrade: {tower.upgrade_level}\nselling price: {tower.total_cost*70//100}\n")

            stats_lines = stats.split('\n')  # 텍스트를 줄별로 나눔
            stats_x, stats_y = 530, 500

            # 각 줄을 순차적으로 그리기
            for i, line in enumerate(stats_lines):
                draw_text(line, stats_x, stats_y - (i * 30))  # 각 줄의 Y좌표를 30씩 차이 두고 출력

        # 업그레이드 버튼
        upgrade_button_x, upgrade_button_y = 560, 150
        tower_icons['Normal'].draw(upgrade_button_x, upgrade_button_y, button_size, button_size)
        draw_text("Upgrade", upgrade_button_x, upgrade_button_y - 70)

        # 판매 버튼
        sell_button_x, sell_button_y = 720, 150
        tower_icons['Sniper'].draw(sell_button_x, sell_button_y, button_size, button_size)
        draw_text("Sell", sell_button_x, sell_button_y - 70)



