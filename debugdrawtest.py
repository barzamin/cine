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

def ortho_proj_matrix(left: float, right: float,
    bottom: float, top: float,
    near: float, far
) -> np.ndarray:
    inv_w = 1/(right - left)
    inv_h = 1/(top - bottom)
    inv_d = 1/(far - near)

    return np.array([
        [2*inv_w, 0,       0,        -(right+left)*inv_w],
        [0,       2*inv_h, 0,        -(top+bottom)*inv_h],
        [0,       0,       -2*inv_d, -(far+near)*inv_d  ],
        [0,       0,       0,        1                  ],
    ])


def translate(x, y, z) -> np.ndarray:
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ])

class OrbitCamera:
    def __init__(self, fb_width: float, fb_height: float):
        self.fb_width = fb_width
        self.fb_height = fb_height
        self.rot_x = 0
        self.rot_y = 0

    @property
    def view_matrix(self) -> np.ndarray:
        return translate(0, 0, -5.) @ rotate_around_x(self.rot_x) @ rotate_around_y(self.rot_y)

    @property
    def proj_matrix(self) -> np.ndarray:
        aspect_ratio = self.fb_height/self.fb_width
        zoom = 2
        return ortho_proj_matrix(
            -zoom*0.5, zoom*0.5,
            -zoom*0.5*aspect_ratio, zoom*0.5*aspect_ratio,
            0.1, 100.
        )

    @property
    def vp_matrix(self) -> np.ndarray:
        return self.proj_matrix @ self.view_matrix

class App:
    def __init__(self):
        self.camera = OrbitCamera(800, 800)

    def setup(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)

        self.debugdraw = DebugDrawCtx(GLDebugDrawBackend())

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # self.debugdraw.line(np.array([0.6, 0.6, 0.0]), np.array([-0.6, 0.6, 0.0]), np.array([1.0, 0.0, 0.0]))
        self.debugdraw.cross(np.array([0,0,0]),0.2)
        self.debugdraw.cross(np.array([0,0,-1]),0.5)

        # self.debugdraw.arrow(np.array([0,0.,0]),
        #     np.array([0,0.0,-5]),
        #     color=np.array([1,0,1]),
        #     head_size=0.3)


        self.debugdraw.backend.mvp_matrix = self.camera.vp_matrix
        print(self.camera.proj_matrix)
        self.debugdraw.flush()

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            lb, mb, rb = pygame.mouse.get_pressed()
            if lb:
                CAM_SPEED = 0.1 * (np.pi/180.)
                cursor_delta_x, cursor_delta_y = event.rel

                self.camera.rot_y -= cursor_delta_x * CAM_SPEED
                self.camera.rot_x -= cursor_delta_y * CAM_SPEED

        if event.type == pygame.MOUSEWHEEL:
            # print(event)
            ...


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