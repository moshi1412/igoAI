# AI 围棋对战平台

## 项目简介

这是一个基于蒙特卡洛树搜索（MCTS）和 Minimax 算法的围棋 AI 对战平台，支持人机对战、AI vs AI 对战以及批量测试功能。

## 功能特性

- **多种 AI 智能体**
  - Random Agent（随机智能体）
  - MCTS Agent（蒙特卡洛树搜索智能体）
    - 支持多种策略：Random、Remove First、Liberty First、RAVE
    - RAVE 策略（快速走子评估）
  - Minimax Agent（极小极大智能体）
    - 支持 Minimax 和 Alpha-Beta 剪枝
    - 支持 Stone Eval 和 Territory Eval 评估函数

- **多种游戏模式**
  - Player vs AI（人机对战）
  - AI vs AI（AI 对战）
  - Test Mode（批量测试模式）
  - Debug Mode（调试模式）

## 环境要求

- Python 3.8+
- pygame 2.0+

## 安装步骤

### 1. 克隆或下载项目

```bash
cd ai-course-hw1
```

### 2. 创建虚拟环境（推荐）

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install pygame
```

## 运行方式

### 方式一：图形界面启动（推荐）

```bash
python start_game.py
```

这会打开一个图形化的主菜单，您可以：
- 选择游戏模式
- 选择棋盘大小
- 选择 AI 智能体类型
- 配置 AI 参数
- 开始游戏

### 方式二：命令行参数

```bash
# 人机对战
python -c "from play import play_pva; play_pva(board_size=5, agent_type='mcts')"

# AI 对战
python -c "from play import play_ava; play_ava(board_size=5, agent1_type='mcts', agent2_type='random')"

# 测试模式
python gui/ai_vs_ai_test.py --size 5 --ai1 mcts --ai2 random --games 10
```

## 主要文件说明

### 核心文件

- `start_game.py` - 主程序入口，启动图形界面
- `play.py` - 游戏逻辑和代理函数

### 智能体文件

- `agents/random_agent.py` - 随机智能体
- `agents/mcts_agent.py` - MCTS 智能体
- `agents/minimax_agent.py` - Minimax 智能体

### 界面文件

- `gui/main_menu.py` - 主菜单界面
- `gui/game_gui.py` - 双人对战界面
- `gui/ai_gui.py` - 人机对战界面
- `gui/ai_vs_ai.py` - AI 对战界面
- `gui/ai_vs_ai_test.py` - AI 对战测试界面
- `gui/debug_gui.py` - 调试界面

### 围棋库文件

- `dlgo/gotypes.py` - 围棋基础类型
- `dlgo/goboard.py` - 棋盘和游戏状态
- `dlgo/scoring.py` - 评分系统
- `dlgo/zobrist.py` - Zobrist 哈希

## MCTS 参数配置

在主菜单中可以配置以下 MCTS 参数：

- **Num Rounds**：搜索轮数（默认 100）
- **Strategy**：
  - Random：随机策略
  - Remove First：优先提子
  - Liberty First：优先占气
  - RAVE：快速走子评估
- **RAVE k**：RAVE 策略的权重参数（默认 300）

## Minimax 参数配置

- **Strategy**：
  - minmax：基础 Minimax
  - Alpha-Beta：Alpha-Beta 剪枝
- **Max Depth**：最大搜索深度（默认 3）
- **Eval**：
  - Stone Eval：基于棋子数和气数评估
  - Territory Eval：基于地盘评估

## 键盘快捷键

- **空格键**：在测试模式下暂停/继续
- **Back 按钮**：返回主菜单

## 测试模式

测试模式可以批量运行多局 AI 对战，并自动统计：
- 黑白双方胜场数
- 平局数
- 平均步数
- 平均用时
- 最后两步棋（方便查看 PASS 和 RESIGN

## 调试模式

调试模式可以可视化 MCTS 搜索树，帮助理解搜索过程。

## 常见问题

### 1. 导入错误

如果遇到 `ModuleNotFoundError`，请确保：
- 当前工作目录在项目根目录
- 已正确安装所有依赖

### 2. 统计数据不一致

已修复统计问题，现在所有对局都会被正确统计，包括：
- 正常结束的对局
- 平局
- 强制结束的对局
- 提前退出的对局

### 3. 棋子和红框大小

棋子和红框大小已优化，显示更精致。

## 项目结构

```
ai-course-hw1/
├── agents/
│   ├── __init__.py
│   ├── random_agent.py
│   ├── mcts_agent.py
│   └── minimax_agent.py
├── dlgo/
│   ├── __init__.py
│   ├── gotypes.py
│   ├── goboard.py
│   ├── scoring.py
│   └── zobrist.py
├── gui/
│   ├── __init__.py
│   ├── main_menu.py
│   ├── game_gui.py
│   ├── ai_gui.py
│   ├── ai_vs_ai.py
│   ├── ai_vs_ai_test.py
│   └── debug_gui.py
├── play.py
├── start_game.py
└── README.md
```

## 许可证

本项目为课程作业项目。


