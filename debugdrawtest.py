import ctypes
import logging

from OpenGL import GL
from OpenGL.GL import shaders
import pygame
import numpy as np
import scipy.spatial.transform as txf

from debugdraw import DebugDrawCtx, GLDebugDrawBackend


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def rotate_around_x(theta):
    return np.array([
        [1., 0.,             0.,             0.],
        [0., np.cos(theta), -np.sin(theta),  0.],
        [0., np.sin(theta),  np.cos(theta),  0.],
        [0., 0.,             0.,             1.],
    ])

def rotate_around_y(theta):
    return np.array([
        [ np.cos(theta), 0., np.sin(theta), 0.],
        [ 0.,            1., 0.,            0.],
        [-np.sin(theta), 0., np.cos(theta), 0.],
        [ 0.,            0., 0.,            1.],
    ])

def rotate_around_z(theta):
    return np.array([
        [np.cos(theta), -np.sin(theta), 0., 0.],
        [np.sin(theta),  np.cos(theta), 0., 0.],
        [0.,             0.,            1., 0.],
        [0.,             0.,            0., 1.],
    ])

class OrbitCamera:
    def __init__(self):
        self.rot_x = 0
        self.rot_y = 0

    @property
    def view_matrix(self) -> np.ndarray:
        rotation = rotate_around_x(self.rot_x) @ rotate_around_y(self.rot_y)

        return rotation

class App:
    def __init__(self):
        self.camera = OrbitCamera()

    def setup(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)

        self.debugdraw = DebugDrawCtx(GLDebugDrawBackend())

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.debugdraw.line(np.array([0.6, 0.6, 0.0]), np.array([-0.6, 0.6, 0.0]), np.array([1.0, 0.0, 0.0]))
        # self.debugdraw.cross(np.array([0,0,0]),1)
        self.debugdraw.arrow(np.array([0,-0.5,0]),
            np.array([0,0.5,0]),
            color=np.array([1,0,1]),
            head_size=0.3)


        self.debugdraw.backend.mvp_matrix = self.camera.view_matrix
        self.debugdraw.flush()

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            lb, mb, rb = pygame.mouse.get_pressed()
            if lb:
                CAM_SPEED = 0.1 * (np.pi/180.)
                cursor_delta_x, cursor_delta_y = event.rel

                self.camera.rot_y += cursor_delta_x * CAM_SPEED
                self.camera.rot_x += cursor_delta_y * CAM_SPEED

if __name__ == '__main__':
    pygame.init()
    # opengl4.1 core
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    screen = pygame.display.set_mode((800, 800), pygame.OPENGL|pygame.DOUBLEBUF)

    app = App()
    app.setup()

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