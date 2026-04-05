"""
第三小问（选做）：Minimax 智能体

实现 Minimax + Alpha-Beta 剪枝算法，与 MCTS 对比效果。
可选实现，用于对比不同搜索算法的差异。

参考：《深度学习与围棋》第 3 章
"""

from dlgo.gotypes import Player,Point
from dlgo.goboard import GameState, Move
from copy import deepcopy
__all__ = ["MinimaxAgent"]

INF=1e5

class MinimaxAgent:
    """
    Minimax 智能体（带 Alpha-Beta 剪枝）。

    属性：
        max_depth: 搜索最大深度
        evaluator: 局面评估函数
    """

    def __init__(self, max_depth=3, evaluator=None):
        self.max_depth = max_depth
        # 默认评估函数（TODO：学生可替换为神经网络）
        self.evaluator = evaluator or self._default_evaluator
        self.player=None

    def select_move(self, game_state: GameState,strategy='minimax') -> Move:
        """
        为当前局面选择最佳棋步。

        Args:
            game_state: 当前游戏状态

        Returns:
            选定的棋步
        """
        # TODO: 实现 Minimax 搜索，调用 minimax 或 alphabeta
        self.player=game_state.next_player
        if strategy=='minmax':
            _,best_state=self.minimax(game_state, self.max_depth, True)
            return best_state.last_move
        if strategy=='alphabeta':
            _,best_state=self.alphabeta(game_state, self.max_depth, -INF, INF, True)
            return best_state.last_move
        
        

    def minimax(self, game_state, depth, maximizing_player):
        """
        基础 Minimax 算法。

        Args:
            game_state: 当前局面
            depth: 剩余搜索深度
            maximizing_player: 是否在当前层最大化（True=我方）

        Returns:
            该局面的评估值和最佳节点
        """
        # TODO: 实现 Minimax
        # 提示：
        # 1. 终局或 depth=0 时返回评估值
        # 2. 如果是最大化方：取所有子节点最大值
        # 3. 如果是最小化方：取所有子节点最小值
        # print(depth,game_state.last_move)
        # if depth is not None:
            # print_board(game_state)
            # print(game_state)
        #没有节点类 只能递归？
        if game_state.is_over() or depth==0:
            value=self.evaluator(game_state,maximizing_player)
            # print(value)
            return value,game_state
        # possible_moves=game_state.legal_moves()  
        pos_moves=self._get_ordered_moves(game_state)
        children_state=[]
        child_value=[]
        for move in pos_moves:
            # new_game_state=deepcopy(game_state)
            new_game_state=game_state.apply_move(move)
            children_state.append(new_game_state)

        for child_state in children_state:
            value,_=self.minimax(child_state, depth-1, not maximizing_player)
            child_value.append(value)
        
        if maximizing_player:
            # print(max(child_value),children_state[child_value.index(max(child_value))].last_move)
            return max(child_value),children_state[child_value.index(max(child_value))]
        else:
            # if depth==2:
            #     print(child_value,children_state[child_value.index(min(child_value))].last_move)
            return min(child_value),children_state[child_value.index(min(child_value))]
        

    def alphabeta(self, game_state, depth, alpha, beta, maximizing_player):
        """
        Alpha-Beta 剪枝优化版 Minimax。

        Args:
            game_state: 当前局面
            depth: 剩余搜索深度
            alpha: 当前最大下界
            beta: 当前最小上界
            maximizing_player: 是否在当前层最大化

        Returns:
            该局面的评估值
        """
        # TODO: 实现 Alpha-Beta 剪枝
        # 提示：在 minimax 基础上添加剪枝逻辑
        # - 最大化方：如果 value >= beta 则剪枝
        # - 最小化方：如果 value <= alpha 则剪枝
        this_alpha=-INF
        this_beta=INF  
        if depth==0 or game_state.is_over():
            return self.evaluator(game_state,maximizing_player),game_state
        
        pos_moves=self._get_ordered_moves(game_state)
        pos_states=[game_state.apply_move(move) for move in pos_moves]
        # best_state=None
        best_value=None
        for i,move in enumerate(pos_moves):
            # new_game_state=game_state.apply_move(move)
            value,_=self.alphabeta(pos_states[i], depth-1, this_alpha, this_beta, not maximizing_player)
            if depth==2:
                print_board(pos_states[i])
                print(value)
                print(alpha,beta)
            
            if maximizing_player:
                if value>this_alpha:
                    this_alpha=value
                if best_value is None or value>best_value:
                    best_value=value
                    best_id=i
                if best_value>=beta:
                    return best_value,pos_states[best_id]
            else:
                if value<this_beta:
                    this_beta=value
                if best_value is None or value<best_value:
                    best_value=value
                    best_id=i
                if best_value<=alpha:
                    return best_value,pos_states[best_id]
        
        return best_value,pos_states[best_id]
        

    def _default_evaluator(self, game_state,max_player):
        """
        默认局面评估函数（简单版本）。

        学生作业：替换为更复杂的评估函数，如：
            - 气数统计
            - 眼位识别
            - 神经网络评估

        Args:
            game_state: 游戏状态

        Returns:
            评估值（正数对我方有利）
        """
        # TODO: 实现简单的启发式评估
        # 示例：子数差 + 气数差
        # if max_player:
        #     player=game_state.next_player
        # else:
        #     player=game_state.next_player.other
        #直接投降需要给一些惩罚 对面选择投降则需要加分
        if game_state.next_player==self.player:
            punish=4   if not game_state.last_move.is_play else 0
        elif game_state.next_player==self.player.other:
            punish=-4   if not game_state.last_move.is_play else 0
        delta_liberty=game_state.delta_liberty_num(self.player)

        #子数
        this_stones=[key for key,value in game_state.board._grid.items() if value is not None and value.color==self.player]
        this_stone_num=len(this_stones)
        other_stones=[key for key,value in game_state.board._grid.items() if value is not None and value.color!=self.player]
        other_stone_num=len(other_stones)
        delta_stones_num=this_stone_num-other_stone_num
        return delta_stones_num+delta_liberty+punish

    def _get_ordered_moves(self, game_state):
        """
        获取排序后的候选棋步（用于优化剪枝效率）。

        好的排序能让 Alpha-Beta 剪掉更多分支。

        Args:
            game_state: 游戏状态

        Returns:
            按启发式排序的棋步列表
        """
        # TODO: 实现棋步排序
        # 提示：优先检查吃子、提子、连络等好棋
        moves = game_state.legal_moves()
        #投降可耻
        if game_state.next_player==self.player:
            punishes=[-4  if not move.is_play else 0 for move in moves]
        else:
             punishes=[4  if not move.is_play else 0 for move in moves]
       

        #吃子 
        # moves_remove = [game_state.num_remove_stone(move,self.player.other) for move in moves]#按照这个进行排序
        # moves=sorted(moves,key=lambda x: moves_remove[moves.index(x)],reverse=True)#从多到少
        
        #联络 且 不能紧自己的气
        moves_connect=[game_state.if_connect(self.player,move) for move in moves ]
        #紧气
        lib_num_bef=game_state.get_all_liberties_num(game_state.board,self.player)
        lib_delta=[game_state.apply_move(move).get_all_liberties_num(game_state.apply_move(move).board,self.player)-lib_num_bef for move in moves]
        
        sorted_key=[0.5*moves_connect[i]+0.5*lib_delta[i]+punishes[i] for i in range(len(moves))]

        moves=sorted(moves,key=lambda x: sorted_key[moves.index(x)],reverse=True)#从多到少


        return moves  #



class GameResultCache:
    """
    局面缓存（Transposition Table）。

    用 Zobrist 哈希缓存已评估的局面，避免重复计算。
    """

    def __init__(self):
        self.cache = {}

    def get(self, zobrist_hash):
        """获取缓存的评估值。"""
        return self.cache.get(zobrist_hash)

    def put(self, zobrist_hash, depth, value, flag='exact'):
        """
        缓存评估结果。

        Args:
            zobrist_hash: 局面哈希
            depth: 搜索深度
            value: 评估值
            flag: 'exact'/'lower'/'upper'（精确值/下界/上界）
        """
        # TODO: 实现缓存逻辑（考虑深度优先替换策略）
        pass

def print_board(game_state):
            """打印棋盘（简化版）。"""
            board = game_state.board
            print("  ", end="")
            for c in range(1, board.num_cols + 1):
                print(f"{c:2}", end="")
            print()

            for r in range(1, board.num_rows + 1):
                print(f"{r:2}", end="")
                for c in range(1, board.num_cols + 1):
                    stone = board.get(Point(r, c))
                    if stone == Player.black:
                        print(" X", end="")
                    elif stone == Player.white:
                        print(" O", end="")
                    else:
                        print(" .", end="")
                print()