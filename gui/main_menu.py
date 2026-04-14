import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, selected_color=None, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.selected_color = selected_color if selected_color else (40, 200, 40)
        self.text_color = text_color
        self.font = pygame.font.Font(None, 30)
        self.selected = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.selected:
            pygame.draw.rect(screen, self.selected_color, self.rect)
        elif self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 4 if self.selected else 2)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Checkbox:
    def __init__(self, x, y, text, checked=False):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.text = text
        self.checked = checked
        self.font = pygame.font.Font(None, 28)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, (0, 0, 0), (self.rect.left + 3, self.rect.centery), 
                           (self.rect.centerx, self.rect.bottom - 3), 3)
            pygame.draw.line(screen, (0, 0, 0), (self.rect.centerx, self.rect.bottom - 3), 
                           (self.rect.right - 3, self.rect.top + 3), 3)
        
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.right + 10, self.rect.y))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False


class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 0, 0)
        self.text = text
        self.font = pygame.font.Font(None, 28)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (0, 100, 255) if self.active else (0, 0, 0)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = (0, 0, 0)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


class MainMenu:
    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 980
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("iGo")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"
        self.font_title = pygame.font.Font(None, 140)
        self.font_label = pygame.font.Font(None, 32)
        
        self.settings = {
            'mode': 'pva',
            'size': 5,
            'ai1': 'random',
            'ai2': 'random',
            'debug': False,
            'strategy': 'random',
            'minmax_strategy': 'minmax',
            'minmax_eval': 'stone',
            'ai_color': 'black',
            'num_rounds': 100,
            'max_depth': 3,
            'test_mode': False,
            'test_games': 10,
            'rave_k': 300
        }
        
        self.buttons = {}
        self.checkboxes = {}
        self.input_boxes = {}
        
    def setup_menu(self):
        self.buttons['start'] = Button(
            self.width//2 - 120, 420, 240, 70, "START",
            (50, 150, 50), (80, 200, 80)
        )
        
    def setup_settings(self):
        self.buttons['pva'] = Button(
            250, 50, 300, 60, "Player vs AI",
            (70, 130, 180), (100, 160, 210)
        )
        self.buttons['ava'] = Button(
            650, 50, 300, 60, "AI vs AI",
            (70, 130, 180), (100, 160, 210)
        )
        
        self.input_boxes['size'] = InputBox(550, 130, 120, 40, str(self.settings['size']))
        
        self.buttons['random1'] = Button(
            150, 150, 160, 50, "Random",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['mcts1'] = Button(
            150, 210, 160, 50, "MCTS",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['minmax1'] = Button(
            150, 270, 160, 50, "minmax",
            (150, 150, 150), (180, 180, 180)
        )
        
        self.buttons['ai_black'] = Button(
            150, 360, 160, 40, "AI is Black",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['ai_white'] = Button(
            150, 410, 160, 40, "AI is White",
            (150, 150, 150), (180, 180, 180)
        )
        
        self.buttons['random2'] = Button(
            890, 150, 160, 50, "Random",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['mcts2'] = Button(
            890, 210, 160, 50, "MCTS",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['minmax2'] = Button(
            890, 270, 160, 50, "minmax",
            (150, 150, 150), (180, 180, 180)
        )
        
        self.checkboxes['debug'] = Checkbox(1000, 775, "Debug Mode", self.settings['debug'])
        self.checkboxes['test_mode'] = Checkbox(400, 320, "Test Mode", self.settings['test_mode'])
        self.input_boxes['test_games'] = InputBox(670, 325, 120, 40, str(self.settings['test_games']))
        
        self.input_boxes['num_rounds'] = InputBox(350, 480, 120, 40, str(self.settings['num_rounds']))
        self.input_boxes['rave_k'] = InputBox(750, 485, 120, 40, str(self.settings['rave_k']))
        
        self.buttons['strategy_random'] = Button(
            150, 580, 160, 50, "Random",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['strategy_remove'] = Button(
            350, 580, 160, 50, "Remove First",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['strategy_liberty'] = Button(
            550, 580, 160, 50, "Liberty First",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['strategy_rave'] = Button(
            750, 580, 160, 50, "RAVE",
            (150, 150, 150), (180, 180, 180)
        )
        
        self.buttons['minmax_minmax'] = Button(
            150, 680, 200, 50, "minmax",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['minmax_alphabeta'] = Button(
            350, 680, 200, 50, "Alpha-Beta",
            (150, 150, 150), (180, 180, 180)
        )
        
        self.buttons['minmax_eval_stone'] = Button(
            650, 680, 200, 50, "Stone Eval",
            (150, 150, 150), (180, 180, 180)
        )
        self.buttons['minmax_eval_territory'] = Button(
            850, 680, 200, 50, "Territory Eval",
            (150, 150, 150), (180, 180, 180)
        )
        
        self.input_boxes['max_depth'] = InputBox(340, 750, 120, 40, str(self.settings['max_depth']))
        
        self.buttons['back'] = Button(
            280, 820, 240, 60, "BACK",
            (180, 80, 80), (210, 110, 110)
        )
        self.buttons['play'] = Button(
            680, 820, 240, 60, "PLAY",
            (50, 150, 50), (80, 200, 80)
        )
        
    def draw_menu(self):
        self.screen.fill((220, 179, 92))
        
        title = self.font_title.render("iGo", True, (0, 0, 0))
        title_rect = title.get_rect(center=(self.width//2, 300))
        self.screen.blit(title, title_rect)
        
        self.buttons['start'].draw(self.screen)
        
    def update_button_selections(self):
        self.buttons['pva'].selected = (self.settings['mode'] == 'pva')
        self.buttons['ava'].selected = (self.settings['mode'] == 'ava')
        
        if self.settings['mode'] in ['pva', 'ava']:
            self.buttons['random1'].selected = (self.settings['ai1'] == 'random')
            self.buttons['mcts1'].selected = (self.settings['ai1'] == 'mcts')
            self.buttons['minmax1'].selected = (self.settings['ai1'] == 'minmax')
        
        if self.settings['mode'] == 'pva':
            self.buttons['ai_black'].selected = (self.settings['ai_color'] == 'black')
            self.buttons['ai_white'].selected = (self.settings['ai_color'] == 'white')
        
        if self.settings['mode'] == 'ava':
            self.buttons['random2'].selected = (self.settings['ai2'] == 'random')
            self.buttons['mcts2'].selected = (self.settings['ai2'] == 'mcts')
            self.buttons['minmax2'].selected = (self.settings['ai2'] == 'minmax')
        
        if self.settings['mode'] in ['pva', 'ava']:
            if self.settings['ai1'] == 'mcts' or self.settings['ai2'] == 'mcts':
                self.buttons['strategy_random'].selected = (self.settings['strategy'] == 'random')
                self.buttons['strategy_remove'].selected = (self.settings['strategy'] == 'remove_first')
                self.buttons['strategy_liberty'].selected = (self.settings['strategy'] == 'liberty_first')
                self.buttons['strategy_rave'].selected = (self.settings['strategy'] == 'rave')
            
            if self.settings['ai1'] == 'minmax' or self.settings['ai2'] == 'minmax':
                self.buttons['minmax_minmax'].selected = (self.settings['minmax_strategy'] == 'minmax')
                self.buttons['minmax_alphabeta'].selected = (self.settings['minmax_strategy'] == 'alphabeta')
                self.buttons['minmax_eval_stone'].selected = (self.settings['minmax_eval'] == 'stone')
                self.buttons['minmax_eval_territory'].selected = (self.settings['minmax_eval'] == 'territory')
    
    def draw_settings(self):
        self.update_button_selections()
        self.screen.fill((220, 179, 92))
        
        self.buttons['pva'].draw(self.screen)
        self.buttons['ava'].draw(self.screen)
        
        size_label = self.font_label.render("Board Size:", True, (0, 0, 0))
        self.screen.blit(size_label, (400, 130))
        self.input_boxes['size'].draw(self.screen)
        
        if self.settings['mode'] in ['pva', 'ava']:
            ai1_label = self.font_label.render("AI 1:", True, (0, 0, 0))
            self.screen.blit(ai1_label, (150, 120))
            self.buttons['random1'].draw(self.screen)
            self.buttons['mcts1'].draw(self.screen)
            self.buttons['minmax1'].draw(self.screen)
        
        if self.settings['mode'] == 'pva':
            ai_color_label = self.font_label.render("AI Color:", True, (0, 0, 0))
            self.screen.blit(ai_color_label, (150, 330))
            self.buttons['ai_black'].draw(self.screen)
            self.buttons['ai_white'].draw(self.screen)
        
        if self.settings['mode'] == 'ava':
            ai2_label = self.font_label.render("AI 2:", True, (0, 0, 0))
            self.screen.blit(ai2_label, (890, 120))
            self.buttons['random2'].draw(self.screen)
            self.buttons['mcts2'].draw(self.screen)
            self.buttons['minmax2'].draw(self.screen)
        
        self.checkboxes['debug'].draw(self.screen)
        
        if self.settings['mode'] == 'ava':
            self.checkboxes['test_mode'].draw(self.screen)
            if self.checkboxes['test_mode'].checked:
                test_games_label = self.font_label.render("Games:", True, (0, 0, 0))
                self.screen.blit(test_games_label, (550, 320))
                self.input_boxes['test_games'].draw(self.screen)
        
        if self.settings['mode'] in ['pva', 'ava']:
            if self.settings['ai1'] == 'mcts' or self.settings['ai2'] == 'mcts':
                num_rounds_label = self.font_label.render("MCTS Rounds:", True, (0, 0, 0))
                self.screen.blit(num_rounds_label, (150, 480))
                self.input_boxes['num_rounds'].draw(self.screen)
                
                rave_k_label = self.font_label.render("RAVE k:", True, (0, 0, 0))
                self.screen.blit(rave_k_label, (560, 480))
                self.input_boxes['rave_k'].draw(self.screen)
            
                strategy_label = self.font_label.render("MCTS Strategy:", True, (0, 0, 0))
                self.screen.blit(strategy_label, (150, 540))
                self.buttons['strategy_random'].draw(self.screen)
                self.buttons['strategy_remove'].draw(self.screen)
                self.buttons['strategy_liberty'].draw(self.screen)
                self.buttons['strategy_rave'].draw(self.screen)
            
            if self.settings['ai1'] == 'minmax' or self.settings['ai2'] == 'minmax':
                minmax_strategy_label = self.font_label.render("minmax Strategy:", True, (0, 0, 0))
                self.screen.blit(minmax_strategy_label, (150, 640))
                self.buttons['minmax_minmax'].draw(self.screen)
                self.buttons['minmax_alphabeta'].draw(self.screen)
                
                max_depth_label = self.font_label.render("Max Depth:", True, (0, 0, 0))
                self.screen.blit(max_depth_label, (150, 740))
                self.input_boxes['max_depth'].draw(self.screen)
                
                minmax_eval_label = self.font_label.render("minmax Eval:", True, (0, 0, 0))
                self.screen.blit(minmax_eval_label, (550, 640))
                self.buttons['minmax_eval_stone'].draw(self.screen)
                self.buttons['minmax_eval_territory'].draw(self.screen)
        
        self.buttons['back'].draw(self.screen)
        self.buttons['play'].draw(self.screen)
        
    def handle_menu_events(self, event):
        if self.buttons['start'].is_clicked(event):
            self.state = "settings"
            self.setup_settings()
            
    def handle_settings_events(self, event):
        if self.buttons['pva'].is_clicked(event):
            self.settings['mode'] = 'pva'
        if self.buttons['ava'].is_clicked(event):
            self.settings['mode'] = 'ava'
            
        self.input_boxes['size'].handle_event(event)
        
        if self.settings['mode'] in ['pva', 'ava']:
            if self.buttons['random1'].is_clicked(event):
                self.settings['ai1'] = 'random'
            if self.buttons['mcts1'].is_clicked(event):
                self.settings['ai1'] = 'mcts'
            if self.buttons['minmax1'].is_clicked(event):
                self.settings['ai1'] = 'minmax'
        
        if self.settings['mode'] == 'pva':
            if self.buttons['ai_black'].is_clicked(event):
                self.settings['ai_color'] = 'black'
            if self.buttons['ai_white'].is_clicked(event):
                self.settings['ai_color'] = 'white'
        
        if self.settings['mode'] == 'ava':
            if self.buttons['random2'].is_clicked(event):
                self.settings['ai2'] = 'random'
            if self.buttons['mcts2'].is_clicked(event):
                self.settings['ai2'] = 'mcts'
            if self.buttons['minmax2'].is_clicked(event):
                self.settings['ai2'] = 'minmax'
            
        self.checkboxes['debug'].is_clicked(event)
        self.settings['debug'] = self.checkboxes['debug'].checked
        
        if self.settings['mode'] == 'ava':
            self.checkboxes['test_mode'].is_clicked(event)
            self.settings['test_mode'] = self.checkboxes['test_mode'].checked
            self.input_boxes['test_games'].handle_event(event)
        
        self.input_boxes['num_rounds'].handle_event(event)
        self.input_boxes['max_depth'].handle_event(event)
        self.input_boxes['rave_k'].handle_event(event)
        
        if self.settings['mode'] in ['pva', 'ava']:
            if self.buttons['strategy_random'].is_clicked(event):
                self.settings['strategy'] = 'random'
            if self.buttons['strategy_remove'].is_clicked(event):
                self.settings['strategy'] = 'remove_first'
            if self.buttons['strategy_liberty'].is_clicked(event):
                self.settings['strategy'] = 'liberty_first'
            if self.buttons['strategy_rave'].is_clicked(event):
                self.settings['strategy'] = 'rave'
            
            if self.settings['ai1'] == 'minmax' or self.settings['ai2'] == 'minmax':
                if self.buttons['minmax_minmax'].is_clicked(event):
                    self.settings['minmax_strategy'] = 'minmax'
                if self.buttons['minmax_alphabeta'].is_clicked(event):
                    self.settings['minmax_strategy'] = 'alphabeta'
                if self.buttons['minmax_eval_stone'].is_clicked(event):
                    self.settings['minmax_eval'] = 'stone'
                if self.buttons['minmax_eval_territory'].is_clicked(event):
                    self.settings['minmax_eval'] = 'territory'
        
        if self.buttons['back'].is_clicked(event):
            self.state = "menu"
            self.setup_menu()
            
        if self.buttons['play'].is_clicked(event):
            try:
                self.settings['size'] = int(self.input_boxes['size'].text)
            except ValueError:
                self.settings['size'] = 5
            try:
                self.settings['num_rounds'] = int(self.input_boxes['num_rounds'].text)
                if self.settings['num_rounds'] < 1:
                    self.settings['num_rounds'] = 100
            except ValueError:
                self.settings['num_rounds'] = 100
            
            try:
                self.settings['max_depth'] = int(self.input_boxes['max_depth'].text)
                if self.settings['max_depth'] < 1:
                    self.settings['max_depth'] = 3
            except ValueError:
                self.settings['max_depth'] = 3
            
            try:
                self.settings['test_games'] = int(self.input_boxes['test_games'].text)
                if self.settings['test_games'] < 1:
                    self.settings['test_games'] = 10
            except ValueError:
                self.settings['test_games'] = 10
            
            try:
                self.settings['rave_k'] = int(self.input_boxes['rave_k'].text)
                if self.settings['rave_k'] < 1:
                    self.settings['rave_k'] = 300
            except ValueError:
                self.settings['rave_k'] = 300
            
            self.running = False
            
    def run(self):
        self.setup_menu()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if self.state == "menu":
                    self.handle_menu_events(event)
                elif self.state == "settings":
                    self.handle_settings_events(event)
                    
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "settings":
                self.draw_settings()
                
            pygame.display.flip()
            self.clock.tick(30)
            
        return self.settings


def get_settings():
    menu = MainMenu()
    return menu.run()


if __name__ == "__main__":
    settings = get_settings()
    print("Settings:", settings)
