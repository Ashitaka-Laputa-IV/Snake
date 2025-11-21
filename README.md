# Snake Game - 多语言实现

这是一个使用三种不同编程语言实现的贪吃蛇游戏项目，每个版本都采用了GitHub风格的设计语言，提供了统一的视觉体验。

## 项目结构

```
Snake/
├── README.md              # 项目说明文档
├── web-snake/             # Web版本（HTML/CSS/JavaScript）
│   ├── index.html         # 主页面
│   ├── css/
│   │   └── style.css      # 样式文件
│   └── js/
│       └── game.js        # 游戏逻辑
├── py-snake/              # Python版本
│   ├── snake.py           # 游戏主程序
│   └── requirements.txt    # 依赖列表
└── cpp-snake/             # C++版本
    ├── snake.cpp           # 游戏主程序
    └── snake.exe           # 编译后的可执行文件
```

## 游戏特性

- **统一GitHub风格设计**：所有版本都采用GitHub的深色主题和配色方案
- **响应式控制**：支持方向键和WASD键控制
- **渐进难度**：随着分数增加，游戏速度逐渐提升
- **暂停功能**：按P键可以暂停/继续游戏
- **视觉效果**：网格背景、渐变蛇身、动态食物等

## 各版本详情

### Web版本 (web-snake)

**技术栈**：HTML5 Canvas, CSS3, JavaScript

**特点**：
- 基于Canvas的流畅渲染
- 响应式设计，适配不同屏幕尺寸
- 现代Web技术实现
- 可直接在浏览器中运行

**运行方法**：
1. 直接打开 `web-snake/index.html` 文件
2. 或使用本地服务器托管该目录

**控制方式**：
- 方向键或WASD：移动蛇
- 空格键：开始游戏
- P键：暂停/继续
- ESC键：退出

### Python版本 (py-snake)

**技术栈**：Python, Pygame

**特点**：
- 使用Pygame库实现
- 跨平台支持（Windows/Linux/Mac）
- 性能优化，支持性能模式切换
- 60 FPS流畅游戏体验

**运行方法**：
```bash
# 安装依赖
pip install -r requirements.txt

# 运行游戏
python snake.py
```

**控制方式**：
- 方向键或WASD：移动蛇
- 空格键：开始游戏
- P键：暂停/继续
- ESC键：退出
- F1键：切换性能模式

### C++版本 (cpp-snake)

**技术栈**：C++, 标准库

**特点**：
- 纯C++实现，无外部依赖
- 跨平台控制台应用
- 双缓冲渲染技术，减少闪烁
- 高性能，低资源占用

**编译与运行**：

**Windows (使用clang++)**：
```powershell
cd cpp-snake
clang++ -o snake.exe snake.cpp
.\snake.exe
```

**Linux/Mac**：
```bash
cd cpp-snake
clang++ -o snake snake.cpp
./snake
```

**控制方式**：
- 方向键或WASD：移动蛇
- 空格键：开始游戏
- P键：暂停/继续
- ESC键：退出

## 游戏规则

1. 控制蛇移动吃食物（橙色方块）
2. 每吃一个食物，蛇身增长一节，分数加1
3. 撞到墙壁或自己的身体游戏结束
4. 每吃5个食物，游戏速度提升一级

## 开发说明

### GitHub风格设计

所有版本都采用以下GitHub风格配色：
- 背景色：#0d1117（深色背景）
- 网格线：#161b22
- 蛇头：#388bfd（GitHub蓝）
- 蛇身：#58a6ff（浅蓝色）
- 食物：#ef6c00（橙色）
- 文本：#e5e7eb

### 技术亮点

1. **Web版本**：
   - Canvas渲染优化
   - 响应式布局
   - 流畅动画效果

2. **Python版本**：
   - 游戏循环优化
   - 性能模式切换
   - 跨平台字体处理

3. **C++版本**：
   - 双缓冲渲染
   - 跨平台控制台操作
   - 高效内存管理

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过GitHub Issues联系。