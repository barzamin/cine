import struct
import logging
from dataclasses import dataclass

import IPython
import numpy as np
import pygame
from OpenGL import GL

from memory import DOLMemory
from melee import FighterKind, FighterBone, JObj_Flags, JObj, Melee
from melee import P_PLAYER_SLOTS, PLAYER_SLOT_SIZE
from petrautil.pygameogl import App, run_app
from petrautil.camera import OrbitCamera
from petrautil.hexdump import hexdump
from debugdraw import DebugDrawCtx, GLDebugDrawBackend


logging.basicConfig(level=logging.INFO)
np.set_printoptions(linewidth=120)


mem = DOLMemory()
melee = Melee(mem)

fighter = melee.get_fighter(slot=0)
fighter_bones = fighter.get_fighterbones()

class RenderableJObj(JObj):
    @classmethod
    def from_mem(cls, mem, p_jobj, parent=None):
        self = super().from_mem(mem, p_jobj)

        self.parent = parent
        self.child = self.sister = None
        if self.p_child:
            self.child = cls.from_mem(mem, self.p_child, parent=self)
        if self.p_next:
            self.child = cls.from_mem(mem, self.p_next, parent=self)

        return self

    def recompute_transforms(self):
        txf_local = mat_scale(self.scale) @ mat_quat(self.rotate) @ mat_translate(self.translate)

        assert NotImplementedError()
        # if self.parent:
        #     # txf_world =

root_jobj = RenderableJObj.from_mem(mem, fighter_bones[0].p_joint)
assert JObj_Flags.SKELETON_ROOT in root_jobj.flags

class BonesApp(App):
    def setup(self, winsize):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)

        self.camera = OrbitCamera(*winsize)
        self.debugdraw = DebugDrawCtx(GLDebugDrawBackend())

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        self.debugdraw.line(np.array([0.6, 0.6, 0.0]), np.array([-0.6, 0.6, 0.0]), np.array([1.0, 0.0, 0.0]))
        self.debugdraw.cross(np.array([0,0,0]),0.2)
        self.debugdraw.cross(np.array([0,0,-1]),0.5)
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
            self.camera.zoom += event.y / 50

if __name__ == '__main__':
    run_app(BonesApp(), windowsize=(800, int(800*9/16)))
