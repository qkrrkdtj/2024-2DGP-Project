from pico2d import *


import game_framework



def init():
    global stage_buttons, background, menu_background, start_button, slide, slide_back
    global is_menu_active, selected_stage

    background = load_image('black.png')
    stage_buttons = [
        load_image(f'map{i+1}_iddle.png') for i in range(4)
    ]
    menu_background = load_image('side_menu.png')
    start_button = load_image('continue.png')
    slide = load_image('arrow2_slide_R.png')
    slide_back = load_image('arrow_slide_R.png')

    is_menu_active = False
    selected_stage = -1

def handle_events():
    global events
    global is_menu_active, selected_stage

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            if is_menu_active:
                is_menu_active = False
            else:
                game_framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN:
            x, y = event.x, get_canvas_height() - event.y

            if is_menu_active:
                if is_start_button_clicked(x, y):
                    open_stage(selected_stage)
                elif is_slide_button_clicked(x, y):  # 슬라이드 버튼이 클릭되었는지 확인
                    is_menu_active = False
            else:
                for i, button in enumerate(stage_buttons):
                    if is_stage_button_clicked(i, x, y):
                        is_menu_active = True
                        # 선택한 스테이지로 GameScene 전환
                        selected_stage = i

def is_stage_button_clicked(stage_index, x, y):
    button_x = 200 + (stage_index % 2) * 400
    button_y = 450 - (stage_index // 2) * 300
    return button_x - 150 <= x <= button_x + 150 and button_y - 75 <= y <= button_y + 75

def is_start_button_clicked(x, y):
    # 버튼의 영역 좌표
    x1, y1 = 500, 130  # 좌상단 좌표
    x2, y2 = 780, 200  # 우하단 좌표

    # 클릭한 좌표가 버튼 영역 내에 있는지 확인
    return x1 <= x <= x2 and y1 <= y <= y2

def is_slide_button_clicked(x, y):
    # 버튼의 영역 좌표
    x1, y1 = 410, 20  # 좌상단 좌표
    x2, y2 = 470, 100  # 우하단 좌표

    # 클릭한 좌표가 버튼 영역 내에 있는지 확인
    return x1 <= x <= x2 and y1 <= y <= y2

def open_stage(stage_index):
    if stage_index == 0:
        import stage1
        game_framework.change_mode(stage1)
    elif stage_index == 1:
        import stage2
        game_framework.change_mode(stage2)
    elif stage_index == 2:
        import stage3
        game_framework.change_mode(stage3)
    elif stage_index == 3:
        import stage4
        game_framework.change_mode(stage4)

def draw_text(text, x, y, color=(0, 0, 0)):
    font = load_font('ARIAL.TTF', 30)
    font.draw(x, y, text, color)

def update():
    pass

def draw():
    clear_canvas()
    background.draw(400, 300)
    button_width, button_height = 300, 150  # 버튼의 고정된 너비와 높이
    stage_labels = ["map1", "map2", "map3", "map4"]  # 각 버튼에 대응하는 텍스트

    for i, button in enumerate(stage_buttons):
        button_x = 200 + (i % 2) * 400
        button_y = 450 - (i // 2) * 300
        button.draw(button_x, button_y, button_width, button_height)  # 고정된 크기로 버튼 그리기

        # 버튼 아래에 텍스트 그리기 (버튼 위치에서 버튼 높이의 절반만큼 아래로 이동)
        if i < len(stage_labels):
            draw_text(stage_labels[i], button_x, button_y - button_height // 2 - 10, (255, 255, 255))


    if is_menu_active:
        draw_menu_overlay()

    update_canvas()

def draw_button_image(image, x1, y1, x2, y2):
    width = x2 - x1
    height = y2 - y1
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # 이미지를 지정된 크기와 중심 좌표로 그립니다.
    image.draw(center_x, center_y, width, height)


def draw_menu_overlay():

    draw_button_image(menu_background, 400, 0, 800, 600)


    draw_button_image(start_button, 500, 130, 780, 200)


    draw_button_image(slide_back, 410, 15, 470, 95)
    draw_button_image(slide, 410, 20, 470, 100)


    # 선택된 스테이지 텍스트 표시
    draw_text(f"Stage {selected_stage + 1} Selected", 520, 400, (255, 255, 255))


def finish():
    global background, stage_buttons
    del background, stage_buttons

def pause():
    pass

def resume():
    pass