import time

from pico2d import load_image

import game_clear_mode
from game_scene import draw_text

# 게임 상태 추가
GAME_OVER = 1
GAME_CLEAR = 2
RUNNING = 3
player_health = 10
player_gold = 200
boss_spawned = False  # Boss가 소환되었는지 여부를 저장

def change_mode(mode):
    global stack
    if len(stack) > 0:
        stack[-1].finish()
        stack.pop()
    stack.append(mode)
    mode.init()

def push_mode(mode):
    global stack
    if len(stack) > 0:
        stack[-1].pause()
    stack.append(mode)
    mode.init()

def pop_mode():
    global stack
    if len(stack) > 0:
        stack[-1].finish()
        stack.pop()
    if len(stack) > 0:
        stack[-1].resume()

def quit():
    global running
    running = False

def run(start_mode):
    global running, stack
    running = True
    stack = [start_mode]
    start_mode.init()

    global frame_time
    frame_time = 0.0
    current_time = time.time()

    while running:
        stack[-1].handle_events()
        stack[-1].update()

        # 게임 종료 조건 체크 (예: 체력이 0이 되거나 보스를 처치한 경우)
        if check_game_over():
            change_mode(game_clear_mode)  # 게임 오버 모드로 전환
        elif check_game_clear():
             change_mode(game_clear_mode)  # 게임 클리어 모드로 전환

        stack[-1].draw()
        frame_time = time.time() - current_time
        current_time += frame_time

    while len(stack) > 0:
        stack[-1].finish()
        stack.pop()

def check_game_over():
    # 적이 목표지점에 도달했거나 플레이어 체력이 0이 될 때 게임 오버 처리
    if player_health <= 0:
        return True
    return False

def check_game_clear():
    if not boss_spawned:
        return False  # Boss가 소환되지 않았다면 클리어 조건 무효
    from game_world import get_enemies
    for enemy in get_enemies():
        if enemy.type == 'Boss' and enemy.alive:
            return False  # Boss가 살아있으면 클리어되지 않음
    print("Round cleared!")
    return True

def add_gold(amount):
    global player_gold
    player_gold += amount
    print(f"Gold updated: {player_gold}")

def deduct_gold(amount):
    global player_gold
    if player_gold >= amount:
        player_gold -= amount
        print(f"Gold deducted: {player_gold}")
        return True
    else:
        print("Not enough gold!")
        return False

def draw_ui():
    health_image = load_image('life.png')
    gold_image = load_image('money.png')

    # 체력 표시
    health_image.draw(50, 550, 40, 40)
    draw_text(f"HP: {player_health}", 90, 550, (255, 255, 255))

    # 골드 표시
    gold_image.draw(50, 500, 40, 40)
    draw_text(f"Gold: {player_gold}", 90, 500, (255, 255, 255))