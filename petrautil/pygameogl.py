import pygame
from OpenGL import GL
from OpenGL.GL import shaders
from abc import ABC, abstractmethod

class App(ABC):
    @abstractmethod
    def setup(self, windowsize: tuple[int, int]): ...

    @abstractmethod
    def draw(self): ...

    @abstractmethod
    def handle_event(self, event): ...

def run_app(app: App, windowsize: tuple[int, int]):
    windowsize = windowsize or (800, 800)

    pygame.init()
    # opengl4.1 core
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    screen = pygame.display.set_mode(windowsize, pygame.OPENGL|pygame.DOUBLEBUF)

    app.setup(windowsize)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                app.handle_event(event)


        app.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
