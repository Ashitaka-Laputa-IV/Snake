// GitHub风格颜色方案 - 使用GitHub的设计语言
const COLORS = {
    BACKGROUND_COLOR: '#0d1117',  // GitHub深色背景 (#0d1117)
    GRID_COLOR: '#161b22',        // GitHub网格线颜色 (#161b22)
    SNAKE_HEAD_COLOR: '#388bfd',  // GitHub蓝色 (#388bfd)
    SNAKE_BODY_COLOR: '#58a6ff',  // GitHub浅蓝色 (#58a6ff)
    FOOD_COLOR: '#ef6c00',        // GitHub橙色 (#ef6c00)
    TEXT_COLOR: '#e5e7eb',        // GitHub文本颜色 (#e5e7eb)
    SCORE_BG_COLOR: '#161b22',    // 分数背景色 (#161b22)
    BUTTON_COLOR: '#238636',      // GitHub绿色按钮 (#238636)
    BUTTON_HOVER_COLOR: '#2ea043' // GitHub绿色悬停 (#2ea043)
};

// 游戏窗口设置
const WINDOW_WIDTH = 600;
const WINDOW_HEIGHT = 390;  // 修改为能被BODY_SIZE(15)整除的值，390/15=26

// 游戏速度设置
const INITIAL_SPEED = 8;
const SPEED_INCREASE_THRESHOLD = 5;  // 每吃多少食物增加速度

// 蛇相关设置
const BODY_SIZE = 15;
const INITIAL_HEAD_POS = [120, 60];
const INITIAL_BODY_POS = [[120, 60], [105, 60], [90, 60]];

// 方向常量
const DIRECTIONS = {
    UP: 0,
    DOWN: 1,
    LEFT: 2,
    RIGHT: 3
};

// 游戏速度优化
const BASE_MOVE_DELAY = 100;  // 基础移动延迟
const MIN_MOVE_DELAY = 40;    // 最小移动延迟（最快速度）
const MOVE_DELAY_REDUCTION = 8;  // 每次速度提升的延迟减少量
const SPEED_LEVELS = 5;       // 速度等级数量

// 帧率优化
const TARGET_FPS = 60;       // 目标帧率

// 游戏状态变量
let canvas, ctx;
let headPos, bodyPos, foodPos, foodFlag;
let direction, nextDirection, score;
let gameStarted, gamePaused;
let moveTimer, moveDelay;
let snakeTrail = [];  // 存储蛇的移动轨迹
let trailLength = 3;  // 轨迹长度
let smoothFactor = 0.3;  // 平滑因子
let performanceMode = false;  // 性能模式
let animationId;

// DOM元素
let startScreen, pauseScreen, gameOverScreen;
let scoreElement, speedElement, finalScoreElement;

// 初始化游戏
function initGame() {
    // 获取画布和上下文
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    
    // 获取DOM元素
    startScreen = document.getElementById('startScreen');
    pauseScreen = document.getElementById('pauseScreen');
    gameOverScreen = document.getElementById('gameOverScreen');
    scoreElement = document.getElementById('score');
    speedElement = document.getElementById('speed');
    finalScoreElement = document.getElementById('finalScore');
    
    // 初始化游戏状态
    resetGame();
    
    // 添加事件监听器
    document.addEventListener('keydown', handleKeyDown);
    document.getElementById('startButton').addEventListener('click', startGame);
    document.getElementById('resumeButton').addEventListener('click', resumeGame);
    document.getElementById('restartButton').addEventListener('click', restartGame);
    
    // 显示开始界面
    startScreen.classList.remove('hidden');
}

// 重置游戏状态
function resetGame() {
    headPos = [...INITIAL_HEAD_POS];
    bodyPos = INITIAL_BODY_POS.map(pos => [...pos]);
    foodPos = [
        Math.floor(Math.random() * (WINDOW_WIDTH / BODY_SIZE)) * BODY_SIZE,
        Math.floor(Math.random() * (WINDOW_HEIGHT / BODY_SIZE)) * BODY_SIZE
    ];
    foodFlag = true;
    direction = DIRECTIONS.RIGHT;
    nextDirection = DIRECTIONS.RIGHT;
    score = 0;
    gameStarted = false;
    gamePaused = false;
    moveDelay = BASE_MOVE_DELAY;
    moveTimer = 0;
    snakeTrail = [];
    
    updateScore();
}

// 开始游戏
function startGame() {
    gameStarted = true;
    startScreen.classList.add('hidden');
    gameLoop();
}

// 暂停游戏
function pauseGame() {
    gamePaused = true;
    pauseScreen.classList.remove('hidden');
}

// 继续游戏
function resumeGame() {
    gamePaused = false;
    pauseScreen.classList.add('hidden');
    gameLoop();
}

// 重新开始游戏
function restartGame() {
    resetGame();
    gameOverScreen.classList.add('hidden');
    gameStarted = true;
    gameLoop();
}

// 处理键盘事件
function handleKeyDown(event) {
    if (!gameStarted && event.key === ' ') {
        startGame();
        return;
    }
    
    if (gameStarted && !gamePaused) {
        // 方向控制 - 改进为更响应的控制
        if (event.key === 'ArrowUp' || event.key === 'w' || event.key === 'W') {
            if (direction !== DIRECTIONS.DOWN) {
                nextDirection = DIRECTIONS.UP;
            }
        }
        if (event.key === 'ArrowDown' || event.key === 's' || event.key === 'S') {
            if (direction !== DIRECTIONS.UP) {
                nextDirection = DIRECTIONS.DOWN;
            }
        }
        if (event.key === 'ArrowLeft' || event.key === 'a' || event.key === 'A') {
            if (direction !== DIRECTIONS.RIGHT) {
                nextDirection = DIRECTIONS.LEFT;
            }
        }
        if (event.key === 'ArrowRight' || event.key === 'd' || event.key === 'D') {
            if (direction !== DIRECTIONS.LEFT) {
                nextDirection = DIRECTIONS.RIGHT;
            }
        }
        if (event.key === 'p' || event.key === 'P') {
            pauseGame();
        }
        // 性能模式切换
        if (event.key === 'F1') {
            performanceMode = !performanceMode;
            console.log(`Performance mode: ${performanceMode ? 'ON' : 'OFF'}`);
        }
    } else if (gamePaused) {
        if (event.key === 'p' || event.key === 'P' || event.key === ' ') {
            resumeGame();
        }
    }
    
    if (event.key === 'Escape') {
        // ESC键处理
        if (gameStarted) {
            if (gamePaused) {
                resumeGame();
            } else {
                pauseGame();
            }
        }
    }
}

// 移动蛇
function moveSnake() {
    // 更新方向
    direction = nextDirection;
    
    // 计算新头部位置
    const newHeadPos = [...bodyPos[0]];  // 复制当前位置
    
    if (direction === DIRECTIONS.UP) {
        newHeadPos[1] -= BODY_SIZE;
    } else if (direction === DIRECTIONS.DOWN) {
        newHeadPos[1] += BODY_SIZE;
    } else if (direction === DIRECTIONS.RIGHT) {
        newHeadPos[0] += BODY_SIZE;
    } else if (direction === DIRECTIONS.LEFT) {
        newHeadPos[0] -= BODY_SIZE;
    }
    
    // 边界检测 - 在移动前检测，避免蛇头超出边界
    if (newHeadPos[0] < 0 || newHeadPos[0] >= WINDOW_WIDTH || 
        newHeadPos[1] < 0 || newHeadPos[1] >= WINDOW_HEIGHT) {
        gameOver();
        return;
    }
    
    // 更新蛇头位置
    bodyPos.unshift(newHeadPos);
    headPos = newHeadPos;  // 更新headPos引用
    
    // 检测蛇头是否与食物重合由此决定是否删除蛇尾巴
    if (headPos[0] === foodPos[0] && headPos[1] === foodPos[1]) {
        updateScore();
        foodFlag = false;
        // 每吃一定数量的食物增加速度
        if (score % SPEED_INCREASE_THRESHOLD === 0) {
            // 计算新的移动延迟，确保不会低于最小延迟
            moveDelay = Math.max(MIN_MOVE_DELAY, moveDelay - MOVE_DELAY_REDUCTION);
        }
    } else {
        bodyPos.pop();
    }
}

// 更新分数
function updateScore() {
    score++;
    scoreElement.textContent = `SCORE: ${score}`;
    
    // 更新速度等级
    const speedLevel = Math.max(1, SPEED_LEVELS - Math.floor((moveDelay - MIN_MOVE_DELAY) / 
                                     (BASE_MOVE_DELAY - MIN_MOVE_DELAY) * SPEED_LEVELS));
    speedElement.textContent = `SPEED: ${speedLevel}/${SPEED_LEVELS}`;
}

// 游戏结束处理
function gameOver() {
    finalScoreElement.textContent = score;
    gameOverScreen.classList.remove('hidden');
    cancelAnimationFrame(animationId);
}

// 绘制网格背景
function drawGrid() {
    ctx.strokeStyle = COLORS.GRID_COLOR;
    ctx.lineWidth = 1;
    
    // 绘制垂直线
    for (let x = 0; x <= WINDOW_WIDTH; x += BODY_SIZE) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, WINDOW_HEIGHT);
        ctx.stroke();
    }
    
    // 绘制水平线
    for (let y = 0; y <= WINDOW_HEIGHT; y += BODY_SIZE) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(WINDOW_WIDTH, y);
        ctx.stroke();
    }
    
    // 确保边界线清晰可见
    ctx.strokeStyle = COLORS.GRID_COLOR;
    ctx.lineWidth = 2;
    
    // 绘制外边框
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(WINDOW_WIDTH, 0);
    ctx.lineTo(WINDOW_WIDTH, WINDOW_HEIGHT);
    ctx.lineTo(0, WINDOW_HEIGHT);
    ctx.closePath();
    ctx.stroke();
    
    // 特别强调底部边框，确保最后一行清晰可见
    ctx.strokeStyle = '#2a3142';  // 稍微亮一点的颜色
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, WINDOW_HEIGHT);
    ctx.lineTo(WINDOW_WIDTH, WINDOW_HEIGHT);
    ctx.stroke();
}

// 绘制食物
function drawFood() {
    ctx.fillStyle = COLORS.FOOD_COLOR;
    ctx.fillRect(foodPos[0] + 2, foodPos[1] + 2, BODY_SIZE - 4, BODY_SIZE - 4);
    
    // 添加简单的内部装饰
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.lineWidth = 2;
    const innerSize = BODY_SIZE - 8;
    ctx.strokeRect(foodPos[0] + 4, foodPos[1] + 4, innerSize, innerSize);
}

// 绘制蛇
function drawSnake() {
    // 添加蛇头到轨迹
    if (snakeTrail.length === 0 || snakeTrail[0][0] !== headPos[0] || snakeTrail[0][1] !== headPos[1]) {
        snakeTrail.unshift([...headPos]);
    }
    
    // 限制轨迹长度
    while (snakeTrail.length > trailLength) {
        snakeTrail.pop();
    }
    
    for (let i = 0; i < bodyPos.length; i++) {
        const pos = bodyPos[i];
        
        if (i === 0) {  // 蛇头
            // 绘制蛇头为GitHub风格矩形
            ctx.fillStyle = COLORS.SNAKE_HEAD_COLOR;
            ctx.fillRect(pos[0] + 1, pos[1] + 1, BODY_SIZE - 2, BODY_SIZE - 2);
            
            // 添加简单的眼睛
            ctx.fillStyle = COLORS.BACKGROUND_COLOR;
            const eyeSize = 2;
            let eye1Pos, eye2Pos;
            
            if (direction === DIRECTIONS.RIGHT) {
                eye1Pos = [pos[0] + BODY_SIZE - 4, pos[1] + 4];
                eye2Pos = [pos[0] + BODY_SIZE - 4, pos[1] + BODY_SIZE - 6];
            } else if (direction === DIRECTIONS.LEFT) {
                eye1Pos = [pos[0] + 4, pos[1] + 4];
                eye2Pos = [pos[0] + 4, pos[1] + BODY_SIZE - 6];
            } else if (direction === DIRECTIONS.UP) {
                eye1Pos = [pos[0] + 4, pos[1] + 4];
                eye2Pos = [pos[0] + BODY_SIZE - 6, pos[1] + 4];
            } else {  // DOWN
                eye1Pos = [pos[0] + 4, pos[1] + BODY_SIZE - 4];
                eye2Pos = [pos[0] + BODY_SIZE - 6, pos[1] + BODY_SIZE - 4];
            }
            
            ctx.fillRect(eye1Pos[0], eye1Pos[1], eyeSize, eyeSize);
            ctx.fillRect(eye2Pos[0], eye2Pos[1], eyeSize, eyeSize);
        } else {  // 蛇身
            // 渐变颜色 - GitHub风格中的简单渐变
            const colorFactor = Math.max(0.7, 1.0 - (i / bodyPos.length) * 0.3);
            const r = parseInt(COLORS.SNAKE_BODY_COLOR.slice(1, 3), 16);
            const g = parseInt(COLORS.SNAKE_BODY_COLOR.slice(3, 5), 16);
            const b = parseInt(COLORS.SNAKE_BODY_COLOR.slice(5, 7), 16);
            
            ctx.fillStyle = `rgb(${Math.floor(r * colorFactor)}, ${Math.floor(g * colorFactor)}, ${Math.floor(b * colorFactor)})`;
            ctx.fillRect(pos[0] + 1, pos[1] + 1, BODY_SIZE - 2, BODY_SIZE - 2);
        }
    }
}

// 游戏主循环
function gameLoop(timestamp) {
    if (!gameStarted || gamePaused) return;
    
    // 计算时间差
    if (!moveTimer) moveTimer = timestamp;
    const deltaTime = timestamp - moveTimer;
    
    // 只有当计时器超过移动延迟时才移动蛇
    if (deltaTime >= moveDelay) {
        moveSnake();
        moveTimer = timestamp;
        
        // 碰撞检测-蛇体检测
        for (let i = 1; i < bodyPos.length; i++) {
            if (headPos[0] === bodyPos[i][0] && headPos[1] === bodyPos[i][1]) {
                gameOver();
                return;
            }
        }
    }
    
    // 更新食物位置 - 移到主循环中，确保每帧都检查
    if (!foodFlag) {
        do {
            foodPos = [
                Math.floor(Math.random() * (WINDOW_WIDTH / BODY_SIZE)) * BODY_SIZE,
                Math.floor(Math.random() * (WINDOW_HEIGHT / BODY_SIZE)) * BODY_SIZE
            ];
        } while (bodyPos.some(segment => segment[0] === foodPos[0] && segment[1] === foodPos[1]));
        foodFlag = true;
    }
    
    // 清空画布
    ctx.fillStyle = COLORS.BACKGROUND_COLOR;
    ctx.fillRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);
    
    // 绘制网格
    drawGrid();
    
    // 绘制蛇
    drawSnake();
    
    // 绘制食物
    drawFood();
    
    // 继续游戏循环
    animationId = requestAnimationFrame(gameLoop);
}

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', initGame);