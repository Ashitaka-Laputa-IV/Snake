import pygame, sys, random, time

# 颜色初始化
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

# 窗口大小
windows_size = [360, 240]

# pygame初始化
errors = pygame.init()
if errors[1] > 0:
    print(f'[!] {errors[1]} errors happened when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] game initialising successfully!')

# 设置窗口及其信息
pygame.display.set_caption('snake')
window = pygame.display.set_mode(windows_size)

# 设置fps
fps = pygame.time.Clock()

# 设置速度
speed = 10

# 设置蛇方块大小
body_size = 10
# 蛇变量 
head_pos = [80, 40]
body_pos = [[80, 40], [70, 40], [60, 40]] 

# 食物变量
food_pos = [random.randrange(0, windows_size[0] // body_size) * body_size, 
           random.randrange(0, windows_size[1] // body_size) * body_size]
# FOOD FLAG
food_flag = True

# 方向
direction = 'RIGHT'
# head下一个位置方向
next_pos = direction

# 分数
score = 0

# game over
def game_over():
    over_font = pygame.font.SysFont('times new roman', 45)
    over_rder = over_font.render('Suck My Dick!', True, red)
    over_rect = over_rder.get_rect()
    over_rect.midtop = (windows_size[0] / 2, windows_size[1] / 2)
    window.fill(black)
    window.blit(over_rder, over_rect)
    show_score()
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    sys.exit()

# show score
def show_score():
    score_font = pygame.font.SysFont('times', 20)
    score_rder = score_font.render('Dicks: ' + str(score), True, white)
    score_rect = score_rder.get_rect()
    score_rect.midtop = (windows_size[0] / 10, 15)
    window.blit(score_rder, score_rect)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # 更新方向
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == ord('w'):
                direction = 'UP'
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                direction = 'DOWN'
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                direction = 'LEFT'
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                direction = 'RIGHT'
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    # 检测是否更新新位置 - 移到事件循环外
    if direction == 'UP' and next_pos != 'DOWN':
        next_pos = 'UP'
    elif direction == 'DOWN' and next_pos != 'UP':
        next_pos = 'DOWN'
    elif direction == 'LEFT' and next_pos != 'RIGHT':
        next_pos = 'LEFT'
    elif direction == 'RIGHT' and next_pos != 'LEFT':
        next_pos = 'RIGHT'
    
    # 更新位置 - 创建新的头部位置，避免引用问题
    new_head_pos = [body_pos[0][0], body_pos[0][1]]  # 复制当前位置
    if next_pos == 'UP':
        new_head_pos[1] -= body_size
    elif next_pos == 'DOWN':
        new_head_pos[1] += body_size
    elif next_pos == 'RIGHT':
        new_head_pos[0] += body_size
    elif next_pos == 'LEFT':
        new_head_pos[0] -= body_size
    
    # 更新蛇头位置
    body_pos.insert(0, new_head_pos)
    head_pos = new_head_pos  # 更新head_pos引用
    
    # 检测蛇头是否与食物重合由此决定是否删除蛇尾巴
    if head_pos[0] == food_pos[0] and head_pos[1] == food_pos[1]:
        score += 1
        food_flag = False
    else:
        body_pos.pop()
        
    # 更新食物位置
    if not food_flag:
        while True:
            food_pos = [random.randrange(1, (windows_size[0]  - body_size)// body_size) * body_size, 
                       random.randrange(1, (windows_size[1] - body_size)// body_size) * body_size]
            if food_pos not in body_pos:
                break
        food_flag = True

    # 绘制背景
    window.fill(black)
    # 绘制蛇体
    for pos in body_pos:
        pygame.draw.rect(window, green, pygame.Rect(pos[0], pos[1], body_size, body_size))
    # 绘制食物
    pygame.draw.rect(window, white, pygame.Rect(food_pos[0], food_pos[1], body_size, body_size))

    # 碰撞检测-边界检测
    if head_pos[0] < 0 or head_pos[0] >= windows_size[0]:
        game_over()
    if head_pos[1] < 0 or head_pos[1] >= windows_size[1]:
        game_over()
    # 碰撞检测-蛇体检测
    if head_pos in body_pos[1:]:
        game_over()
    
    # 显示分数
    show_score()

    # 更新画面
    pygame.display.update()
    
    # 更新频率(画面速度越快, 蛇速度越快)
    fps.tick(speed)
