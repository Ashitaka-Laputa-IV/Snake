import pygame
import sys
import random
import time
import os
import math

# GitHub风格颜色方案 - 使用GitHub的设计语言
BACKGROUND_COLOR = pygame.Color(13, 17, 23)  # GitHub深色背景 (#0d1117)
GRID_COLOR = pygame.Color(22, 27, 34)  # GitHub网格线颜色 (#161b22)
SNAKE_HEAD_COLOR = pygame.Color(56, 139, 253)  # GitHub蓝色 (#388bfd)
SNAKE_BODY_COLOR = pygame.Color(88, 166, 255)  # GitHub浅蓝色 (#58a6ff)
FOOD_COLOR = pygame.Color(239, 108, 0)  # GitHub橙色 (#ef6c00)
TEXT_COLOR = pygame.Color(229, 231, 235)  # GitHub文本颜色 (#e5e7eb)
SCORE_BG_COLOR = pygame.Color(22, 27, 34)  # 分数背景色 (#161b22)
BUTTON_COLOR = pygame.Color(35, 134, 54)  # GitHub绿色按钮 (#238636)
BUTTON_HOVER_COLOR = pygame.Color(46, 160, 67)  # GitHub绿色悬停 (#2ea043)

# 游戏窗口设置
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
WINDOW_SIZE = [WINDOW_WIDTH, WINDOW_HEIGHT]

# 游戏初始化
INIT_ERRORS = pygame.init()
if INIT_ERRORS[1] > 0:
    print(f'[!] {INIT_ERRORS[1]} errors happened when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] game initialising successfully!')

# 设置窗口及其信息
pygame.display.set_caption('Snake Game')
GAME_WINDOW = pygame.display.set_mode(WINDOW_SIZE)

# 设置帧率控制器
FPS_CLOCK = pygame.time.Clock()

# 游戏速度设置
INITIAL_SPEED = 8
SPEED_INCREASE_THRESHOLD = 5  # 每吃多少食物增加速度

# 蛇相关设置
BODY_SIZE = 15
INITIAL_HEAD_POS = [120, 60]
INITIAL_BODY_POS = [[120, 60], [105, 60], [90, 60]]

# 方向常量
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

# 游戏状态变量
head_pos = INITIAL_HEAD_POS.copy()
body_pos = [pos.copy() for pos in INITIAL_BODY_POS]
direction = RIGHT
next_direction = RIGHT
score = 0
game_started = False
game_paused = False

# 食物相关
food_pos = [
    random.randrange(0, WINDOW_WIDTH // BODY_SIZE) * BODY_SIZE,
    random.randrange(0, WINDOW_HEIGHT // BODY_SIZE) * BODY_SIZE
]
food_flag = True

# 蛇移动相关
move_timer = 0
move_delay = 100  # 初始移动延迟（毫秒）

# 蛇移动平滑度
snake_trail = []  # 存储蛇的移动轨迹
trail_length = 3  # 轨迹长度
smooth_factor = 0.3  # 平滑因子

# 游戏速度优化
BASE_MOVE_DELAY = 100  # 基础移动延迟
MIN_MOVE_DELAY = 40    # 最小移动延迟（最快速度）
MOVE_DELAY_REDUCTION = 8  # 每次速度提升的延迟减少量
SPEED_LEVELS = 5       # 速度等级数量

# 帧率优化
TARGET_FPS = 60       # 目标帧率
frame_skip = False     # 是否跳帧
performance_mode = False  # 性能模式


def get_font(size):
    """
    跨平台字体加载函数
    :param size: 字体大小
    :return: 字体对象
    """
    try:
        if os.name == 'nt':  # Windows
            return pygame.font.SysFont('Segoe UI', size)
        else:  # Linux/Mac
            return pygame.font.SysFont('Roboto', size)
    except:
        # 如果系统字体加载失败，使用默认字体
        return pygame.font.Font(None, size)


def draw_grid():
    """绘制GitHub风格网格背景"""
    for x in range(0, WINDOW_WIDTH, BODY_SIZE):
        pygame.draw.line(GAME_WINDOW, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, BODY_SIZE):
        pygame.draw.line(GAME_WINDOW, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)


def draw_food():
    """绘制GitHub风格食物 - 简单的正方形"""
    rect = pygame.Rect(food_pos[0] + 2, food_pos[1] + 2, BODY_SIZE - 4, BODY_SIZE - 4)
    pygame.draw.rect(GAME_WINDOW, FOOD_COLOR, rect)
    
    # 添加简单的内部装饰
    inner_size = BODY_SIZE - 8
    inner_rect = pygame.Rect(food_pos[0] + 4, food_pos[1] + 4, inner_size, inner_size)
    pygame.draw.rect(GAME_WINDOW, pygame.Color(255, 255, 255, 100), inner_rect, 2)


def draw_snake():
    """绘制GitHub风格蛇"""
    global snake_trail
    
    # 添加蛇头到轨迹
    if len(snake_trail) == 0 or snake_trail[0] != head_pos:
        snake_trail.insert(0, [head_pos[0], head_pos[1]])
    
    # 限制轨迹长度
    while len(snake_trail) > trail_length:
        snake_trail.pop()
    
    for i, pos in enumerate(body_pos):
        if i == 0:  # 蛇头
            # 绘制蛇头为GitHub风格矩形
            rect = pygame.Rect(pos[0] + 1, pos[1] + 1, BODY_SIZE - 2, BODY_SIZE - 2)
            pygame.draw.rect(GAME_WINDOW, SNAKE_HEAD_COLOR, rect)
            
            # 添加简单的眼睛
            eye_size = 2
            if direction == RIGHT:
                eye1_pos = (pos[0] + BODY_SIZE - 4, pos[1] + 4)
                eye2_pos = (pos[0] + BODY_SIZE - 4, pos[1] + BODY_SIZE - 6)
            elif direction == LEFT:
                eye1_pos = (pos[0] + 4, pos[1] + 4)
                eye2_pos = (pos[0] + 4, pos[1] + BODY_SIZE - 6)
            elif direction == UP:
                eye1_pos = (pos[0] + 4, pos[1] + 4)
                eye2_pos = (pos[0] + BODY_SIZE - 6, pos[1] + 4)
            else:  # DOWN
                eye1_pos = (pos[0] + 4, pos[1] + BODY_SIZE - 4)
                eye2_pos = (pos[0] + BODY_SIZE - 6, pos[1] + BODY_SIZE - 4)
                
            pygame.draw.rect(GAME_WINDOW, BACKGROUND_COLOR, (eye1_pos[0], eye1_pos[1], eye_size, eye_size))
            pygame.draw.rect(GAME_WINDOW, BACKGROUND_COLOR, (eye2_pos[0], eye2_pos[1], eye_size, eye_size))
        else:  # 蛇身
            # 渐变颜色 - GitHub风格中的简单渐变
            color_factor = max(0.7, 1.0 - (i / len(body_pos)) * 0.3)
            r = int(SNAKE_BODY_COLOR.r * color_factor)
            g = int(SNAKE_BODY_COLOR.g * color_factor)
            b = int(SNAKE_BODY_COLOR.b * color_factor)
            color = pygame.Color(r, g, b)
            
            # 绘制GitHub风格矩形
            rect = pygame.Rect(pos[0] + 1, pos[1] + 1, BODY_SIZE - 2, BODY_SIZE - 2)
            pygame.draw.rect(GAME_WINDOW, color, rect)


def draw_start_screen():
    """绘制GitHub风格游戏开始界面"""
    # 绘制背景
    GAME_WINDOW.fill(BACKGROUND_COLOR)
    
    # 标题
    title_font = get_font(60)
    title_text = title_font.render('SNAKE', True, SNAKE_HEAD_COLOR)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
    GAME_WINDOW.blit(title_text, title_rect)
    
    # 副标题
    subtitle_font = get_font(30)
    subtitle_text = subtitle_font.render('GITHUB STYLE', True, TEXT_COLOR)
    subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3 + 50))
    GAME_WINDOW.blit(subtitle_text, subtitle_rect)
    
    # 开始按钮
    button_font = get_font(25)
    button_text = button_font.render('PRESS SPACE TO START', True, TEXT_COLOR)
    button_rect = button_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    
    # 绘制GitHub风格按钮背景
    button_bg_rect = pygame.Rect(
        button_rect.left - 20, button_rect.top - 10,
        button_rect.width + 40, button_rect.height + 20
    )
    pygame.draw.rect(GAME_WINDOW, BUTTON_COLOR, button_bg_rect)
    GAME_WINDOW.blit(button_text, button_rect)
    
    # 控制说明
    control_font = get_font(18)
    control_text1 = control_font.render('USE ARROW KEYS OR WASD TO MOVE', True, TEXT_COLOR)
    control_rect1 = control_text1.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))
    GAME_WINDOW.blit(control_text1, control_rect1)
    
    control_text2 = control_font.render('PRESS P TO PAUSE, ESC TO QUIT', True, TEXT_COLOR)
    control_rect2 = control_text2.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4))
    GAME_WINDOW.blit(control_text2, control_rect2)
    
    pygame.display.flip()


def draw_pause_screen():
    """绘制GitHub风格暂停界面"""
    # 创建半透明覆盖层
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    GAME_WINDOW.blit(overlay, (0, 0))
    
    # 暂停文本
    pause_font = get_font(60)
    pause_text = pause_font.render('PAUSED', True, TEXT_COLOR)
    pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    GAME_WINDOW.blit(pause_text, pause_rect)
    
    # 继续按钮
    resume_font = get_font(25)
    resume_text = resume_font.render('PRESS P TO RESUME', True, TEXT_COLOR)
    resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))
    
    # 绘制GitHub风格按钮背景
    button_bg_rect = pygame.Rect(
        resume_rect.left - 20, resume_rect.top - 10,
        resume_rect.width + 40, resume_rect.height + 20
    )
    pygame.draw.rect(GAME_WINDOW, BUTTON_COLOR, button_bg_rect)
    GAME_WINDOW.blit(resume_text, resume_rect)
    
    pygame.display.flip()


def handle_events():
    """处理游戏事件"""
    global direction, next_direction, game_started, game_paused, performance_mode
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # 更新方向
        elif event.type == pygame.KEYDOWN:
            if not game_started:
                if event.key == pygame.K_SPACE:
                    game_started = True
            elif game_paused:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    game_paused = False
            else:
                # 方向控制 - 改进为更响应的控制
                if event.key == pygame.K_UP or event.key == ord('w'):
                    if direction != DOWN:
                        next_direction = UP
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    if direction != UP:
                        next_direction = DOWN
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    if direction != RIGHT:
                        next_direction = LEFT
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    if direction != LEFT:
                        next_direction = RIGHT
                if event.key == pygame.K_p:
                    game_paused = True
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                # 性能模式切换
                if event.key == pygame.K_F1:
                    performance_mode = not performance_mode
                    print(f"Performance mode: {'ON' if performance_mode else 'OFF'}")


def move_snake():
    """移动蛇"""
    global head_pos, move_timer, move_delay, snake_trail, food_flag, score
    
    # 更新方向
    direction = next_direction
    
    # 计算新头部位置
    new_head_pos = [body_pos[0][0], body_pos[0][1]]  # 复制当前位置
    
    if direction == UP:
        new_head_pos[1] -= BODY_SIZE
    elif direction == DOWN:
        new_head_pos[1] += BODY_SIZE
    elif direction == RIGHT:
        new_head_pos[0] += BODY_SIZE
    elif direction == LEFT:
        new_head_pos[0] -= BODY_SIZE
    
    # 更新蛇头位置
    body_pos.insert(0, new_head_pos)
    head_pos = new_head_pos  # 更新head_pos引用
    
    # 检测蛇头是否与食物重合由此决定是否删除蛇尾巴
    if head_pos[0] == food_pos[0] and head_pos[1] == food_pos[1]:
        update_score()
        food_flag = False
        # 每吃一定数量的食物增加速度
        if score % SPEED_INCREASE_THRESHOLD == 0:
            # 计算新的移动延迟，确保不会低于最小延迟
            new_delay = max(MIN_MOVE_DELAY, move_delay - MOVE_DELAY_REDUCTION)
            move_delay = new_delay
    else:
        body_pos.pop()


def update_score():
    """更新分数"""
    global score
    score += 1


def game_over():
    """游戏结束处理"""
    # 创建半透明覆盖层
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    GAME_WINDOW.blit(overlay, (0, 0))
    
    # 游戏结束文本
    over_font = get_font(60)
    over_text = over_font.render('GAME OVER', True, FOOD_COLOR)
    over_rect = over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
    GAME_WINDOW.blit(over_text, over_rect)
    
    # 分数文本
    score_font = get_font(30)
    score_text = score_font.render(f'SCORE: {score}', True, TEXT_COLOR)
    score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    GAME_WINDOW.blit(score_text, score_rect)
    
    # 重新开始按钮
    restart_font = get_font(25)
    restart_text = restart_font.render('PRESS SPACE TO PLAY AGAIN', True, TEXT_COLOR)
    restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))
    
    # 绘制GitHub风格按钮背景
    button_bg_rect = pygame.Rect(
        restart_rect.left - 20, restart_rect.top - 10,
        restart_rect.width + 40, restart_rect.height + 20
    )
    pygame.draw.rect(GAME_WINDOW, BUTTON_COLOR, button_bg_rect)
    GAME_WINDOW.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    
    # 等待用户输入
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))


def reset_game():
    """重置游戏状态"""
    global head_pos, body_pos, food_pos, food_flag, direction, next_direction
    global score, game_started, game_paused, move_delay, move_timer, snake_trail
    
    head_pos = INITIAL_HEAD_POS.copy()
    body_pos = [pos.copy() for pos in INITIAL_BODY_POS]
    food_pos = [
        random.randrange(0, WINDOW_WIDTH // BODY_SIZE) * BODY_SIZE,
        random.randrange(0, WINDOW_HEIGHT // BODY_SIZE) * BODY_SIZE
    ]
    food_flag = True
    direction = RIGHT
    next_direction = RIGHT
    score = 0
    game_started = True
    game_paused = False
    move_delay = BASE_MOVE_DELAY  # 重置移动延迟
    move_timer = 0  # 重置移动计时器
    snake_trail = []  # 重置蛇轨迹


def show_score():
    """GitHub风格分数显示"""
    # 分数文本 - 添加阴影效果以提高可读性
    score_font = get_font(25)
    score_text = score_font.render(f'SCORE: {score}', True, TEXT_COLOR)
    score_shadow = score_font.render(f'SCORE: {score}', True, BACKGROUND_COLOR)
    score_rect = score_text.get_rect()
    score_rect.topleft = (10, 10)
    score_shadow_rect = score_shadow.get_rect()
    score_shadow_rect.topleft = (12, 12)  # 阴影偏移
    GAME_WINDOW.blit(score_shadow, score_shadow_rect)
    GAME_WINDOW.blit(score_text, score_rect)
    
    # 显示速度等级 - 添加阴影效果
    speed_level = max(1, SPEED_LEVELS - int((move_delay - MIN_MOVE_DELAY) / 
                                           (BASE_MOVE_DELAY - MIN_MOVE_DELAY) * SPEED_LEVELS))
    speed_text = score_font.render(f'SPEED: {speed_level}/{SPEED_LEVELS}', True, TEXT_COLOR)
    speed_shadow = score_font.render(f'SPEED: {speed_level}/{SPEED_LEVELS}', True, BACKGROUND_COLOR)
    speed_rect = speed_text.get_rect()
    speed_rect.topleft = (10, 35)
    speed_shadow_rect = speed_shadow.get_rect()
    speed_shadow_rect.topleft = (12, 37)  # 阴影偏移
    GAME_WINDOW.blit(speed_shadow, speed_shadow_rect)
    GAME_WINDOW.blit(speed_text, speed_rect)


# 游戏主循环
while True:
    handle_events()
    
    if not game_started:
        draw_start_screen()
        FPS_CLOCK.tick(30)
        continue
    
    if game_paused:
        draw_pause_screen()
        FPS_CLOCK.tick(30)
        continue
    
    # 获取自上一帧以来的时间（毫秒）
    dt = FPS_CLOCK.get_time()
    move_timer += dt
    
    # 只有当计时器超过移动延迟时才移动蛇
    if move_timer >= move_delay:
        move_snake()
        move_timer = 0  # 重置计时器

        # 碰撞检测-边界检测
        if head_pos[0] < 0 or head_pos[0] >= WINDOW_WIDTH:
            game_over()
        if head_pos[1] < 0 or head_pos[1] >= WINDOW_HEIGHT:
            game_over()
        # 碰撞检测-蛇体检测
        if head_pos in body_pos[1:]:
            game_over()
    
    # 更新食物位置 - 移到主循环中，确保每帧都检查
    if not food_flag:
        while True:
            food_pos = [
                random.randrange(1, (WINDOW_WIDTH - BODY_SIZE) // BODY_SIZE) * BODY_SIZE,
                random.randrange(1, (WINDOW_HEIGHT - BODY_SIZE) // BODY_SIZE) * BODY_SIZE
            ]
            if food_pos not in body_pos:
                break
        food_flag = True

    # 绘制背景
    GAME_WINDOW.fill(BACKGROUND_COLOR)
    # 绘制网格
    draw_grid()
    # 绘制蛇
    draw_snake()
    # 绘制食物
    draw_food()
    
    # 显示分数
    show_score()

    # 更新画面
    pygame.display.update()
    
    # 根据性能模式调整帧率
    current_fps = TARGET_FPS if not performance_mode else 30
    FPS_CLOCK.tick(current_fps)
