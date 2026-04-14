#!/usr/bin/env python3
"""
iGo Game Launcher
"""
import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.main_menu import get_settings
from gui.game_gui import GoGameGUI
from gui.ai_gui import AIGoGameGUI
from gui.ai_vs_ai import AIVsAIGameGUI
from gui.ai_vs_ai_test import AIVsAITestGUI
from gui.debug_gui import DebugGoGameGUI


def main():
    while True:
        settings = get_settings()
        
        human_first = settings.get('ai_color', 'black') != 'black'
        rave_k = settings.get('rave_k', 300)
        minmax_eval = settings.get('minmax_eval', 'stone')
        
        if settings['debug'] and settings['mode'] == 'pva' and settings['ai1'] == 'mcts':
            gui = DebugGoGameGUI(
                board_size=settings['size'],
                ai_agent='mcts',
                human_first=human_first,
                strategy=settings['strategy'],
                num_rounds=settings['num_rounds'],
                max_depth=settings['max_depth'],
                rave_k=rave_k,
                minmax_eval=minmax_eval
            )
        elif settings['mode'] == 'pva':
            gui = AIGoGameGUI(
                board_size=settings['size'],
                ai_agent=settings['ai1'],
                human_first=human_first,
                strategy=settings['strategy'],
                num_rounds=settings['num_rounds'],
                minmax_strategy=settings['minmax_strategy'],
                max_depth=settings['max_depth'],
                rave_k=rave_k,
                minmax_eval=minmax_eval
            )
        elif settings['mode'] == 'ava':
            if settings.get('test_mode', False):
                gui = AIVsAITestGUI(
                    board_size=settings['size'],
                    ai1=settings['ai1'],
                    ai2=settings['ai2'],
                    strategy=settings['strategy'],
                    num_rounds=settings['num_rounds'],
                    minmax_strategy=settings['minmax_strategy'],
                    max_depth=settings['max_depth'],
                    test_games=settings['test_games'],
                    rave_k=rave_k,
                    minmax_eval=minmax_eval
                )
            else:
                gui = AIVsAIGameGUI(
                    board_size=settings['size'],
                    ai1=settings['ai1'],
                    ai2=settings['ai2'],
                    strategy=settings['strategy'],
                    num_rounds=settings['num_rounds'],
                    minmax_strategy=settings['minmax_strategy'],
                    max_depth=settings['max_depth'],
                    rave_k=rave_k,
                    minmax_eval=minmax_eval
                )
        
        should_return = gui.run()
        
        if not should_return:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
