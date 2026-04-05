# iGo GUI

## Installation

First install pygame:

```bash
pip install pygame
```

## Usage

### Recommended: Using the Launcher (Start Game with Main Menu)

Run from project root directory:

```bash
python start_game.py
```

This will show a main menu with "iGo" title, START button, and settings interface with:
- Three game modes:
  - Player vs Player
  - Player vs AI
  - AI vs AI
- Board size configuration
- AI agent selection:
  - For Player vs AI: select AI type
  - For AI vs AI: select both AI 1 (Black) and AI 2 (White) types
- Debug mode checkbox

### Alternative: Direct GUI Files

#### 1. Player vs Player Mode

```bash
python gui/game_gui.py --size 5
```

Options:
- `--size`: Board size, default 5

#### 2. Player vs AI Mode

```bash
python gui/ai_gui.py --size 5 --ai random
```

Options:
- `--size`: Board size, default 5
- `--ai`: AI agent type, choices: random, mcts, minimax, default random
- `--ai_first`: Let AI play first (default human first)

#### 3. AI vs AI Mode

```bash
python gui/ai_vs_ai.py --size 5 --ai1 random --ai2 mcts
```

Options:
- `--size`: Board size, default 5
- `--ai1`: AI 1 (Black) agent type, choices: random, mcts, minimax, default random
- `--ai2`: AI 2 (White) agent type, choices: random, mcts, minimax, default random
- Press SPACE to pause/resume

#### 4. Debug Mode with MCTS Tree Visualization

```bash
python gui/debug_gui.py --size 5
```

Or via the main menu with Debug mode checked, Player vs AI mode, and MCTS AI selected.

Features:
- Dual-panel display: Left = Board, Right = MCTS Tree
- Tree nodes as circles showing:
  - Value sum (top, 2 decimal places)
  - Visit count (bottom)
- Root node in red, other nodes in blue
- Drag to scroll tree view

## Features

- Classic Go board background
- Black and white circular stones
- Real-time current player display
- Winner display when game ends
- Click anywhere to restart
- Supports different board sizes
- All text in English
- Three game modes available
- AI vs AI mode with pause functionality
- Debug mode with MCTS tree visualization
