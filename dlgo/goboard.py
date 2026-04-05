"""
围棋棋盘和游戏规则实现模块。

本模块提供：
- Board: 棋盘数据结构，支持落子、提子、Zobrist哈希
- GameState: 游戏状态机（不可变设计），支持劫判定
- Move: 棋步（落子/停一手/认输）
"""

import copy
from .gotypes import Player, Point
from .scoring import compute_game_result
from . import zobrist

__all__ = ["Board", "GameState", "Move"]


class IllegalMoveError(Exception):
    """非法移动异常。"""

    pass


class GoString:
    """
    同色连通棋串（气、子连通块）。

    Attributes:
        color: 棋串颜色
        stones: 棋串包含的所有棋子坐标（frozenset）
        liberties: 棋串的所有气（frozenset）

    Note:
        使用 frozenset 实现不可变性，便于 GameState 的拷贝。
    """

    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        """返回去掉一个气后的新棋串（不修改原对象）。"""
        new_liberties = self.liberties - {point}
        return GoString(self.color, self.stones, new_liberties)

    def with_liberty(self, point):
        """返回增加一个气后的新棋串（不修改原对象）。"""
        new_liberties = self.liberties | {point}
        return GoString(self.color, self.stones, new_liberties)

    def merged_with(self, string):
        """
        将当前棋串与另一同色棋串合并。

        Args:
            string: 要合并的棋串（必须同色）

        Returns:
            新的合并后棋串
        """
        assert string.color == self.color, "只能合并同色棋串"
        combined_stones = self.stones | string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | string.liberties) - combined_stones,
        )

    @property
    def num_liberties(self):
        """返回棋串的气数。"""
        return len(self.liberties)

    def __eq__(self, other):
        if not isinstance(other, GoString):
            return False
        return (
            self.color == other.color
            and self.stones == other.stones
            and self.liberties == other.liberties
        )

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        return GoString(self.color, self.stones, copy.deepcopy(self.liberties))


class Board:
    """
    围棋棋盘。

    使用字典存储棋盘状态，支持快速访问和更新。
    使用 Zobrist 哈希实现 O(1) 局面比较（用于劫判定）。

    Attributes:
        num_rows: 行数
        num_cols: 列数
    """

    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}  # Point -> GoString，空点无键
        self._hash = zobrist.EMPTY_BOARD

    def place_stone(self, player, point):
        """
        在指定位置落子。

        Args:
            player: 落子玩家
            point: 落子位置

        Raises:
            AssertionError: 如果位置越界或已被占据
        """
        # 基本合法性检查
        assert self.is_on_grid(point), f"落子 {point} 超出棋盘范围"
        if self._grid.get(point) is not None:
            raise IllegalMoveError(f"位置 {point} 已被占据")
        assert self._grid.get(point) is None

        # 收集四邻信息
        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []

        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            neighbor_string = self._grid.get(neighbor)
            if neighbor_string is None:
                liberties.append(neighbor)
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)

        # 创建新棋串
        new_string = GoString(player, [point], liberties)

        # 合并同色邻串
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string

        # 更新 Zobrist 哈希
        self._hash ^= zobrist.HASH_CODE[point, player]

        # 处理异色邻串：减气或提子
        for other_color_string in adjacent_opposite_color:
            replacement = other_color_string.without_liberty(point)
            if replacement.num_liberties:
                self._replace_string(other_color_string.without_liberty(point))
            else:
                self._remove_string(other_color_string)

    def _replace_string(self, new_string):
        """更新棋盘上的棋串映射。"""
        for point in new_string.stones:
            self._grid[point] = new_string

    def _remove_string(self, string):
        """提走整串棋子，并为周围棋串增加气。"""
        for point in string.stones:
            for neighbor in point.neighbors():
                neighbor_string = self._grid.get(neighbor)
                if neighbor_string is None:
                    continue
                if neighbor_string is not string:
                    self._replace_string(neighbor_string.with_liberty(point))
            #修改 直接去除该点?
            self._grid[point] = None
            # self._grid.remove(point)
            # 撤销该子的哈希值
            self._hash ^= zobrist.HASH_CODE[point, string.color]

    def is_on_grid(self, point):
        """检查坐标是否在棋盘范围内。"""
        return (
            1 <= point.row <= self.num_rows and 1 <= point.col <= self.num_cols
        )

    def get(self, point):
        """
        获取指定位置的棋子颜色。

        Returns:
            Player 或 None（空点）
        """
        string = self._grid.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point):
        """
        获取指定位置的完整棋串。

        Returns:
            GoString 或 None（空点）
        """
        string = self._grid.get(point)
        if string is None:
            return None
        return string

    def __eq__(self, other):
        return (
            isinstance(other, Board)
            and self.num_rows == other.num_rows
            and self.num_cols == other.num_cols
            and self.zobrist_hash() == other.zobrist_hash()
        )

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        copied = Board(self.num_rows, self.num_cols)
        copied._grid = copy.copy(self._grid)
        copied._hash = self._hash
        return copied

    def zobrist_hash(self):
        """返回当前局面的 Zobrist 哈希值。"""
        return self._hash

class Move:
    """
    棋步。

    三种类型：落子、停一手、认输。
    只能使用类方法创建。
    """

    def __init__(self, point=None, is_pass=False, is_resign=False):
        assert (
            point is not None
        ) ^ is_pass ^ is_resign, "只能指定一种棋步类型"
        self.point = point
        self.is_play = self.point is not None
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        """落子。"""
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        """停一手。"""
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        """认输。"""
        return Move(is_resign=True)

    def __str__(self):
        if self.is_pass:
            return "pass"
        if self.is_resign:
            return "resign"
        return f"(r {self.point.row}, c {self.point.col})"


class GameState:
    """
    游戏状态。

    采用不可变设计，每次落子返回新状态。
    使用状态链实现劫判定（检测重复局面）。

    Attributes:
        board: 当前棋盘
        next_player: 下一手玩家
        previous_state: 上一状态（形成链表）
        previous_states: 历史局面集合（用于劫判定）
        last_move: 上一步棋
    """

    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        if self.previous_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                previous.previous_states
                | {(previous.next_player, previous.board.zobrist_hash())}
            )
        self.last_move = move

    def apply_move(self, move):
        """
        应用棋步，返回新状态。

        Args:
            move: 要应用的棋步

        Returns:
            新的 GameState
        """
        if move.is_play:
            next_board = copy.deepcopy(self.board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.board
        return GameState(
            next_board, self.next_player.other, self, move
        )
    def num_remove_stone(self,move,player=None):
        """移除"""
        if player is None:
            player=self.next_player.other
        if not move.is_play:
            return 0
        if self.board.get(move.point) is not None:
            return 0
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(self.next_player, move.point)
        
        stone_list=[key for key,value in self.board._grid.items() if value is not None and value.color==player]
        stone_num=len(stone_list)
        stone_list_aft=[key for key,value in next_board._grid.items() if value is not None and value.color==player]
        stone_num_aft=len(stone_list_aft)
        return stone_num-stone_num_aft

    @classmethod
    def new_game(cls, board_size):
        """
        创建新对局。

        Args:
            board_size: 棋盘大小（int 或 (rows, cols) 元组）

        Returns:
            初始 GameState
        """
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_move_self_capture(self, player, move):
        """检查是否自杀（落子后无气）。"""
        
        if not move.is_play:
            return False
        if self.board.get(move.point) is not None:
            return True
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0

    @property
    def situation(self):
        """当前局面（下一手玩家 + 棋盘）。"""
        return (self.next_player, self.board)

    def does_move_violate_ko(self, player, move):
        """检查是否违反劫规则。"""
        if not move.is_play:
            return False
        if self.board.get(move.point) is not None:
            return True
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        return next_situation in self.previous_states

    def is_valid_move(self, move):
        """检查棋步是否合法。"""
        #加一条 不能只紧自己的气 否则就是在自杀
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        if self.board.get(move.point) is not None:
            return False
        return (
            not self.is_move_self_capture(self.next_player, move)
            and not self.does_move_violate_ko(self.next_player, move)
            # and not self.is_move_self_decrease(self.next_player, move)
        )
    def is_move_self_decrease(self, player, move):
        """检查是否只减少自己的气。"""
        if self.board.get(move.point) is not None:
            return True
        liberty_bef={Player.black:0,Player.white:0}
        liberty_bef[player]=self.get_all_liberties_num(self.board,player)
        liberty_bef[player.other]=self.get_all_liberties_num(self.board,player.other)
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        liberty_aft={Player.black:0,Player.white:0}
        liberty_aft[player]=self.get_all_liberties_num(next_board,player)
        liberty_aft[player.other]=self.get_all_liberties_num(next_board,player.other)
        #得到value for key,value in next_board._grid.items() 但是要去重 value是unhashable的
        #not （自己的减少 且敌人的不变）
        return  (liberty_bef[player] >= liberty_aft[player]) and  (liberty_aft[player.other] == liberty_bef[player.other])
    


    def is_over(self):
        """检查对局是否结束。"""
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def legal_moves(self):
        """返回所有合法棋步。"""
        moves = []
        for row in range(1, self.board.num_rows + 1):
            for col in range(1, self.board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        moves.append(Move.pass_turn())
        moves.append(Move.resign())
        return moves

    def winner(self):
        """返回赢家（如果已结束）。"""
        if not self.is_over():
            return None
        if self.last_move.is_resign:
            return self.next_player
        game_result = compute_game_result(self)
        return game_result.winner
    def get_all_liberties_num(self, board, player):
        """总气数（去重统计）"""
        unique_liberties = set()
        
        # 首先收集所有唯一的go_string（用id作为键）
        unique_strings = {}
        for _, go_string in board._grid.items():
            if go_string is not None and go_string.color == player:
                unique_strings[id(go_string)] = go_string
        
        # 收集所有气并去重
        for go_string in unique_strings.values():
            # Point是namedtuple，hashable，可以直接加入set
            unique_liberties.update(go_string.liberties)
        
        return len(unique_liberties)         
    

    def delta_liberty_num(self,this_player):
        """气数变化。"""
        liberty_bef = self.get_all_liberties_num(self.board,this_player)#子节点的颜色
        liberty_other_bef=self.get_all_liberties_num(self.board,this_player.other)#子节点对手颜色
        
        # liberty_after = new_game_state.get_all_liberties_num(new_game_state.board,self.next_player)
        # liberty_other_after=new_game_state.get_all_liberties_num(new_game_state.board,self.next_player.other)
        # print(liberty_bef,liberty_other_bef)
        return liberty_bef-liberty_other_bef#
        # print(node.game_state.last_move.point,"this ",liberty_bef,liberty_after,"other",liberty_other_bef,liberty_other_after)

    def if_connect(self, player, move):
        """检查是否连接（返回棋串减少的数量）。"""
        if move.point is None:
            return 0
        if self.board.get(move.point) is not None:
            return 0
        
        # 收集落子前的唯一棋串
        unique_bef = {}
        for _, go_string in self.board._grid.items():
            if go_string is not None and go_string.color == player:
                unique_bef[id(go_string)] = go_string
        
        if len(unique_bef) == 0:  # 如果就没有自己的子 谈不上连接
            return 0
        
        next_board = copy.deepcopy(self.board)
        next_board.place_stone(player, move.point)
        
        # 收集落子后的唯一棋串
        unique_aft = {}
        for _, go_string in next_board._grid.items():
            if go_string is not None and go_string.color == player:
                unique_aft[id(go_string)] = go_string
        
        return len(unique_bef) - len(unique_aft)