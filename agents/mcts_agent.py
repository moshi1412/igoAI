"""
MCTS (蒙特卡洛树搜索) 智能体模板。

学生作业：完成 MCTS 算法的核心实现。
参考：《深度学习与围棋》第 4 章
"""

from dlgo.gotypes import Player, Point
from dlgo.goboard import GameState, Move
from .random_agent import RandomAgent
import math
import time
__all__ = ["MCTSAgent"]



class MCTSNode:
    """
    MCTS 树节点。


    属性：
        game_state: 当前局面
        parent: 父节点（None 表示根节点）
        children: 子节点列表
        visit_count: 访问次数
        value_sum: 累积价值（胜场数）
        prior: 先验概率（来自策略网络，可选）
    """

    def __init__(self, game_state, parent=None, prior=1.0):
        self.game_state = game_state
        self.parent = parent
        self.children = []
        self.visit_count = 0
        self.value_sum = 0
        self.prior = prior
        
        # TODO: 初始化其他必要属性
        self.remove_num=0
        self.delta_liberty=0
    @property
    def value(self):
        """计算平均价值 = value_sum / visit_count，防止除零。"""
        # TODO: 实现价值计算
        value=self.value_sum / self.visit_count if self.visit_count > 0 else 0
        return value
    def child_stone_remove_num(self):
        """计算移除棋子数。"""
        for node in self.children:
            if node.game_state.last_move is None:
                continue
            node.remove_num = self.game_state.num_remove_stone(node.game_state.last_move)
        
    def is_leaf(self):
        """是否为叶节点（未展开）。"""
        return len(self.children) == 0

    def is_terminal(self):
        """是否为终局节点。"""
        return self.game_state.is_over()
    def UCT_cal(self, c=1.414, strategy='random'):
        if strategy == "remove_first":
            return [node.remove_num + node.value + c * math.sqrt(math.log(self.visit_count) / node.visit_count) for node in self.children]
        elif strategy == "liberty_first":
            return [node.delta_liberty + node.value + c * math.sqrt(math.log(self.visit_count) / node.visit_count) for node in self.children]
        else:
            return [node.value + c * math.sqrt(math.log(self.visit_count) / node.visit_count) for node in self.children]
        return [node.value + c * math.sqrt(math.log(self.visit_count) / node.visit_count) for node in self.children]
    def best_child(self, c=1.414,strategy='random'):
        """
        选择最佳子节点（UCT 算法）。

        UCT = value + c * sqrt(ln(parent_visits) / visits)

        Args:
            c: 探索常数（默认 sqrt(2)）

        Returns:
            最佳子节点
        """
        #还要判断0
        # TODO: 实现 UCT 选择
        for node in self.children:
            if node.visit_count==0:
                return node
        UCT_value=self.UCT_cal(c,strategy)
        best_index=UCT_value.index(max(UCT_value))
        return self.children[best_index]

    def expand(self):
        """
        展开节点：为所有合法棋步创建子节点。

        Returns:
            新创建的子节点（用于后续模拟）
        """
        # TODO: 实现节点展开
        possible_moves=self.game_state.legal_moves()
        # if possible_moves==[]:
        #     return Move(is_pass=True)   
        
        for move in possible_moves:
            # new_game_state=deepcopy(self.game_state)
            new_game_state=self.game_state.apply_move(move)
            new_child=MCTSNode(new_game_state,self)
            self.children.append(new_child)
        
        self.child_stone_remove_num()
        self.delta_liberty_num()
        return self.children
    def delta_liberty_num(self):
        """计算气数变化。"""
        for node in self.children:
            if node.game_state.last_move is None:
                node.delta_liberty=0
            
            delta_liberty_before =self.game_state.delta_liberty_num(self.game_state.next_player)#当前盘 子节点颜色
            delta_liberty_after=node.game_state.delta_liberty_num(self.game_state.next_player)#子盘 子节点颜色
            node.delta_liberty=delta_liberty_after-delta_liberty_before
            # print(node.game_state.last_move.point,node.delta_liberty)
            # print(node.game_state.last_move.point,"this ",liberty_bef,liberty_after,"other",liberty_other_bef,liberty_other_after)
       
    def backup(self, value):
        """
        反向传播：更新从当前节点到根节点的统计。

        Args:
            value: 从当前局面模拟得到的结果（1=胜，0=负，0.5=和）
        """
        
        # TODO: 实现反向传播
        node=self
        # print(value)
        while node!=None:           
            node.visit_count+=1
            node.value_sum+=value
            # print(node.game_state.last_move.point)
            #value 取反
            value=1-value
            node=node.parent

class MCTSAgent:
    """
    MCTS 智能体。

    属性：
        num_rounds: 每次决策的模拟轮数
        temperature: 温度参数（控制探索程度）
        last_root: 最后一次搜索的根节点（用于debug可视化）
    """

    def __init__(self, num_rounds=1000, temperature=1.0,strategy='random'):
        self.num_rounds = num_rounds
        self.temperature = temperature
        # self.random_agent_b=RandomAgent()
        # self.random_agent_w=RandomAgent()
        self.strategy=strategy
        self.last_root = None

    def select_move(self, game_state: GameState) -> Move:
        """
        为当前局面选择最佳棋步。

        流程：
            1. 创建根节点
            2. 进行 num_rounds 轮模拟：
               a. Selection: 用 UCT 选择路径到叶节点
               b. Expansion: 展开叶节点
               c. Simulation: 随机模拟至终局
               d. Backup: 反向传播结果
            3. 选择访问次数最多的棋步

        Args:
            game_state: 当前游戏状态

        Returns:
            选定的棋步
        """
        # TODO: 实现 MCTS 主循环
        start_time=time.time()
        root=MCTSNode(game_state)
        root.expand()
        
        for round in range(self.num_rounds):     
            node=root       
            while not node.is_leaf():
                node=node.best_child()
            else:
                #resign不扩展
                if not node.game_state.last_move.is_resign:
                    node.expand()
                # if node.game_state.last_move.is_resign:
                #    print("resign")
                sim_result=self._simulate(node.game_state)
                node.backup(sim_result)            
        self.last_root = root
        end_time=time.time()
        print(f"搜索时间：{end_time-start_time}秒")

        return self._select_best_move(root)

    def _simulate(self, game_state):
        """
        快速模拟（Rollout）：随机走子至终局。

        【第二小问要求】
        标准 MCTS 使用完全随机走子，但需要实现至少两种优化方法：
        1. 启发式走子策略（如：优先选有气、不自杀、提子的走法）
        2. 限制模拟深度（如：最多走 20-30 步后停止评估）
        3. 其他：快速走子评估（RAVE）、池势启发等

        Args:
            game_state: 起始局面

        Returns:
            从当前玩家视角的结果（1=胜, 0=负, 0.5=和）
        """
        #normal realize
        # game_state=game_state
        sum_player=game_state.next_player.other
        # print(sum_player)
        # score=0.5
        winner=random_play(game_state)
        # print_board(game_state)
        if winner:
            # print("胜者：",winner.name)
            if winner==sum_player:
                score=1
            else:
                score=0
        else:
            # print("平局")
            score=0.5
        # if verbose:
        #     print("\n=== 终局 ===")
        #     print_board(game_state)
        #     if winner:
        #         print(f"胜者: {winner.name}")
        #     else:
        #         print("平局")

        return score
        # TODO: 实现快速模拟（含两种优化策略）
        pass

    def _select_best_move(self, root):
        """
        根据UCT选择最佳棋步。

        Args:
            root: MCTS 树根节点

        Returns:
            最佳棋步
        """
        # TODO: 根据访问次数或价值选择
        # for node in root.children:
        #     print(node.game_state.last_move.point,node.visit_count,node.value,node.remove_num,node.delta_liberty,'\n')      #根据价值选择
        return root.best_child(strategy=self.strategy).game_state.last_move



def random_play(game_state):
        agents = {
            Player.black:RandomAgent(),
            Player.white:RandomAgent(),
        }
        # if game_state.last_move.is_resign:
        #     print("resign")
        move_count = 0
        while not game_state.is_over():
            agent_fn = agents[game_state.next_player]
            move = agent_fn.select_move(game_state)
            game_state = game_state.apply_move(move)
            move_count += 1

            if move_count > game_state.board.num_rows * game_state.board.num_cols * 2:
                # print("[WARN] 步数过多，强制结束")
                # print_board(game_state)
                return winner_def(game_state)
                break
        
        winner = game_state.winner()
        return winner if winner else None 

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
def winner_def(game_state):
    """根据气的比较判断胜者。"""
    liberty={Player.black:0,Player.white:0}
    liberty[Player.black]=game_state.get_all_liberties_num(game_state.board,Player.black)
    liberty[Player.white]=game_state.get_all_liberties_num(game_state.board,Player.white)
    if liberty[Player.black]>liberty[Player.white]:
        return Player.black
    elif liberty[Player.white]>liberty[Player.black]:
        return Player.white
    else:
        return None
    