import pygame
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dlgo import GameState, Player, Point
from dlgo.goboard import Move
from play import AGENTS, get_agent, play_game


class AIVsAITestGUI:
    def __init__(self, board_size=5, ai1="random", ai2="random", strategy='random', num_rounds=100, minmax_strategy='minmax', max_depth=3, test_games=10, rave_k=300, minmax_eval='stone'):
        pygame.init()
        self.board_size = board_size
        self.grid_size = 80
        self.margin = 80
        self.board_height = self.margin * 2 + self.grid_size * (board_size - 1)
        self.history_height = 280
        self.window_width = self.board_height
        self.window_height = self.board_height + self.history_height
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption(f"iGo AI vs AI Test - {board_size}x{board_size}")
        
        self.colors = {
            'bg': (220, 179, 92),
            'history_bg': (240, 240, 240),
            'line': (0, 0, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }
        
        self.game = GameState.new_game(board_size)
        self.running = True
        self.should_return_to_menu = False
        self.last_move = None
        
        self.ai1_agent = get_agent(ai1, strategy=strategy, num_rounds=num_rounds, minmax_strategy=minmax_strategy, max_depth=max_depth, rave_k=rave_k, minmax_eval=minmax_eval)
        self.ai2_agent = get_agent(ai2, strategy=strategy, num_rounds=num_rounds, minmax_strategy=minmax_strategy, max_depth=max_depth, rave_k=rave_k, minmax_eval=minmax_eval)
        
        self.ai1_type = ai1
        self.ai2_type = ai2
        
        self.test_games = test_games
        self.current_game = 0
        self.results = {Player.black: 0, Player.white: 0, None: 0}
        self.total_moves = 0
        self.total_time = 0
        self.test_complete = False
        self.paused = False
        self.move_history = []
        
        self.font = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 16)
        
        self.back_button_rect = pygame.Rect(10, 10, 100, 35)
        
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
                    pygame.draw.circle(self.screen, color, (x, y), self.grid_size // 2 - 8)
                    pygame.draw.circle(self.screen, self.colors['line'], (x, y), self.grid_size // 2 - 8, 1)
                    
                    if self.last_move and self.last_move.is_play and self.last_move.point == point:
                        box_size = self.grid_size // 2 - 12
                        pygame.draw.rect(self.screen, (255, 0, 0), 
                                        (x - box_size, y - box_size, box_size * 2, box_size * 2), 2)
    
    def draw_stats(self):
        history_rect = pygame.Rect(0, self.board_height, self.window_width, self.history_height)
        pygame.draw.rect(self.screen, self.colors['history_bg'], history_rect)
        
        start_y = self.board_height + 10
        line_height = 24
        
        ai1_label = self.font.render(f"AI 1 (Black): {self.ai1_type}", True, (0, 0, 0))
        self.screen.blit(ai1_label, (10, start_y))
        
        ai2_label = self.font.render(f"AI 2 (White): {self.ai2_type}", True, (0, 0, 0))
        self.screen.blit(ai2_label, (10, start_y + line_height))
        
        game_label = self.font.render(f"Game: {self.current_game + 1}/{self.test_games}", True, (0, 0, 0))
        self.screen.blit(game_label, (10, start_y + line_height * 2))
        
        win1_label = self.font.render(f"AI 1 Wins: {self.results[Player.black]}", True, (0, 0, 0))
        self.screen.blit(win1_label, (10, start_y + line_height * 3))
        
        win2_label = self.font.render(f"AI 2 Wins: {self.results[Player.white]}", True, (0, 0, 0))
        self.screen.blit(win2_label, (10, start_y + line_height * 4))
        
        draw_label = self.font.render(f"Draws: {self.results[None]}", True, (0, 0, 0))
        self.screen.blit(draw_label, (10, start_y + line_height * 5))
        
        if self.current_game > 0:
            avg_moves = self.total_moves / self.current_game
            avg_moves_label = self.font.render(f"Avg Moves: {avg_moves:.1f}", True, (0, 0, 0))
            self.screen.blit(avg_moves_label, (250, start_y + line_height))
            
            avg_time = self.total_time / self.current_game
            avg_time_label = self.font.render(f"Avg Time: {avg_time:.2f}s", True, (0, 0, 0))
            self.screen.blit(avg_time_label, (250, start_y + line_height * 2))
        
        # 显示最后两步棋
        last_moves_label = self.font.render("Last Moves:", True, (0, 0, 0))
        self.screen.blit(last_moves_label, (250, start_y+100))
        
        if len(self.move_history) >= 1:
            # 显示倒数第一步
            player1, move1 = self.move_history[-1]
            move1_text = self.format_move(player1, move1)
            move1_label = self.font.render(move1_text, True, (0, 0, 0))
            self.screen.blit(move1_label, (250, start_y + 100+line_height))
        
        if len(self.move_history) >= 2:
            # 显示倒数第二步
            player2, move2 = self.move_history[-2]
            move2_text = self.format_move(player2, move2)
            move2_label = self.font.render(move2_text, True, (0, 0, 0))
            self.screen.blit(move2_label, (250, start_y + 100+line_height * 2))
    
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
    
    def format_move(self, player, move):
        """将移动转换为文字描述"""
        player_name = "Black" if player == Player.black else "White"
        if move.is_pass:
            return f"{player_name}: PASS"
        elif move.is_resign:
            return f"{player_name}: RESIGN"
        else:
            return f"{player_name}: ({move.point.row}, {move.point.col})"
    
    def run_single_game(self):
        self.game = GameState.new_game(self.board_size)
        self.last_move = None
        self.move_history = []
        agents = {
            Player.black: self.ai1_agent,
            Player.white: self.ai2_agent,
        }
        
        move_count = 0
        start_time = time.time()
        
        while not self.game.is_over() and self.running:
            self.handle_events()
            if not self.running:
                # 用户提前退出，也要返回当前状态
                duration = time.time() - start_time
                winner = self.game.winner()
                return winner, move_count, duration
            
            if self.paused:
                self.draw_board()
                self.draw_back_button()
                self.draw_stats()
                pygame.display.flip()
                continue
            
            agent_fn = agents[self.game.next_player]
            current_player = self.game.next_player
            move = agent_fn(self.game)
            self.last_move = move
            self.move_history.append((current_player, move))
            self.game = self.game.apply_move(move)
            move_count += 1
            
            if move_count > self.board_size * self.board_size * 2:
                break
            
            self.draw_board()
            self.draw_back_button()
            self.draw_stats()
            pygame.display.flip()
        
        duration = time.time() - start_time
        winner = self.game.winner()
        return winner, move_count, duration
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.current_game < self.test_games and self.running:
            winner, moves, duration = self.run_single_game()
            
            # 即使提前退出，只要有对局数据就要统计
            self.results[winner] += 1
            self.total_moves += moves
            self.total_time += duration
            self.current_game += 1
            
            if not self.running:
                break
        
        self.test_complete = True
        
        while self.running:
            self.handle_events()
            
            self.draw_board()
            self.draw_back_button()
            self.draw_stats()
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.display.quit()
        return self.should_return_to_menu


def main():
    import argparse
    parser = argparse.ArgumentParser(description="iGo AI vs AI Test GUI")
    parser.add_argument("--size", type=int, default=5, help="Board size (default 5)")
    parser.add_argument("--ai1", choices=["random", "mcts", "minmax"], default="random", help="AI 1 (default random)")
    parser.add_argument("--ai2", choices=["random", "mcts", "minmax"], default="random", help="AI 2 (default random)")
    parser.add_argument("--games", type=int, default=10, help="Number of games (default 10)")
    args = parser.parse_args()
    
    gui = AIVsAITestGUI(
        board_size=args.size,
        ai1=args.ai1,
        ai2=args.ai2,
        test_games=args.games
    )
    gui.run()


if __name__ == "__main__":
    main()
