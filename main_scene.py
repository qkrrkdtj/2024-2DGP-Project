from pico2d import *

import game_framework
import stage_select

def init():
    global background, play_button
    background = load_image('black.png')
    play_button = load_image('continue2.png')


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN:
            x, y = event.x, get_canvas_height() - event.y
            if is_play_button_clicked(x, y):
                 # 플레이 버튼이 클릭되면 StageSelectScene으로 전환
                game_framework.change_mode(stage_select)

def is_play_button_clicked(x, y):
    return 150 <= x <= 650 and 311 <= y <= 386


def update():
     pass  # 필요하면 추가적인 업데이트 로직

def draw():
    clear_canvas()
    background.draw(400, 300)
    play_button.draw(400, 350)


    update_canvas()

def finish():
    global background, play_button
    del background, play_button