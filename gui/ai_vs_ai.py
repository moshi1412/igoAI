import pygame
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dlgo import GameState, Player, Point
from dlgo.goboard import Move
from play import AGENTS


class AIVsAIGameGUI:
    def __init__(self, board_size=5, ai1="random", ai2="random", strategy='random', num_rounds=100, minimax_strategy='minmax', max_depth=3):
        pygame.init()
        self.board_size = board_size
        self.grid_size = 80
        self.margin = 80
        self.board_height = self.margin * 2 + self.grid_size * (board_size - 1)
        self.history_height = 150
        self.window_width = self.board_height
        self.window_height = self.board_height + self.history_height
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(f"iGo AI vs AI - {board_size}x{board_size}")
        
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
        self.move_history = []
        self.should_return_to_menu = False
        
        from play import get_agent
        self.ai1_agent = get_agent(ai1, strategy=strategy, num_rounds=num_rounds, minimax_strategy=minimax_strategy, max_depth=max_depth)
        self.ai2_agent = get_agent(ai2, strategy=strategy, num_rounds=num_rounds, minimax_strategy=minimax_strategy, max_depth=max_depth)
        
        self.ai1_type = ai1
        self.ai2_type = ai2
        self.paused = False
        self.restart_requested = False
        self.ai_thinking = False
        self.font = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 16)
        
        self.back_button_rect = pygame.Rect(10, 10, 100, 35)
    
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
    
    def ai_move(self):
        if not self.game_over and not self.paused:
            self.ai_thinking = True
            self.draw_status()
            self.draw_history()
            pygame.display.flip()
            
            time.sleep(0.3)
            
            if self.game.next_player == Player.black:
                move = self.ai1_agent(self.game)
            else:
                move = self.ai2_agent(self.game)
                
            move_num = len(self.move_history) + 1
            self.move_history.append((move_num, self.game.next_player, self.get_move_text(move)))
            self.game = self.game.apply_move(move)
            
            if self.game.is_over():
                self.game_over = True
            self.ai_thinking = False
    
    def draw_status(self):
        ai1_label = self.font.render(f"AI 1 (Black): {self.ai1_type}", True, (0, 0, 0))
        ai2_label = self.font.render(f"AI 2 (White): {self.ai2_type}", True, (0, 0, 0))
        self.screen.blit(ai1_label, (10, 10))
        self.screen.blit(ai2_label, (10, 30))
        
        if self.game_over:
            winner = self.game.winner()
            if winner:
                text = f"Game Over! Winner: {winner.name}"
            else:
                text = "Game Over! Draw"
        elif self.paused:
            text = "Paused - Press SPACE to continue"
        elif self.ai_thinking:
            text = f"AI thinking - {self.game.next_player.name}"
        else:
            text = f"Current: {self.game.next_player.name} - Press SPACE to pause"
        
        text_surface = self.font_large.render(text, True, self.colors['line'])
        text_rect = text_surface.get_rect(center=(self.window_width // 2, 20))
        pygame.draw.rect(self.screen, self.colors['bg'], text_rect)
        self.screen.blit(text_surface, text_rect)
        
        if self.game_over:
            restart_text = self.font_large.render("Click anywhere to restart", True, self.colors['line'])
            restart_rect = restart_text.get_rect(center=(self.window_width // 2, self.board_height - 20))
            pygame.draw.rect(self.screen, self.colors['bg'], restart_rect)
            self.screen.blit(restart_text, restart_rect)
    
    def draw_back_button(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.back_button_rect.collidepoint(mouse_pos)
        
        color = (100, 150, 100) if is_hover else (80, 120, 80)
        pygame.draw.rect(self.screen, color, self.back_button_rect, border_radius=5)
        
        text = self.font_small.render("Back", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(text, text_rect)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button_rect.collidepoint(event.pos):
                    self.should_return_to_menu = True
                    self.running = False
                    return
                if self.game_over:
                    self.game = GameState.new_game(self.board_size)
                    self.game_over = False
                    self.paused = False
                    self.move_history = []
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            
            if not self.game_over and not self.paused:
                self.ai_move()
            
            self.draw_board()
            self.draw_back_button()
            self.draw_status()
            self.draw_history()
            pygame.display.flip()
            clock.tick(30)
        
        pygame.display.quit()
        return self.should_return_to_menu


def main():
    import argparse
    parser = argparse.ArgumentParser(description="iGo AI vs AI GUI")
    parser.add_argument("--size", type=int, default=5, help="Board size (default 5)")
    parser.add_argument("--ai1", choices=["random", "mcts", "minimax"], default="random", help="AI 1 (default random)")
    parser.add_argument("--ai2", choices=["random", "mcts", "minimax"], default="random", help="AI 2 (default random)")
    args = parser.parse_args()
    
    gui = AIVsAIGameGUI(
        board_size=args.size,
        ai1=args.ai1,
        ai2=args.ai2
    )
    gui.run()


if __name__ == "__main__":
    main()
