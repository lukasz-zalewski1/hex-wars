import pygame
import abc


class Control:
    '''Base class for graphic controls'''

    def __init__(self, rect, title, font, color):
        '''
        Initializes Control object

        Args:
            rect (int, int, int, int): control's rectangle

            title (string): text displayed on control

            font (pygame.font.SysFont): font used to display text
        '''

        self.rect = rect
        self.title = title
        self.font = font
        self.color = color

    def is_point_in_rect(self, point):
        '''
        Returns true if point is in button's rect

        Args:
            point (int, int): point, mostly mouse position

        Returns:
            True if point is inside of button's rect
        '''

        if self.rect[0] <= point[0] <= self.rect[0] + self.rect[2] and \
           self.rect[1] <= point[1] <= self.rect[1] + self.rect[3]:
            return True

        return False


    @abc.abstractmethod
    def render(self, surface):
        '''
        Abstract rendering method
        '''

        pass


class Button(Control):
    def __init__(self, rect, title, font, color):
        '''
        Initializes button objects

        Args:
            rect (int, int, int, int): control's rectangle

            title (string): text displayed on control

            font (pygame.font.SysFont): font used to display text

            color (int, int, int): text color
        '''

        super().__init__(rect, title, font, color)

        self.lines = [[self.rect[0], self.rect[1]],
                      [self.rect[0] + self.rect[2], self.rect[1]],
                      [self.rect[0] + self.rect[2], self.rect[1] +
                       self.rect[3]],
                      [self.rect[0], self.rect[1] + self.rect[3]]]

        self.text = font.render(self.title, True, (255, 255, 255))
        text_rect = self.text.get_rect()
        self.final_text_rect = rect[:]
        self.final_text_rect[0] += (self.rect[2] - text_rect[2]) / 2
        self.final_text_rect[1] += (self.rect[3] - text_rect[3]) / 2
        self.final_text_rect[2] = text_rect[2]
        self.final_text_rect[3] = text_rect[3]

    def render(self, surface):
        '''
        Renders button on surface

        Arguments:
            surface (pygame.Surface): surface to render on
        '''

        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.lines(surface, (0, 0, 0), True, self.lines, 4)
        surface.blit(self.text, self.final_text_rect)


class Slider(Control):
    def __init__(self, rect, text_rect_shift, title, font, min_value,
                 max_value, default_value, step, color, slider_color):
        '''
        Initializes Slider control

        Args:
            rect (int, int, int, int): control's rectangle

            title (string): text displayed on control

            font (pygame.font.SysFont): font used to display text

            min_value (int): slider's min value

            max_value (int): slider's max value

            default_value (int): slider's default value

            step (int): how much value changes with each step

            color (int, int, int): text color

            slider_color (int, int, int): slider's color
        '''

        super().__init__(rect, title, font, color)

        self.base_title = title
        
        self.slider_rect = self.rect[:]
        self.slider_rect[2] //= 4

        self.text_rect = self.rect[:]
        self.text_rect[0] += text_rect_shift[0]
        self.text_rect[1] += text_rect_shift[1]

        self.min_value = min_value
        self.max_value = max_value
        self.value = default_value
        self.step = step

        self.slider_color = slider_color

        self.title = self.base_title + " " + str(self.value) 

        self.__set_starting_position()


    def __set_starting_position(self):
        '''
        Sets slider starting position
        '''

        slider_relative = (self.value - self.min_value) / \
                          (self.max_value - self.min_value)
        self.slider_rect[0] += slider_relative * \
            (self.rect[2] - self.slider_rect[2])


    def move_slider(self, shift):
        '''
        Moves slider by given shift

        Args:
            shift {list(int, int)}
        '''

        self.slider_rect[0] += shift[0]
        if self.slider_rect[0] < self.rect[0]:
            self.slider_rect[0] = self.rect[0]
        elif self.slider_rect[0] + self.slider_rect[2] > \
                self.rect[0] + self.rect[2]:
            self.slider_rect[0] = self.rect[0] + self.rect[2] - \
                self.slider_rect[2]

        slider_relative = ((self.rect[2] - self.slider_rect[2]) -
                           (self.slider_rect[0] - self.rect[0])) / \
            (self.rect[2] - self.slider_rect[2])

        self.value = int(
            self.min_value + (self.max_value - self.min_value) *
            (1.0 - slider_relative)) // \
            self.step * self.step
        
        self.title = self.base_title + " " + str(self.value) 

    def render(self, surface):
        '''
        Renders slider on surface

        Args:
            surface {pygame.Surface}: surface to render on
        '''

        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, self.slider_color, self.slider_rect)
        title_text = self.font.render(self.title, True, (255, 255, 255))
        surface.blit(title_text, self.text_rect)
