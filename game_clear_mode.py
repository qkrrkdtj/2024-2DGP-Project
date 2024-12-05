from pico2d import *

import game_framework
import main_scene
import stage_select

def init():
    global background1, to_select, win_sound, sound_play
    background1 = load_image('black.png')
    to_select = load_image('continue2.png')
    win_sound = load_wav('win.wav')
    win_sound.set_volume(32)
    sound_play = False
    game_framework.player_health = 10
    game_framework.player_gold = 100

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
                 print("Switching to stage_select mode from game_clear_mode")
                 game_framework.change_mode(stage_select)
                 print("Successfully switched")

def is_play_button_clicked(x, y):
    return 150 <= x <= 650 and 311 <= y <= 386


def update():
     pass  # 필요하면 추가적인 업데이트 로직

def draw():
    global win_sound, sound_play
    clear_canvas()
    if not sound_play:
        win_sound.play()
        sound_play = True
    background1.draw(400, 300)
    to_select.draw(400, 350)

    update_canvas()

def finish():
    global background1, to_select, sound_play
    del background1, to_select
    sound_play = False