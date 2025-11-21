import pygame, sys, random, time, os, math

# 颜色初始化 - 使用更现代的配色方案
black = pygame.Color(15, 15, 25)  # 深色背景
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 85, 85)  # 柔和的红色
green = pygame.Color(85, 255, 85)  # 柔和的绿色
blue = pygame.Color(85, 85, 255)  # 柔和的蓝色
dark_green = pygame.Color(0, 180, 0)  # 深绿色
light_green = pygame.Color(150, 255, 150)  # 浅绿色
yellow = pygame.Color(255, 215, 0)  # 金黄色
purple = pygame.Color(180, 85, 255)  # 紫色
orange = pygame.Color(255, 165, 0)  # 橙色

# 窗口大小 - 增大窗口以获得更好的视觉效果
windows_size = [600, 400]

# pygame初始化
errors = pygame.init()
if errors[1] > 0:
    print(f'[!] {errors[1]} errors happened when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] game initialising successfully!')

# 设置窗口及其信息
pygame.display.set_caption('Snake Game')
window = pygame.display.set_mode(windows_size)

# 设置fps
fps = pygame.time.Clock()

# 设置速度 - 初始速度稍慢，便于操作
speed = 8
# 增加速度的阈值
speed_increase_threshold = 5

# 设置蛇方块大小 - 增大方块大小
body_size = 15
# 蛇变量 
head_pos = [120, 60]
body_pos = [[120, 60], [105, 60], [90, 60]] 

# 食物变量
food_pos = [random.randrange(0, windows_size[0] // body_size) * body_size, 
           random.randrange(0, windows_size[1] // body_size) * body_size]
# FOOD FLAG
food_flag = True

# 方向 - 使用数字表示方向，便于处理
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
direction = RIGHT
# head下一个位置方向
next_direction = RIGHT

# 分数
score = 0

# 游戏状态
game_started = False
game_paused = False

# 蛇移动计时器
move_timer = 0
move_delay = 100  # 初始移动延迟（毫秒）

# 蛇移动平滑度
snake_trail = []  # 存储蛇的移动轨迹
trail_length = 3  # 轨迹长度
smooth_factor = 0.3  # 平滑因子

# 游戏速度优化
base_move_delay = 100  # 基础移动延迟
min_move_delay = 40    # 最小移动延迟（最快速度）
move_delay_reduction = 8  # 每次速度提升的延迟减少量
speed_levels = 5       # 速度等级数量

# 帧率优化
target_fps = 60       # 目标帧率
frame_skip = False     # 是否跳帧
performance_mode = False  # 性能模式

# 跨平台字体加载
def get_font(size):
    # 尝试加载系统字体，跨平台兼容
    try:
        if os.name == 'nt':  # Windows
            return pygame.font.SysFont('times new roman', size)
        else:  # Linux/Mac
            return pygame.font.SysFont('Arial', size)
    except:
        # 如果系统字体加载失败，使用默认字体
        return pygame.font.Font(None, size)

# 绘制网格背景
def draw_grid():
    # 绘制淡色网格线
    grid_color = pygame.Color(25, 25, 35)
    for x in range(0, windows_size[0], body_size):
        pygame.draw.line(window, grid_color, (x, 0), (x, windows_size[1]), 1)
    for y in range(0, windows_size[1], body_size):
        pygame.draw.line(window, grid_color, (0, y), (windows_size[0], y), 1)

# 绘制圆形食物
def draw_food():
    # 绘制一个带渐变效果的圆形食物
    center = (food_pos[0] + body_size // 2, food_pos[1] + body_size // 2)
    radius = body_size // 2 - 1
    
    # 绘制多层圆形以创建渐变效果
    pygame.draw.circle(window, yellow, center, radius)
    pygame.draw.circle(window, orange, center, radius - 2)
    pygame.draw.circle(window, red, center, radius - 4)
    
    # 添加高光效果
    highlight_pos = (center[0] - radius // 3, center[1] - radius // 3)
    pygame.draw.circle(window, white, highlight_pos, radius // 3)

# 绘制蛇
def draw_snake():
    # 添加蛇头到轨迹
    if len(snake_trail) == 0 or snake_trail[0] != head_pos:
        snake_trail.insert(0, [head_pos[0], head_pos[1]])
    
    # 限制轨迹长度
    while len(snake_trail) > trail_length:
        snake_trail.pop()
    
    for i, pos in enumerate(body_pos):
        # 计算渐变颜色
        if i == 0:  # 蛇头
            color = light_green
            # 绘制蛇头为圆角矩形
            rect = pygame.Rect(pos[0], pos[1], body_size, body_size)
            pygame.draw.rect(window, color, rect, border_radius=3)
            
            # 添加眼睛
            eye_size = 3
            if direction == RIGHT:
                eye1_pos = (pos[0] + body_size - 5, pos[1] + 4)
                eye2_pos = (pos[0] + body_size - 5, pos[1] + body_size - 7)
            elif direction == LEFT:
                eye1_pos = (pos[0] + 5, pos[1] + 4)
                eye2_pos = (pos[0] + 5, pos[1] + body_size - 7)
            elif direction == UP:
                eye1_pos = (pos[0] + 4, pos[1] + 5)
                eye2_pos = (pos[0] + body_size - 7, pos[1] + 5)
            else:  # DOWN
                eye1_pos = (pos[0] + 4, pos[1] + body_size - 5)
                eye2_pos = (pos[0] + body_size - 7, pos[1] + body_size - 5)
                
            pygame.draw.circle(window, black, eye1_pos, eye_size)
            pygame.draw.circle(window, black, eye2_pos, eye_size)
        else:  # 蛇身
            # 渐变颜色
            color_factor = max(0.4, 1.0 - (i / len(body_pos)) * 0.5)
            r = int(dark_green.r * color_factor + light_green.r * (1 - color_factor))
            g = int(dark_green.g * color_factor + light_green.g * (1 - color_factor))
            b = int(dark_green.b * color_factor + light_green.b * (1 - color_factor))
            color = pygame.Color(r, g, b)
            
            # 绘制圆角矩形
            rect = pygame.Rect(pos[0], pos[1], body_size, body_size)
            pygame.draw.rect(window, color, rect, border_radius=2)
            
            # 添加平滑过渡效果
            if i < len(body_pos) - 1:
                next_pos = body_pos[i+1]
                # 计算连接点
                if i < len(snake_trail):
                    # 使用轨迹进行平滑过渡
                    trail_pos = snake_trail[min(i, len(snake_trail)-1)]
                    # 绘制连接部分
                    pygame.draw.line(window, color, 
                                    (pos[0] + body_size // 2, pos[1] + body_size // 2),
                                    (next_pos[0] + body_size // 2, next_pos[1] + body_size // 2), 
                                    body_size - 2)

# 绘制游戏开始界面
def draw_start_screen():
    title_font = get_font(50)
    title_text = title_font.render('Snake Game', True, light_green)
    title_rect = title_text.get_rect(center=(windows_size[0] // 2, windows_size[1] // 3))
    
    instruction_font = get_font(25)
    instruction_text = instruction_font.render('Press SPACE to Start', True, white)
    instruction_rect = instruction_text.get_rect(center=(windows_size[0] // 2, windows_size[1] // 2))
    
    control_font = get_font(20)
    control_text1 = control_font.render('Use Arrow Keys or WASD to Move', True, white)
    control_rect1 = control_text1.get_rect(center=(windows_size[0] // 2, windows_size[1] * 2 // 3))
    
    control_text2 = control_font.render('Press P to Pause, ESC to Quit', True, white)
    control_rect2 = control_text2.get_rect(center=(windows_size[0] // 2, windows_size[1] * 3 // 4))
    
    window.fill(black)
    window.blit(title_text, title_rect)
    window.blit(instruction_text, instruction_rect)
    window.blit(control_text1, control_rect1)
    window.blit(control_text2, control_rect2)
    pygame.display.flip()

# 绘制暂停界面
def draw_pause_screen():
    pause_font = get_font(50)
    pause_text = pause_font.render('PAUSED', True, yellow)
    pause_rect = pause_text.get_rect(center=(windows_size[0] // 2, windows_size[1] // 2))
    
    resume_font = get_font(25)
    resume_text = resume_font.render('Press P to Resume', True, white)
    resume_rect = resume_text.get_rect(center=(windows_size[0] // 2, windows_size[1] * 2 // 3))
    
    window.blit(pause_text, pause_rect)
    window.blit(resume_text, resume_rect)
    pygame.display.flip()

# 跨平台事件处理
def handle_events():
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

# 移动蛇
def move_snake():
    global direction, head_pos, move_timer, move_delay, snake_trail, food_flag, score
    
    # 更新方向
    direction = next_direction
    
    # 计算新头部位置
    new_head_pos = [body_pos[0][0], body_pos[0][1]]  # 复制当前位置
    
    if direction == UP:
        new_head_pos[1] -= body_size
    elif direction == DOWN:
        new_head_pos[1] += body_size
    elif direction == RIGHT:
        new_head_pos[0] += body_size
    elif direction == LEFT:
        new_head_pos[0] -= body_size
    
    # 更新蛇头位置
    body_pos.insert(0, new_head_pos)
    head_pos = new_head_pos  # 更新head_pos引用
    
    # 检测蛇头是否与食物重合由此决定是否删除蛇尾巴
    if head_pos[0] == food_pos[0] and head_pos[1] == food_pos[1]:
        update_score()
        food_flag = False
        # 每吃一定数量的食物增加速度
        if score % speed_increase_threshold == 0:
            # 计算新的移动延迟，确保不会低于最小延迟
            new_delay = max(min_move_delay, move_delay - move_delay_reduction)
            move_delay = new_delay
    else:
        body_pos.pop()

# 更新分数
def update_score():
    global score
    score += 1

# game over
def game_over():
    over_font = get_font(50)
    over_rder = over_font.render('Game Over!', True, red)
    over_rect = over_rder.get_rect()
    over_rect.midtop = (windows_size[0] / 2, windows_size[1] / 3)
    
    score_font = get_font(30)
    score_text = score_font.render(f'Final Score: {score}', True, white)
    score_rect = score_text.get_rect()
    score_rect.midtop = (windows_size[0] / 2, windows_size[1] / 2)
    
    restart_font = get_font(25)
    restart_text = restart_font.render('Press SPACE to Play Again', True, white)
    restart_rect = restart_text.get_rect()
    restart_rect.midtop = (windows_size[0] / 2, windows_size[1] * 2 // 3)
    
    window.fill(black)
    window.blit(over_rder, over_rect)
    window.blit(score_text, score_rect)
    window.blit(restart_text, restart_rect)
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

# 重置游戏
def reset_game():
    global head_pos, body_pos, food_pos, food_flag, direction, next_direction, score, game_started, game_paused, move_delay, move_timer, snake_trail
    
    head_pos = [120, 60]
    body_pos = [[120, 60], [105, 60], [90, 60]] 
    food_pos = [random.randrange(0, windows_size[0] // body_size) * body_size, 
               random.randrange(0, windows_size[1] // body_size) * body_size]
    food_flag = True
    direction = RIGHT
    next_direction = RIGHT
    score = 0
    game_started = True
    game_paused = False
    move_delay = base_move_delay  # 重置移动延迟
    move_timer = 0  # 重置移动计时器
    snake_trail = []  # 重置蛇轨迹

# show score
def show_score():
    score_font = get_font(25)
    score_rder = score_font.render('Score: ' + str(score), True, white)
    score_rect = score_rder.get_rect()
    score_rect.topleft = (10, 10)
    window.blit(score_rder, score_rect)
    
    # 显示速度等级
    speed_level = max(1, speed_levels - int((move_delay - min_move_delay) / (base_move_delay - min_move_delay) * speed_levels))
    speed_text = score_font.render(f'Speed: {speed_level}/{speed_levels}', True, white)
    speed_rect = speed_text.get_rect()
    speed_rect.topleft = (10, 35)
    window.blit(speed_text, speed_rect)

# 游戏主循环
while True:
    handle_events()
    
    if not game_started:
        draw_start_screen()
        fps.tick(30)
        continue
    
    if game_paused:
        draw_pause_screen()
        fps.tick(30)
        continue
    
    # 获取自上一帧以来的时间（毫秒）
    dt = fps.get_time()
    move_timer += dt
    
    # 只有当计时器超过移动延迟时才移动蛇
    if move_timer >= move_delay:
        move_snake()
        move_timer = 0  # 重置计时器

        # 碰撞检测-边界检测
        if head_pos[0] < 0 or head_pos[0] >= windows_size[0]:
            game_over()
        if head_pos[1] < 0 or head_pos[1] >= windows_size[1]:
            game_over()
        # 碰撞检测-蛇体检测
        if head_pos in body_pos[1:]:
            game_over()
    
    # 更新食物位置 - 移到主循环中，确保每帧都检查
    if not food_flag:
        while True:
            food_pos = [random.randrange(1, (windows_size[0]  - body_size)// body_size) * body_size, 
                       random.randrange(1, (windows_size[1] - body_size)// body_size) * body_size]
            if food_pos not in body_pos:
                break
        food_flag = True

    # 绘制背景
    window.fill(black)
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
    current_fps = target_fps if not performance_mode else 30
    fps.tick(current_fps)
