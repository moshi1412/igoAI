"""
第一小问（必做）：随机 AI

基于随机落子（但需满足规则）的基础围棋 AI
用于验证规则调用和基础设施正常工作。
"""

import random
from dlgo import GameState, Move

__all__ = ["RandomAgent"]


class RandomAgent:
    """
    随机落子智能体 - 第一小问实现

    从所有合法棋步中均匀随机选择，包括：
    - 正常落子
    - 停一手 (pass)
    - 认输 (resign)
    """

    def __init__(self):
        """初始化随机智能体（无需特殊参数）"""
        # DONE: 学生实现
        # self.board_size=None
        pass

    def select_move(self, game_state: GameState) -> Move:
        """
        选择随机合法棋步

        Args:
            game_state: 当前游戏状态

        Returns:
            随机选择的合法 Move
        """
        # DONE: 学生实现
        # 提示：使用 game_state.legal_moves() 获取所有合法棋步
        # 提示：使用 random.choice() 随机选择
        #point 需要棋盘的大小 game_state.board_size
        #board_size (x,y)
        # self.board_size=game_state.board_size if self.board_size is None else self.board_size
        #均匀随机选取point
        #棋盘上所有的点
       
        possible_moves=[move.point for move in game_state.legal_moves() if move.point is not None]
        # print(possible_moves)
        if possible_moves==[]:
            return Move(is_pass=True)
        point=random.choice(possible_moves)
        return Move(point=point)

    


# 便捷函数（向后兼容 play.py）
def random_agent(game_state: GameState) -> Move:
    """函数接口，兼容 play.py 的调用方式"""
    agent = RandomAgent()
    return agent.select_move(game_state)