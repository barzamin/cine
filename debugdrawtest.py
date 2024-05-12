import ctypes
import logging

from OpenGL import GL
import pygame
import numpy as np

from debugdraw import DebugDrawCtx, GLDebugDrawBackend
from petrautil.pygameogl import App, run_app
from petrautil.camera import OrbitCamera


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugDrawTestApp(App):
    def __init__(self):
        ...

    def setup(self, windowsize: tuple[int, int]):
        self.camera = OrbitCamera(*windowsize)
        self.camera.rot_x = np.pi/7
        self.camera.rot_y = np.pi/9

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)

        self.debugdraw = DebugDrawCtx(GLDebugDrawBackend())

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.debugdraw.line(np.array([0.6, 0.6, 0.0]), np.array([-0.6, 0.6, 0.0]), np.array([1.0, 0.0, 0.0]))
        self.debugdraw.cross(np.array([0,0,0]),0.2)
        self.debugdraw.cross(np.array([0,0,-1]),0.5)
        self.debugdraw.point(np.array([0,0,0]), np.array([1., 0., 1.]), 15.)

        self.debugdraw.axes(np.identity(4), axis_length=1, head_size=0.3)

        self.debugdraw.backend.mvp_matrix = self.camera.vp_matrix
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
            self.camera.zoom += event.y / 100

if __name__ == '__main__':
    run_app(DebugDrawTestApp(), windowsize=(800, int(800*9/16)))
