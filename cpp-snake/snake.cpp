#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <chrono>
#include <thread>
#include <string>
#include <algorithm>
#include <sstream>

#ifdef _WIN32
#include <windows.h>
#include <conio.h>
#else
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#endif

// 游戏常量
const int WINDOW_WIDTH = 60;
const int WINDOW_HEIGHT = 30;
const int BODY_SIZE = 1;
const int INITIAL_SPEED = 150; // 毫秒
const int MIN_SPEED = 50; // 最快速度（毫秒）
const int SPEED_INCREASE_THRESHOLD = 5; // 每吃多少食物增加速度

// 辅助函数：将整数转换为字符串
template<typename T>
std::string to_string(T value) {
    std::ostringstream ss;
    ss << value;
    return ss.str();
}

// GitHub风格颜色代码
namespace Colors {
    const char* RESET = "\033[0m";
    const char* BLACK = "\033[30m";
    const char* RED = "\033[31m";
    const char* GREEN = "\033[32m";
    const char* YELLOW = "\033[33m";
    const char* BLUE = "\033[34m";
    const char* MAGENTA = "\033[35m";
    const char* CYAN = "\033[36m";
    const char* WHITE = "\033[37m";
    
    // 背景色
    const char* BG_BLACK = "\033[40m";
    const char* BG_RED = "\033[41m";
    const char* BG_GREEN = "\033[42m";
    const char* BG_YELLOW = "\033[43m";
    const char* BG_BLUE = "\033[44m";
    const char* BG_MAGENTA = "\033[45m";
    const char* BG_CYAN = "\033[46m";
    const char* BG_WHITE = "\033[47m";
    
    // GitHub风格颜色
    const char* GITHUB_BG = "\033[48;2;13;17;23m";     // #0d1117
    const char* GITHUB_GRID = "\033[48;2;22;27;34m";    // #161b22
    const char* GITHUB_BLUE = "\033[38;2;56;139;253m";  // #388bfd
    const char* GITHUB_LIGHT_BLUE = "\033[38;2;88;166;255m"; // #58a6ff
    const char* GITHUB_ORANGE = "\033[38;2;239;108;0m"; // #ef6c00
    const char* GITHUB_TEXT = "\033[38;2;229;231;235m"; // #e5e7eb
}

// 方向枚举
enum Direction {
    UP = 0,
    DOWN = 1,
    LEFT = 2,
    RIGHT = 3
};

// 游戏状态枚举
enum GameState {
    MENU,
    PLAYING,
    PAUSED,
    GAME_OVER
};

// 点结构体
struct Point {
    int x, y;
    Point() : x(0), y(0) {}
    Point(int x, int y) : x(x), y(y) {}
    
    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }
};

// 跨平台控制台操作类
class Console {
public:
    static void init() {
#ifdef _WIN32
        // 启用Windows 10+的虚拟终端处理
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        DWORD dwMode = 0;
        GetConsoleMode(hOut, &dwMode);
        dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
        SetConsoleMode(hOut, dwMode);
        
        // 设置控制台编码为UTF-8
        SetConsoleOutputCP(CP_UTF8);
        SetConsoleCP(CP_UTF8);
        
        // 获取控制台窗口信息并设置缓冲区大小
        CONSOLE_SCREEN_BUFFER_INFO csbi;
        GetConsoleScreenBufferInfo(hOut, &csbi);
        
        // 设置控制台缓冲区大小与窗口大小相同，防止滚动
        COORD bufferSize;
        bufferSize.X = csbi.srWindow.Right - csbi.srWindow.Left + 1;
        bufferSize.Y = csbi.srWindow.Bottom - csbi.srWindow.Top + 1;
        SetConsoleScreenBufferSize(hOut, bufferSize);
        
        // 禁用控制台快速编辑模式，防止鼠标选择导致滚动
        HANDLE hIn = GetStdHandle(STD_INPUT_HANDLE);
        DWORD inMode = 0;
        GetConsoleMode(hIn, &inMode);
        inMode &= ~ENABLE_QUICK_EDIT_MODE;
        inMode |= ENABLE_EXTENDED_FLAGS;
        SetConsoleMode(hIn, inMode);
#endif
    }
    
    static void clear() {
#ifdef _WIN32
        system("cls");
#else
        system("clear");
#endif
    }
    
    static void hideCursor() {
#ifdef _WIN32
        HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
        CONSOLE_CURSOR_INFO cursorInfo;
        GetConsoleCursorInfo(hConsole, &cursorInfo);
        cursorInfo.bVisible = false;
        SetConsoleCursorInfo(hConsole, &cursorInfo);
#else
        std::cout << "\033[?25l";
#endif
    }
    
    static void showCursor() {
#ifdef _WIN32
        HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
        CONSOLE_CURSOR_INFO cursorInfo;
        GetConsoleCursorInfo(hConsole, &cursorInfo);
        cursorInfo.bVisible = true;
        SetConsoleCursorInfo(hConsole, &cursorInfo);
#else
        std::cout << "\033[?25h";
#endif
    }
    
    static void setCursorPosition(int x, int y) {
#ifdef _WIN32
        COORD coord;
        coord.X = x;
        coord.Y = y;
        SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), coord);
#else
        std::cout << "\033[" << y << ";" << x << "H";
#endif
    }
    
    static int getKey() {
#ifdef _WIN32
        if (_kbhit()) {
            return _getch();
        }
        return -1;
#else
        struct termios oldt, newt;
        int ch;
        int oldf;
        
        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &newt);
        oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
        fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);
        
        ch = getchar();
        
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
        fcntl(STDIN_FILENO, F_SETFL, oldf);
        
        if(ch != EOF) {
            return ch;
        }
        
        return -1;
#endif
    }
    
    static void sleep(int milliseconds) {
        std::this_thread::sleep_for(std::chrono::milliseconds(milliseconds));
    }
};

// 双缓冲渲染系统
class DoubleBuffer {
private:
    std::vector<std::string> frontBuffer;
    std::vector<std::string> backBuffer;
    int width, height;
    
public:
    DoubleBuffer(int w, int h) : width(w), height(h) {
        frontBuffer.resize(height, std::string(width, ' '));
        backBuffer.resize(height, std::string(width, ' '));
    }
    
    void clear() {
        for (auto& row : backBuffer) {
            std::fill(row.begin(), row.end(), ' ');
        }
    }
    
    void drawChar(int x, int y, char c, const char* color = Colors::RESET) {
        if (x >= 0 && x < width && y >= 0 && y < height) {
            backBuffer[y][x] = c;
        }
    }
    
    void drawText(int x, int y, const std::string& text, const char* color = Colors::RESET) {
        for (size_t i = 0; i < text.length(); ++i) {
            if (x + i < width) {
                backBuffer[y][x + i] = text[i];
            }
        }
    }
    
    void drawBox(int x, int y, int w, int h, const char* color = Colors::RESET) {
        // 绘制边框
        for (int i = x; i < x + w; ++i) {
            drawChar(i, y, '-', color);
            drawChar(i, y + h - 1, '-', color);
        }
        
        for (int i = y; i < y + h; ++i) {
            drawChar(x, i, '|', color);
            drawChar(x + w - 1, i, '|', color);
        }
        
        // 绘制角
        drawChar(x, y, '+', color);
        drawChar(x + w - 1, y, '+', color);
        drawChar(x, y + h - 1, '+', color);
        drawChar(x + w - 1, y + h - 1, '+', color);
    }
    
    void fillRect(int x, int y, int w, int h, char c, const char* color = Colors::RESET) {
        for (int j = y; j < y + h; ++j) {
            for (int i = x; i < x + w; ++i) {
                drawChar(i, j, c, color);
            }
        }
    }
    
    void render() {
        Console::setCursorPosition(0, 0);
        
        // 使用单个输出操作来减少闪烁
        std::string output;
        output.reserve(height * (width + 1)); // 预分配内存
        
        for (const auto& row : backBuffer) {
            output += Colors::GITHUB_BG;
            output += row;
            output += Colors::RESET;
            output += '\n';
        }
        
        // 在Windows上使用WriteFile而不是cout，以减少闪烁
#ifdef _WIN32
        HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
        DWORD charsWritten;
        WriteFile(hOut, output.c_str(), static_cast<DWORD>(output.length()), &charsWritten, NULL);
#else
        std::cout << output;
        std::cout.flush(); // 确保立即输出
#endif
        
        frontBuffer = backBuffer;
    }
};

// 贪吃蛇游戏类
class SnakeGame {
private:
    std::vector<Point> snake;
    Point food;
    Direction direction;
    Direction nextDirection;
    int score;
    int speed;
    GameState gameState;
    DoubleBuffer buffer;
    
public:
    SnakeGame() : buffer(WINDOW_WIDTH, WINDOW_HEIGHT) {
        srand(time(nullptr));
        init();
    }
    
    void init() {
        // 初始化蛇
        snake.clear();
        snake.push_back(Point(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2));
        snake.push_back(Point(WINDOW_WIDTH / 2 - 1, WINDOW_HEIGHT / 2));
        snake.push_back(Point(WINDOW_WIDTH / 2 - 2, WINDOW_HEIGHT / 2));
        
        // 初始化食物
        generateFood();
        
        // 初始化游戏状态
        direction = RIGHT;
        nextDirection = RIGHT;
        score = 0;
        speed = INITIAL_SPEED;
        gameState = MENU;
        
        Console::hideCursor();
    }
    
    void generateFood() {
        bool validPosition = false;
        
        while (!validPosition) {
            food.x = rand() % (WINDOW_WIDTH - 2) + 1;
            food.y = rand() % (WINDOW_HEIGHT - 2) + 1;
            
            validPosition = true;
            for (const auto& segment : snake) {
                if (segment == food) {
                    validPosition = false;
                    break;
                }
            }
        }
    }
    
    void handleInput() {
        int key = Console::getKey();
        
        if (key == -1) return;
        
        switch (gameState) {
            case MENU:
                if (key == ' ') {
                    gameState = PLAYING;
                }
                break;
                
            case PLAYING:
                // 处理普通字符键
                switch (key) {
                    case 'w':
                    case 'W':
                        if (direction != DOWN) nextDirection = UP;
                        break;
                    case 's':
                    case 'S':
                        if (direction != UP) nextDirection = DOWN;
                        break;
                    case 'a':
                    case 'A':
                        if (direction != RIGHT) nextDirection = LEFT;
                        break;
                    case 'd':
                    case 'D':
                        if (direction != LEFT) nextDirection = RIGHT;
                        break;
                    case 'p':
                    case 'P':
                        gameState = PAUSED;
                        break;
                    case 27: // ESC
                        gameState = MENU;
                        break;
                    // Windows下特殊键处理
                    case 0: // 或者224（取决于系统）
                    {
                        int extendedKey = Console::getKey();
                        if (extendedKey != -1) {
                            switch (extendedKey) {
                                case 72: // 上箭头
                                    if (direction != DOWN) nextDirection = UP;
                                    break;
                                case 80: // 下箭头
                                    if (direction != UP) nextDirection = DOWN;
                                    break;
                                case 75: // 左箭头
                                    if (direction != RIGHT) nextDirection = LEFT;
                                    break;
                                case 77: // 右箭头
                                    if (direction != LEFT) nextDirection = RIGHT;
                                    break;
                            }
                        }
                        break;
                    }
                }
                break;
                
            case PAUSED:
                if (key == 'p' || key == 'P' || key == ' ') {
                    gameState = PLAYING;
                } else if (key == 27) { // ESC
                    gameState = MENU;
                }
                break;
                
            case GAME_OVER:
                if (key == ' ') {
                    init();
                    gameState = PLAYING;
                } else if (key == 27) { // ESC
                    gameState = MENU;
                }
                break;
        }
    }
    
    void update() {
        if (gameState != PLAYING) return;
        
        // 更新方向
        direction = nextDirection;
        
        // 计算新头部位置
        Point newHead = snake[0];
        
        switch (direction) {
            case UP:
                newHead.y--;
                break;
            case DOWN:
                newHead.y++;
                break;
            case LEFT:
                newHead.x--;
                break;
            case RIGHT:
                newHead.x++;
                break;
        }
        
        // 边界检测
        if (newHead.x <= 0 || newHead.x >= WINDOW_WIDTH - 1 || 
            newHead.y <= 0 || newHead.y >= WINDOW_HEIGHT - 1) {
            gameState = GAME_OVER;
            return;
        }
        
        // 自身碰撞检测
        for (const auto& segment : snake) {
            if (newHead == segment) {
                gameState = GAME_OVER;
                return;
            }
        }
        
        // 添加新头部
        snake.insert(snake.begin(), newHead);
        
        // 检查是否吃到食物
        if (newHead == food) {
            score++;
            generateFood();
            
            // 每吃一定数量的食物增加速度
            if (score % SPEED_INCREASE_THRESHOLD == 0) {
                speed = (std::max)(MIN_SPEED, speed - 10);
            }
        } else {
            // 没吃到食物，移除尾部
            snake.pop_back();
        }
    }
    
    void render() {
        buffer.clear();
        
        switch (gameState) {
            case MENU:
                renderMenu();
                break;
            case PLAYING:
            case PAUSED:
                renderGame();
                if (gameState == PAUSED) {
                    renderPauseScreen();
                }
                break;
            case GAME_OVER:
                renderGame();
                renderGameOverScreen();
                break;
        }
        
        buffer.render();
    }
    
    void renderMenu() {
        // 标题
        std::string title = "SNAKE GAME";
        std::string subtitle = "GITHUB STYLE";
        
        buffer.drawText(WINDOW_WIDTH / 2 - title.length() / 2, WINDOW_HEIGHT / 2 - 5, title);
        buffer.drawText(WINDOW_WIDTH / 2 - subtitle.length() / 2, WINDOW_HEIGHT / 2 - 3, subtitle);
        
        // 开始按钮
        std::string start = "PRESS SPACE TO START";
        buffer.drawText(WINDOW_WIDTH / 2 - start.length() / 2, WINDOW_HEIGHT / 2 + 1, start);
        
        // 控制说明
        std::string controls1 = "USE ARROW KEYS OR WASD TO MOVE";
        std::string controls2 = "PRESS P TO PAUSE, ESC TO QUIT";
        
        buffer.drawText(WINDOW_WIDTH / 2 - controls1.length() / 2, WINDOW_HEIGHT / 2 + 4, controls1);
        buffer.drawText(WINDOW_WIDTH / 2 - controls2.length() / 2, WINDOW_HEIGHT / 2 + 5, controls2);
        
        // 绘制边框
        buffer.drawBox(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);
    }
    
    void renderGame() {
        // 绘制边框
        buffer.drawBox(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);
        
        // 绘制网格
        for (int x = 2; x < WINDOW_WIDTH - 1; x += 3) {
            for (int y = 2; y < WINDOW_HEIGHT - 1; y += 3) {
                buffer.drawChar(x, y, '.');
            }
        }
        
        // 绘制食物
        buffer.drawChar(food.x, food.y, '@', Colors::GITHUB_ORANGE);
        
        // 绘制蛇
        for (size_t i = 0; i < snake.size(); ++i) {
            if (i == 0) {
                // 蛇头
                buffer.drawChar(snake[i].x, snake[i].y, 'O', Colors::GITHUB_BLUE);
            } else {
                // 蛇身
                buffer.drawChar(snake[i].x, snake[i].y, 'o', Colors::GITHUB_LIGHT_BLUE);
            }
        }
        
        // 绘制分数和速度
        std::string scoreText = "SCORE: " + to_string(score);
        std::string speedText = "SPEED: " + to_string((INITIAL_SPEED - speed) / 10 + 1) + "/5";
        
        buffer.drawText(2, 0, scoreText);
        buffer.drawText(WINDOW_WIDTH - speedText.length() - 2, 0, speedText);
    }
    
    void renderPauseScreen() {
        std::string pauseText = "PAUSED";
        std::string resumeText = "PRESS P TO RESUME";
        
        // 绘制半透明背景
        for (int y = WINDOW_HEIGHT / 2 - 2; y <= WINDOW_HEIGHT / 2 + 2; ++y) {
            for (int x = WINDOW_WIDTH / 2 - pauseText.length() / 2 - 2; x <= WINDOW_WIDTH / 2 + pauseText.length() / 2 + 1; ++x) {
                buffer.drawChar(x, y, ' ');
            }
        }
        
        buffer.drawText(WINDOW_WIDTH / 2 - pauseText.length() / 2, WINDOW_HEIGHT / 2 - 1, pauseText);
        buffer.drawText(WINDOW_WIDTH / 2 - resumeText.length() / 2, WINDOW_HEIGHT / 2 + 1, resumeText);
        
        // 绘制边框
        buffer.drawBox(WINDOW_WIDTH / 2 - pauseText.length() / 2 - 3, WINDOW_HEIGHT / 2 - 3, 
                      pauseText.length() + 6, 7);
    }
    
    void renderGameOverScreen() {
        std::string gameOverText = "GAME OVER";
        std::string finalScoreText = "SCORE: " + to_string(score);
        std::string restartText = "PRESS SPACE TO PLAY AGAIN";
        
        // 绘制半透明背景
        for (int y = WINDOW_HEIGHT / 2 - 3; y <= WINDOW_HEIGHT / 2 + 3; ++y) {
            for (int x = WINDOW_WIDTH / 2 - gameOverText.length() / 2 - 3; x <= WINDOW_WIDTH / 2 + gameOverText.length() / 2 + 2; ++x) {
                buffer.drawChar(x, y, ' ');
            }
        }
        
        buffer.drawText(WINDOW_WIDTH / 2 - gameOverText.length() / 2, WINDOW_HEIGHT / 2 - 2, gameOverText);
        buffer.drawText(WINDOW_WIDTH / 2 - finalScoreText.length() / 2, WINDOW_HEIGHT / 2, finalScoreText);
        buffer.drawText(WINDOW_WIDTH / 2 - restartText.length() / 2, WINDOW_HEIGHT / 2 + 2, restartText);
        
        // 绘制边框
        buffer.drawBox(WINDOW_WIDTH / 2 - gameOverText.length() / 2 - 4, WINDOW_HEIGHT / 2 - 4, 
                      gameOverText.length() + 8, 9);
    }
    
    void run() {
        while (true) {
            handleInput();
            update();
            render();
            
            if (gameState == PLAYING) {
                Console::sleep(speed);
            } else {
                Console::sleep(50); // 非游戏状态下减少CPU使用
            }
        }
    }
};

int main() {
    Console::init(); // 初始化控制台
    Console::clear();
    
    SnakeGame game;
    game.run();
    
    Console::showCursor();
    
    return 0;
}