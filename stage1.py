from pico2d import *

from tile import Stage, Tile
from tower import Tower
import game_world
import game_framework
import stage_select


def handle_events():
    global running

    Stage.handle_events(stage)

    events = get_events()

    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(stage_select)
        else:
            pass

def init():
    global running
    global tower
    global stage
    global background

    running = True

    background = load_image('black.png')

    stage = Stage('map1')
    game_world.add_object(stage, 1)

def finish():
    game_world.clear()
    pass


def update():
    game_world.update() # 객체들의 위치가 다 결정됐다. 따라서 이어서 충돌 검사를 하면 됨


def draw():
    clear_canvas()
    background.draw(400, 300)
    game_world.render()
    update_canvas()

def pause():
    pass

def resume():
    pass

