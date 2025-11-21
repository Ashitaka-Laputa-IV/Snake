# Snake Game - GitHub Style

一个采用GitHub风格的贪吃蛇游戏，同时提供Python桌面版和Web版本。

## 项目结构

```
Snake/
├── src/                    # Web版本源代码
│   ├── css/               # 样式文件
│   │   └── style.css      # GitHub风格样式表
│   ├── js/                # JavaScript文件
│   │   └── game.js        # 游戏逻辑
│   ├── images/            # 图片资源（预留）
│   └── index.html         # 主页面
├── scripts/               # Python脚本
│   └── snake.py           # Python版本游戏
├── assets/                # 资源文件（预留）
├── docs/                  # 文档（预留）
├── requirements.txt       # Python依赖
└── README.md             # 项目说明文档
```

## 如何运行

### Web版本
1. 在项目根目录启动本地服务器：
   ```
   python -m http.server 8000
   ```
2. 在浏览器中访问：http://localhost:8000/src/

### Python版本
1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
2. 运行游戏：
   ```
   python scripts/snake.py
   ```

## 游戏控制

- **方向键/WASD**：控制蛇的移动方向
- **空格键**：开始游戏/重新开始
- **P键**：暂停/继续游戏
- **ESC键**：退出游戏

## 特点

- GitHub风格设计
- 响应式布局，支持移动设备
- 流畅的游戏体验
- 清晰的游戏边界和视觉效果

## 开发说明

本项目采用模块化结构，Web版本和Python版本共享相同的设计理念和游戏逻辑。