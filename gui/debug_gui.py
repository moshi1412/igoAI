import pygame
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dlgo import GameState, Player, Point
from dlgo.goboard import Move
from play import AGENTS, random_agent, minimax_agent
from agents.mcts_agent import MCTSAgent


class TreeNodeWrapper:
    def __init__(self, node, move_info=""):
        self.node = node
        self.expanded = False
        self.move_info = move_info
        self.children = []


class DebugGoGameGUI:
    def __init__(self, board_size=5, ai_agent="mcts", human_first=True, strategy='random', max_depth=3):
        pygame.init()
        self.board_size = board_size
        
        self.grid_size = 80
        self.margin = 80
        self.board_height = self.margin * 2 + self.grid_size * (board_size - 1)
        self.history_height = 150
        self.error_height = 80
        
        self.tree_window_size = 900
        self.total_width = self.board_height + self.tree_window_size
        self.total_height = max(self.board_height + self.history_height + self.error_height, 930)
        
        self.screen = pygame.display.set_mode((self.total_width, self.total_height))
        pygame.display.set_caption(f"iGo Debug Mode - {board_size}x{board_size}")
        
        self.colors = {
            'board_bg': (220, 179, 92),
            'tree_bg': (240, 240, 240),
            'line': (0, 0, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'node': (100, 150, 200),
            'node_border': (50, 100, 150),
            'root_node': (200, 100, 100),
            'root_border': (150, 50, 50),
            'collapsed_node': (150, 150, 150),
            'hover_node': (120, 180, 220),
            'best_node': (80, 200, 80),
            'best_node_border': (50, 150, 50),
        }
        
        self.game = GameState.new_game(board_size)
        self.running = True
        self.game_over = False
        self.ai_thinking = False
        self.should_return_to_menu = False
        self.ai_agent_name = ai_agent
        self.human_player = Player.black if human_first else Player.white
        self.ai_player = Player.white if human_first else Player.black
        self.has_error = False
        self.error_message = ""
        self.has_warning = False
        self.warning_message = ""
        self.warning_start_time = 0
        self.font = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 14)
        
        self.back_button_rect = pygame.Rect(10, 10, 100, 35)
        self.pass_button_rect = pygame.Rect(self.board_height - 180, 10, 80, 35)
        self.resign_button_rect = pygame.Rect(self.board_height - 90, 10, 80, 35)
        
        if ai_agent == 'mcts':
            self.mcts_agent_instance = MCTSAgent(num_rounds=100, strategy=strategy)
            self.ai_agent = lambda gs: self.mcts_agent_instance.select_move(gs)
        elif ai_agent == 'minimax':
            from play import get_agent
            self.ai_agent = get_agent(ai_agent, strategy=strategy, num_rounds=100, minimax_strategy='minmax', max_depth=max_depth)
        else:
            self.ai_agent = random_agent
        
        self.mcts_root = None
        self.tree_wrappers = {}
        self.scroll_offset = [0, 0]
        self.scale = 1.0
        self.dragging = False
        self.last_mouse_pos = None
        self.hovered_node = None
        self.node_positions = {}
        self.selected_move_node = None
        self.move_history = []
        
        self.draw()
        pygame.display.flip()
        pygame.event.pump()
        
    def draw_board(self, surface):
        temp_surface = pygame.Surface((self.board_height, self.board_height))
        temp_surface.fill(self.colors['board_bg'])
        
        for i in range(self.board_size):
            start_pos = (self.margin, self.margin + i * self.grid_size)
            end_pos = (self.board_height - self.margin, self.margin + i * self.grid_size)
            pygame.draw.line(temp_surface, self.colors['line'], start_pos, end_pos, 2)
            
            start_pos = (self.margin + i * self.grid_size, self.margin)
            end_pos = (self.margin + i * self.grid_size, self.board_height - self.margin)
            pygame.draw.line(temp_surface, self.colors['line'], start_pos, end_pos, 2)
        
        self.draw_coordinates(temp_surface)
        
        if self.game.next_player == self.human_player and not self.ai_thinking and not self.game_over:
            legal_moves = self.game.legal_moves()
            for move in legal_moves:
                if move.is_pass or not hasattr(move, 'point') or move.point is None:
                    continue
                point = move.point
                x = self.margin + (point.col - 1) * self.grid_size
                y = self.margin + (point.row - 1) * self.grid_size
                pygame.draw.circle(temp_surface, (100, 200, 100), (x, y), 8)
        
        self.draw_stones(temp_surface)
        
        surface.blit(temp_surface, (0, 0))
        
        self.draw_history(surface)
    
    def draw_history(self, surface):
        history_rect = pygame.Rect(0, self.board_height, self.board_height, self.history_height)
        pygame.draw.rect(surface, (240, 240, 240), history_rect)
        
        header = self.font_small.render("Move History:", True, (0, 0, 0))
        surface.blit(header, (10, self.board_height + 10))
        
        max_display = 6
        start_y = self.board_height + 35
        line_height = 18
        
        start_idx = max(0, len(self.move_history) - max_display)
        for i in range(start_idx, len(self.move_history)):
            move_idx, player, move_text = self.move_history[i]
            player_color = (0, 0, 0) if player == Player.black else (100, 100, 100)
            player_bg = (220, 220, 220) if player == Player.black else (255, 255, 255)
            
            history_text = f"#{move_idx}: {player.name} - {move_text}"
            text_surface = self.font_small.render(history_text, True, player_color)
            text_rect = text_surface.get_rect(topleft=(15, start_y))
            pygame.draw.rect(surface, player_bg, text_rect.inflate(4, 0))
            surface.blit(text_surface, text_rect)
            start_y += line_height
        
        if start_idx > 0:
            more_text = f"... {start_idx} earlier moves hidden"
            more_surface = self.font_small.render(more_text, True, (100, 100, 100))
            surface.blit(more_surface, (15, start_y))
    
    def draw_coordinates(self, surface):
        for i in range(self.board_size):
            col_text = str(i + 1)
            text_surface = self.font.render(col_text, True, self.colors['line'])
            x = self.margin + i * self.grid_size
            y = self.margin // 2
            text_rect = text_surface.get_rect(center=(x, y))
            surface.blit(text_surface, text_rect)
            
            row_text = str(i + 1)
            text_surface = self.font.render(row_text, True, self.colors['line'])
            x = self.margin // 2
            y = self.margin + i * self.grid_size
            text_rect = text_surface.get_rect(center=(x, y))
            surface.blit(text_surface, text_rect)
        
    def draw_stones(self, surface):
        for row in range(1, self.board_size + 1):
            for col in range(1, self.board_size + 1):
                point = Point(row, col)
                stone = self.game.board.get(point)
                if stone:
                    x = self.margin + (col - 1) * self.grid_size
                    y = self.margin + (row - 1) * self.grid_size
                    color = self.colors['black'] if stone == Player.black else self.colors['white']
                    pygame.draw.circle(surface, color, (x, y), self.grid_size // 2 - 3)
                    pygame.draw.circle(surface, self.colors['line'], (x, y), self.grid_size // 2 - 3, 1)
    
    def get_board_pos(self, screen_pos):
        x, y = screen_pos
        if x > self.board_height or y > self.board_height:
            return None
        
        col_float = (x - self.margin) / self.grid_size
        row_float = (y - self.margin) / self.grid_size
        col = int(round(col_float)) + 1
        row = int(round(row_float)) + 1
        
        if 1 <= row <= self.board_size and 1 <= col <= self.board_size:
            return Point(row, col)
        return None
    
    def get_move_info(self, node):
        if hasattr(node, 'game_state') and node.game_state.last_move:
            move = node.game_state.last_move
            if move.is_pass:
                return "Pass"
            elif hasattr(move, 'is_resign') and move.is_resign:
                return "Resign"
            elif hasattr(move, 'point') and move.point:
                return f"({move.point.col},{move.point.row})"
        return "Root"
    
    def get_move_text(self, move):
        if move.is_pass:
            return "Pass"
        elif hasattr(move, 'is_resign') and move.is_resign:
            return "Resign"
        elif hasattr(move, 'point') and move.point:
            return f"({move.point.row},{move.point.col})"
        return "?"
    
    def get_wrapper(self, node):
        if node not in self.tree_wrappers:
            move_info = self.get_move_info(node)
            self.tree_wrappers[node] = TreeNodeWrapper(node, move_info)
        return self.tree_wrappers[node]
    
    def find_best_child(self, root):
        if not root or len(root.children) == 0:
            return None
        
        return root.best_child()
    
    def draw_tree_node(self, surface, node, x, y, level, max_level, mouse_pos=None):
        radius = int((32 - level * 2) * self.scale)
        if radius < 15:
            radius = 15
        
        wrapper = self.get_wrapper(node)
        is_root = (node.parent is None)
        is_best = (node == self.selected_move_node)
        
        if mouse_pos and (x - radius) <= mouse_pos[0] <= (x + radius) and (y - radius) <= mouse_pos[1] <= (y + radius):
            self.hovered_node = node
            color = self.colors['hover_node']
        elif is_best:
            color = self.colors['best_node']
        else:
            if is_root:
                color = self.colors['root_node']
            elif not wrapper.expanded and len(node.children) > 0:
                color = self.colors['collapsed_node']
            else:
                color = self.colors['node']
        
        if is_best:
            border_color = self.colors['best_node_border']
        elif is_root:
            border_color = self.colors['root_border']
        else:
            border_color = self.colors['node_border']
        
        self.node_positions[node] = (x, y, radius)
        
        pygame.draw.circle(surface, color, (x, y), radius)
        pygame.draw.circle(surface, border_color, (x, y), radius, 2)
        
        if len(node.children) > 0:
            if wrapper.expanded:
                collapse_text = "-"
            else:
                collapse_text = "+"
            collapse_surface = self.font.render(collapse_text, True, (255, 255, 255))
            collapse_rect = collapse_surface.get_rect(center=(x, y - radius + 10))
            surface.blit(collapse_surface, collapse_rect)
        
        value_text = f"{node.value_sum:.2f}"
        visit_text = f"{node.visit_count}"
        move_text = wrapper.move_info
        
        font_size = max(10, int(14 * self.scale))
        font = pygame.font.Font(None, font_size)
        
        value_surface = font.render(value_text, True, (255, 255, 255))
        visit_surface = font.render(visit_text, True, (255, 255, 255))
        move_surface = font.render(move_text, True, (255, 255, 255))
        
        value_rect = value_surface.get_rect(center=(x, y - 8))
        visit_rect = visit_surface.get_rect(center=(x, y + 2))
        move_rect = move_surface.get_rect(center=(x, y + 12))
        
        surface.blit(value_surface, value_rect)
        surface.blit(visit_surface, visit_rect)
        if move_text != "Root" or is_root:
            surface.blit(move_surface, move_rect)
        
        if wrapper.expanded or is_root:
            x_offset = int(110 * self.scale)
            y_offset = int(85 * self.scale)
            child_count = len(node.children)
            for i, child in enumerate(node.children):
                child_x = x + x_offset
                child_y = y - (child_count - 1) * y_offset / 2 + i * y_offset
                
                pygame.draw.line(surface, (150, 150, 150), (x + radius, y), (child_x - radius, child_y), 1)
                
                if level < max_level:
                    self.draw_tree_node(surface, child, child_x, child_y, level + 1, max_level, mouse_pos)
    
    def draw_mcts_tree(self, surface, mouse_pos):
        surface.fill(self.colors['tree_bg'])
        
        title = self.font_large.render("MCTS Tree", True, (0, 0, 0))
        surface.blit(title, (10, 10))
        
        scale_text = self.font_small.render(f"Scale: {self.scale:.1f}x", True, (80, 80, 80))
        surface.blit(scale_text, (10, 60))
        
        tree_mouse_pos = None
        if mouse_pos and mouse_pos[0] > self.board_height:
            tree_mouse_pos = ((mouse_pos[0] - self.board_height - self.scroll_offset[0]) / self.scale, 
                              (mouse_pos[1] - self.scroll_offset[1]) / self.scale)
        
        self.hovered_node = None
        self.node_positions = {}
        
        if self.mcts_root:
            root_x = int(70 * self.scale)
            root_y = self.total_height // 2
            
            offset_x = self.scroll_offset[0]
            offset_y = self.scroll_offset[1]
            
            temp_surface = pygame.Surface((self.tree_window_size, self.total_height))
            temp_surface.fill(self.colors['tree_bg'])
            
            self.draw_tree_node(temp_surface, self.mcts_root, root_x + offset_x, root_y + offset_y, 0, 2, tree_mouse_pos)
            
            surface.blit(temp_surface, (0, 0))
            
            info_text = f"Root visits: {self.mcts_root.visit_count}, Children: {len(self.mcts_root.children)}"
            info_surface = self.font_small.render(info_text, True, (0, 0, 0))
            surface.blit(info_surface, (10, 40))
            
            hint1 = self.font_small.render("Click nodes to expand/collapse", True, (80, 80, 80))
            hint2 = self.font_small.render("Drag to scroll, Scroll to zoom", True, (80, 80, 80))
            surface.blit(hint1, (10, self.total_height - 45))
            surface.blit(hint2, (10, self.total_height - 25))
        else:
            hint = self.font.render("Wait for AI to move to see tree", True, (100, 100, 100))
            hint_rect = hint.get_rect(center=(self.tree_window_size // 2, self.total_height // 2))
            surface.blit(hint, hint_rect)
    
    def draw_move_history(self, surface):
        start_y = 90
        line_height = 18
        
        header = self.font_small.render("Move History:", True, (0, 0, 0))
        surface.blit(header, (10, start_y))
        
        start_y += 22
        max_display = 15
        
        for i in range(min(len(self.move_history), max_display)):
            move_idx, player, move_text = self.move_history[-(i+1)]
            player_color = (0, 0, 0) if player == Player.black else (200, 200, 200)
            player_bg = (220, 220, 220) if player == Player.black else (255, 255, 255)
            
            history_text = f"#{move_idx}: {player.name} - {move_text}"
            text_surface = self.font_small.render(history_text, True, player_color)
            text_rect = text_surface.get_rect(topleft=(15, start_y))
            pygame.draw.rect(surface, player_bg, text_rect.inflate(4, 0))
            surface.blit(text_surface, text_rect)
            start_y += line_height
        
        if len(self.move_history) > max_display:
            more_text = f"... and {len(self.move_history) - max_display} more"
            more_surface = self.font_small.render(more_text, True, (100, 100, 100))
            surface.blit(more_surface, (15, start_y))
    
    def handle_click(self, pos):
        if self.game_over:
            self.game = GameState.new_game(self.board_size)
            self.game_over = False
            self.mcts_root = None
            self.tree_wrappers = {}
            self.selected_move_node = None
            self.move_history = []
            self.has_error = False
            self.error_message = ""
            self.has_warning = False
            self.warning_message = ""
            return
            
        if self.ai_thinking or self.has_error:
            return
            
        if self.game.next_player != self.human_player:
            return
            
        point = self.get_board_pos(pos)
        if point:
            move = Move(point)
            if not self.game.is_valid_move(move):
                if self.game.board.get(point) is not None:
                    self.has_warning = True
                    self.warning_message = "Position already occupied! Please try again."
                else:
                    self.has_warning = True
                    self.warning_message = "Invalid move! Please try again."
                self.warning_start_time = time.time()
                return
            try:
                move_num = len(self.move_history) + 1
                self.move_history.append((move_num, self.game.next_player, self.get_move_text(move)))
                self.game = self.game.apply_move(move)
                if self.game.is_over():
                    self.game_over = True
            except Exception as e:
                self.has_error = True
                self.error_message = f"Move Error: {str(e)[:100]}"
                print(f"Move Error: {e}")
    
    def handle_tree_click(self, pos):
        tree_x = (pos[0] - self.board_height - self.scroll_offset[0]) / self.scale
        tree_y = (pos[1] - self.scroll_offset[1]) / self.scale
        
        for node, (x, y, radius) in self.node_positions.items():
            if (tree_x - x) ** 2 + (tree_y - y) ** 2 <= radius ** 2:
                wrapper = self.get_wrapper(node)
                if len(node.children) > 0:
                    wrapper.expanded = not wrapper.expanded
                return True
        return False
    
    def ai_move(self):
        if self.game.next_player == self.ai_player and not self.game_over and not self.has_error:
            try:
                self.ai_thinking = True
                
                for _ in range(3):
                    self.draw()
                    pygame.display.flip()
                    pygame.event.pump()
                    pygame.time.wait(50)
                
                move = self.ai_agent(self.game)
                
                if self.ai_agent_name == 'mcts' and hasattr(self, 'mcts_agent_instance'):
                    self.mcts_root = self.mcts_agent_instance.last_root
                    self.selected_move_node = self.find_best_child(self.mcts_root)
                
                move_num = len(self.move_history) + 1
                self.move_history.append((move_num, self.game.next_player, self.get_move_text(move)))
                self.game = self.game.apply_move(move)
                
                if self.game.is_over():
                    self.game_over = True
                self.ai_thinking = False
            except Exception as e:
                self.has_error = True
                self.error_message = f"AI Error: {str(e)[:100]}"
                self.ai_thinking = False
                print(f"AI Error: {e}")
    
    def draw_status(self, board_surface):
        if self.game_over:
            winner = self.game.winner()
            if winner:
                text = f"Game Over! Winner: {winner.name}"
            else:
                text = "Game Over! Draw"
        elif self.ai_thinking:
            text = "AI thinking..."
        elif self.game.next_player == self.human_player:
            text = f"Your turn ({self.human_player.name}) - Click to place!"
        else:
            text = f"AI turn ({self.ai_player.name})"
        
        text_surface = self.font_large.render(text, True, self.colors['line'])
        text_rect = text_surface.get_rect(center=(self.board_height // 2, 25))
        pygame.draw.rect(board_surface, self.colors['board_bg'], text_rect)
        board_surface.blit(text_surface, text_rect)
        
        if self.game_over:
            restart_text = self.font_large.render("Click anywhere to restart", True, self.colors['line'])
            restart_rect = restart_text.get_rect(center=(self.board_height // 2, self.board_height - 25))
            pygame.draw.rect(board_surface, self.colors['board_bg'], restart_rect)
            board_surface.blit(restart_text, restart_rect)
    
    def draw_back_button(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.back_button_rect.collidepoint(mouse_pos)
        
        color = (100, 150, 100) if is_hover else (80, 120, 80)
        pygame.draw.rect(self.screen, color, self.back_button_rect, border_radius=5)
        
        text = self.font_small.render("Back", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_pass_button(self):
        if self.game_over or self.ai_thinking or self.game.next_player != self.human_player:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.pass_button_rect.collidepoint(mouse_pos)
        
        color = (70, 130, 180) if is_hover else (50, 110, 160)
        pygame.draw.rect(self.screen, color, self.pass_button_rect, border_radius=5)
        
        text = self.font_small.render("Pass", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.pass_button_rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_resign_button(self):
        if self.game_over or self.ai_thinking or self.game.next_player != self.human_player:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.resign_button_rect.collidepoint(mouse_pos)
        
        color = (180, 80, 80) if is_hover else (160, 60, 60)
        pygame.draw.rect(self.screen, color, self.resign_button_rect, border_radius=5)
        
        text = self.font_small.render("Resign", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.resign_button_rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_error_message(self, board_surface):
        if not self.has_error:
            return
        
        error_rect = pygame.Rect(0, self.board_height + self.history_height, self.board_height, self.error_height)
        pygame.draw.rect(board_surface, (255, 200, 200), error_rect)
        pygame.draw.rect(board_surface, (200, 50, 50), error_rect, 2)
        
        header = self.font_large.render("Error occurred!", True, (150, 0, 0))
        header_rect = header.get_rect(center=(self.board_height // 2, self.board_height + self.history_height + 25))
        board_surface.blit(header, header_rect)
        
        message = self.font_small.render(self.error_message, True, (100, 0, 0))
        message_rect = message.get_rect(center=(self.board_height // 2, self.board_height + self.history_height + 55))
        board_surface.blit(message, message_rect)
    
    def draw_warning_message(self, board_surface):
        if not self.has_warning:
            return
        
        current_time = time.time()
        if current_time - self.warning_start_time > 2.0:
            self.has_warning = False
            self.warning_message = ""
            return
        
        warning_rect = pygame.Rect(0, self.board_height // 2 - 30, self.board_height, 60)
        pygame.draw.rect(board_surface, (255, 255, 200), warning_rect)
        pygame.draw.rect(board_surface, (200, 150, 0), warning_rect, 3)
        
        warning_text = self.font_large.render(self.warning_message, True, (150, 100, 0))
        warning_rect_text = warning_text.get_rect(center=(self.board_height // 2, self.board_height // 2))
        board_surface.blit(warning_text, warning_rect_text)
    
    def draw(self, mouse_pos=None):
        board_surface = pygame.Surface((self.board_height, self.total_height))
        tree_surface = pygame.Surface((self.tree_window_size, self.total_height))
        
        self.draw_board(board_surface)
        self.draw_status(board_surface)
        self.draw_error_message(board_surface)
        self.draw_warning_message(board_surface)
        self.draw_mcts_tree(tree_surface, mouse_pos)
        
        self.screen.blit(board_surface, (0, 0))
        self.screen.blit(tree_surface, (self.board_height, 0))
        
        pygame.draw.line(self.screen, (0, 0, 0), (self.board_height, 0), (self.board_height, self.total_height), 2)
        self.draw_back_button()
        self.draw_pass_button()
        self.draw_resign_button()
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = event.pos
                    if self.back_button_rect.collidepoint(pos):
                        self.should_return_to_menu = True
                        self.running = False
                        return mouse_pos
                    if self.pass_button_rect.collidepoint(pos) and not self.game_over and not self.ai_thinking and self.game.next_player == self.human_player and not self.has_error:
                        try:
                            move = Move.pass_turn()
                            move_num = len(self.move_history) + 1
                            self.move_history.append((move_num, self.game.next_player, self.get_move_text(move)))
                            self.game = self.game.apply_move(move)
                            if self.game.is_over():
                                self.game_over = True
                        except Exception as e:
                            self.has_error = True
                            self.error_message = f"Pass Error: {str(e)[:100]}"
                            print(f"Pass Error: {e}")
                        return mouse_pos
                    if self.resign_button_rect.collidepoint(pos) and not self.game_over and not self.ai_thinking and self.game.next_player == self.human_player and not self.has_error:
                        try:
                            move = Move.resign()
                            move_num = len(self.move_history) + 1
                            self.move_history.append((move_num, self.game.next_player, self.get_move_text(move)))
                            self.game = self.game.apply_move(move)
                            self.game_over = True
                        except Exception as e:
                            self.has_error = True
                            self.error_message = f"Resign Error: {str(e)[:100]}"
                            print(f"Resign Error: {e}")
                        return mouse_pos
                    if pos[0] > self.board_height:
                        if not self.handle_tree_click(pos):
                            self.dragging = True
                            self.last_mouse_pos = pos
                    else:
                        self.handle_click(pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
                    self.last_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.last_mouse_pos:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.scroll_offset[0] += dx
                    self.scroll_offset[1] += dy
                    self.last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEWHEEL:
                if mouse_pos[0] > self.board_height:
                    old_scale = self.scale
                    if event.y > 0:
                        self.scale = min(2.0, self.scale * 1.1)
                    else:
                        self.scale = max(0.5, self.scale / 1.1)
                    scale_change = self.scale / old_scale
                    mouse_tree_x = (mouse_pos[0] - self.board_height - self.scroll_offset[0])
                    mouse_tree_y = (mouse_pos[1] - self.scroll_offset[1])
                    self.scroll_offset[0] = mouse_pos[0] - self.board_height - mouse_tree_x * scale_change
                    self.scroll_offset[1] = mouse_pos[1] - mouse_tree_y * scale_change
        
        return mouse_pos
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            mouse_pos = self.handle_events()
            
            if not self.game_over and self.game.next_player == self.ai_player and not self.ai_thinking:
                self.ai_move()
            
            self.draw(mouse_pos)
            pygame.display.flip()
            clock.tick(30)
        
        pygame.display.quit()
        return self.should_return_to_menu


def main():
    import argparse
    parser = argparse.ArgumentParser(description="iGo Debug GUI with MCTS Tree")
    parser.add_argument("--size", type=int, default=5, help="Board size (default 5)")
    parser.add_argument("--ai", choices=["mcts", "minimax", "random"], default="mcts", help="AI agent")
    parser.add_argument("--ai_first", action="store_true", help="AI first (default human first)")
    parser.add_argument("--strategy", choices=["random", "remove_first", "liberty_first"], default="random", help="MCTS strategy (default random)")
    parser.add_argument("--max_depth", type=int, default=3, help="Minimax max depth (default 3)")
    args = parser.parse_args()
    
    gui = DebugGoGameGUI(
        board_size=args.size,
        ai_agent=args.ai,
        human_first=not args.ai_first,
        strategy=args.strategy,
        max_depth=args.max_depth
    )
    gui.run()


if __name__ == "__main__":
    main()
