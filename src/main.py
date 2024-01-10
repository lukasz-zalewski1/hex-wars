import pygame

import controls
import map
import game
import graphics
import events


class Main:
    def __init__(self):
        '''
        Initializes main game objects
        '''

        pygame.init()
        players = [game.Player((255, 0, 0)), game.Player((0, 255, 100))]

        resolution = pygame.display.Info()

        self.window_size = (resolution.current_w, resolution.current_h)

        self.map_ = map.Map((5, 5), 10, players, 4, 32, self.window_size)
        self.map_.create_map()

        self.gameplay = game.Gameplay(self.map_, 6, 2000, 8)
        self.graphics = graphics.Graphics(self.map_, self.gameplay,
                                          self.window_size)
        self.event_handler = events.EventHandler(self.map_, self.graphics,
                                                 self.gameplay)


    def play(self):
        '''
        Starts event loop
        '''

        self.event_handler.event_loop()

if __name__ == '__main__':
    main = Main()
    main.play()
