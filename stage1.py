from pico2d import *

from enemy import Enemy
from spawner import Spawner
from tile import Stage, Tile
from tower import Tower
import game_world
import game_framework
import stage_select


def handle_events():
    global running, boss_spawned

    Stage.handle_events(stage)
    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(stage_select)
        elif event.type == SDL_MOUSEBUTTONDOWN:  # 마우스 클릭 이벤트
            x, y = event.x, 600 - event.y  # Pico2D의 y 좌표는 반전되어 있음
            if 50 <= x <= 150 and 50 <= y <= 100 and not boss_spawned:  # 버튼 클릭 영역
                spawn_boss()
        else:
            pass

def init():
    global running, tower, stage, background, spawner, boss_button, boss_spawned
    global path
    path = [(200, 375), (250, 375), (300, 375), (350, 375), (350, 325), (350, 275), (400, 275), (450, 275), (500, 275)]

    running = True
    background = load_image('black.png')
    stage = Stage('map1')
    spawner = Spawner(path)  # 스포너 초기화
    boss_button = load_image('wave_button2.png')  # 보스 버튼 이미지 로드
    boss_spawned = False  # 보스가 생성되었는지 여부

    game_world.add_object(stage, 1)

def finish():
    game_world.clear()
    pass

def update():
    global boss_spawned
    spawner.update()
    game_world.update()

    # 보스 처치 후 클리어 처리
    if boss_spawned:
        for obj in game_world.world[1]:
            if isinstance(obj, Enemy) and obj.type == 'Boss' and not obj.alive:
                print("Boss defeated! Stage Cleared!")
                boss_spawned = False
                break

def draw():
    clear_canvas()
    background.draw(400, 300)
    game_world.render()
    boss_button.draw(100, 75, 100, 50)  # 보스 버튼 그리기 (x=100, y=75)
    update_canvas()

def pause():
    pass

def resume():
    pass

def spawn_boss():
    global boss_spawned
    boss_spawned = True
    boss = Enemy(path[0][0], path[0][1], 'Boss', 1000, 10, path)
    game_world.add_object(boss, 1)