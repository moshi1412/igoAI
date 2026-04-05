import pygame
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dlgo import GameState, Player, Point
from dlgo.goboard import Move
from play import AGENTS


class AIGoGameGUI:
    def __init__(self, board_size=5, ai_agent="random", human_first=True, strategy='random', num_rounds=100, minimax_strategy='minmax', max_depth=3):
        pygame.init()
        self.board_size = board_size
        self.grid_size = 80
        self.margin = 80
        self.board_height = self.margin * 2 + self.grid_size * (board_size - 1)
        self.history_height = 150
        self.error_height = 80
        self.window_width = self.board_height
        self.window_height = self.board_height + self.history_height + self.error_height
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(f"iGo - {board_size}x{board_size}")
        
        self.colors = {
            'bg': (220, 179, 92),
            'history_bg': (240, 240, 240),
            'line': (0, 0, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }
        
        self.game = GameState.new_game(board_size)
        self.running = True
        self.game_over = False
        self.ai_thinking = False
        self.move_history = []
        self.should_return_to_menu = False
        self.has_error = False
        self.error_message = ""
        self.has_warning = False
        self.warning_message = ""
        self.warning_start_time = 0
        
        from play import get_agent
        self.ai_agent = get_agent(ai_agent, strategy=strategy, num_rounds=num_rounds, minimax_strategy=minimax_strategy, max_depth=max_depth)
        
        self.human_player = Player.black if human_first else Player.white
        self.ai_player = Player.white if human_first else Player.black
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)
        
        self.back_button_rect = pygame.Rect(10, 10, 100, 35)
        self.pass_button_rect = pygame.Rect(self.window_width - 180, 10, 80, 35)
        self.resign_button_rect = pygame.Rect(self.window_width - 90, 10, 80, 35)
    
    def get_move_text(self, move):
        if move.is_pass:
            return "Pass"
        elif hasattr(move, 'is_resign') and move.is_resign:
            return "Resign"
        elif hasattr(move, 'point') and move.point:
            return f"({move.point.col},{move.point.row})"
        return "?"
    
    def draw_board(self):
        self.screen.fill(self.colors['bg'])
        
        for i in range(self.board_size):
            start_pos = (self.margin, self.margin + i * self.grid_size)
            end_pos = (self.window_width - self.margin, self.margin + i * self.grid_size)
            pygame.draw.line(self.screen, self.colors['line'], start_pos, end_pos, 2)
            
            start_pos = (self.margin + i * self.grid_size, self.margin)
            end_pos = (self.margin + i * self.grid_size, self.board_height - self.margin)
            pygame.draw.line(self.screen, self.colors['line'], start_pos, end_pos, 2)
        
        self.draw_coordinates()
        self.draw_stones()
    
    def draw_coordinates(self):
        for i in range(self.board_size):
            col_text = str(i + 1)
            text_surface = self.font.render(col_text, True, self.colors['line'])
            x = self.margin + i * self.grid_size
            y = self.margin // 2
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
            
            row_text = str(i + 1)
            text_surface = self.font.render(row_text, True, self.colors['line'])
            x = self.margin // 2
            y = self.margin + i * self.grid_size
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
    
    def draw_stones(self):
        for row in range(1, self.board_size + 1):
            for col in range(1, self.board_size + 1):
                point = Point(row, col)
                stone = self.game.board.get(point)
                if stone:
                    x = self.margin + (col - 1) * self.grid_size
                    y = self.margin + (row - 1) * self.grid_size
                    color = self.colors['black'] if stone == Player.black else self.colors['white']
                    pygame.draw.circle(self.screen, color, (x, y), self.grid_size // 2 - 3)
                    pygame.draw.circle(self.screen, self.colors['line'], (x, y), self.grid_size // 2 - 3, 1)
    
    def draw_history(self):
        history_rect = pygame.Rect(0, self.board_height, self.window_width, self.history_height)
        pygame.draw.rect(self.screen, self.colors['history_bg'], history_rect)
        
        header = self.font_small.render("Move History:", True, (0, 0, 0))
        self.screen.blit(header, (10, self.board_height + 10))
        
        max_display = 6
        start_y = self.board_height + 35
        line_height = 18
        
        # 只显示最近的max_display步
        start_idx = max(0, len(self.move_history) - max_display)
        for i in range(start_idx, len(self.move_history)):
            move_idx, player, move_text = self.move_history[i]
            player_color = (0, 0, 0) if player == Player.black else (100, 100, 100)
            player_bg = (220, 220, 220) if player == Player.black else (255, 255, 255)
            
            history_text = f"#{move_idx}: {player.name} - {move_text}"
            text_surface = self.font_small.render(history_text, True, player_color)
            text_rect = text_surface.get_rect(topleft=(15, start_y))
            pygame.draw.rect(self.screen, player_bg, text_rect.inflate(4, 0))
            self.screen.blit(text_surface, text_rect)
            start_y += line_height
        
        # 如果之前有隐藏的步数，显示提示
        if start_idx > 0:
            more_text = f"... {start_idx} earlier moves hidden"
            more_surface = self.font_small.render(more_text, True, (100, 100, 100))
            self.screen.blit(more_surface, (15, start_y))
    
    def get_board_pos(self, screen_pos):
        x, y = screen_pos
        if y > self.board_height:
            return None
        
        col = round((x - self.margin) / self.grid_size) + 1
        row = round((y - self.margin) / self.grid_size) + 1
        if 1 <= row <= self.board_size and 1 <= col <= self.board_size:
            return Point(row, col)
        return None
    
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
    
    def draw_error_message(self):
        if not self.has_error:
            return
        
        error_rect = pygame.Rect(0, self.board_height + self.history_height, self.window_width, self.error_height)
        pygame.draw.rect(self.screen, (255, 200, 200), error_rect)
        pygame.draw.rect(self.screen, (200, 50, 50), error_rect, 2)
        
        header = self.font.render("Error occurred!", True, (150, 0, 0))
        header_rect = header.get_rect(center=(self.window_width // 2, self.board_height + self.history_height + 20))
        self.screen.blit(header, header_rect)
        
        message = self.font_small.render(self.error_message, True, (100, 0, 0))
        message_rect = message.get_rect(center=(self.window_width // 2, self.board_height + self.history_height + 50))
        self.screen.blit(message, message_rect)
    
    def draw_warning_message(self):
        if not self.has_warning:
            return
        
        current_time = time.time()
        if current_time - self.warning_start_time > 2.0:
            self.has_warning = False
            self.warning_message = ""
            return
        
        warning_rect = pygame.Rect(0, self.board_height // 2 - 30, self.window_width, 60)
        pygame.draw.rect(self.screen, (255, 255, 200), warning_rect)
        pygame.draw.rect(self.screen, (200, 150, 0), warning_rect, 3)
        
        warning_text = self.font.render(self.warning_message, True, (150, 100, 0))
        warning_rect_text = warning_text.get_rect(center=(self.window_width // 2, self.board_height // 2))
        self.screen.blit(warning_text, warning_rect_text)
    
    def handle_click(self, pos):
        if self.back_button_rect.collidepoint(pos):
            self.should_return_to_menu = True
            self.running = False
            return
        
        if self.pass_button_rect.collidepoint(pos):
            if not self.game_over and not self.ai_thinking and self.game.next_player == self.human_player and not self.has_error:
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
            return
        
        if self.resign_button_rect.collidepoint(pos):
            if not self.game_over and not self.ai_thinking and self.game.next_player == self.human_player and not self.has_error:
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
            return
            
        if self.game_over:
            self.game = GameState.new_game(self.board_size)
            self.game_over = False
            self.move_history = []
            self.has_error = False
            self.error_message = ""
            self.has_warning = False
            self.warning_message = ""
            return
            
        if self.ai_thinking or self.game.next_player != self.human_player:
            return
            
        point = self.get_board_pos(pos)
        if point and not self.has_error:
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
    
    def ai_move(self):
        if self.game.next_player == self.ai_player and not self.game_over and not self.has_error:
            try:
                self.ai_thinking = True
                self.draw_status()
                self.draw_history()
                self.draw_error_message()
                pygame.display.flip()
                
                time.sleep(0.5)
                move = self.ai_agent(self.game)
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
    
    def draw_status(self):
        if self.game_over:
            winner = self.game.winner()
            if winner:
                text = f"Game Over! Winner: {winner.name}"
            else:
                text = "Game Over! Draw"
        elif self.ai_thinking:
            text = "AI thinking..."
        elif self.game.next_player == self.human_player:
            text = f"Your turn ({self.human_player.name})"
        else:
            text = f"AI turn ({self.ai_player.name})"
        
        text_surface = self.font.render(text, True, self.colors['line'])
        text_rect = text_surface.get_rect(center=(self.window_width // 2, 25))
        pygame.draw.rect(self.screen, self.colors['bg'], text_rect)
        self.screen.blit(text_surface, text_rect)
        
        if self.game_over:
            restart_text = self.font.render("Click anywhere to restart", True, self.colors['line'])
            restart_rect = restart_text.get_rect(center=(self.window_width // 2, self.board_height - 25))
            pygame.draw.rect(self.screen, self.colors['bg'], restart_rect)
            self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            if not self.game_over and self.game.next_player == self.ai_player and not self.ai_thinking:
                self.ai_move()
            
            self.draw_board()
            self.draw_back_button()
            self.draw_pass_button()
            self.draw_resign_button()
            self.draw_status()
            self.draw_history()
            self.draw_error_message()
            self.draw_warning_message()
            pygame.display.flip()
            clock.tick(30)
        
        pygame.display.quit()
        return self.should_return_to_menu


def main():
    import argparse
    parser = argparse.ArgumentParser(description="iGo AI GUI")
    parser.add_argument("--size", type=int, default=5, help="Board size (default 5)")
    parser.add_argument("--ai", choices=AGENTS.keys(), default="random", help="AI agent (default random)")
    parser.add_argument("--ai_first", action="store_true", help="AI first (default human first)")
    args = parser.parse_args()
    
    gui = AIGoGameGUI(
        board_size=args.size,
        ai_agent=args.ai,
        human_first=not args.ai_first
    )
    gui.run()


if __name__ == "__main__":
    main()
