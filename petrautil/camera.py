import numpy as np

from .geom import *


class OrbitCamera:
    def __init__(self, fb_width: float, fb_height: float):
        self.fb_width = fb_width
        self.fb_height = fb_height
        self.rot_x = 0
        self.rot_y = 0
        self.zoom = 2

    def resize(fb_width: float, fb_height: float):
        self.fb_width = fb_width
        self.fb_height = fb_height

    @property
    def view_matrix(self) -> np.ndarray:
        return translate(0, 0, -5.) @ rotate_around_x(self.rot_x) @ rotate_around_y(self.rot_y)
        # return translate(0, 0, -5)

    @property
    def proj_matrix(self) -> np.ndarray:
        aspect_ratio = self.fb_height/self.fb_width
        halfw = self.zoom*0.5
        halfh = halfw * aspect_ratio

        return ortho_proj_matrix(
            -halfw, halfw,
            -halfh, halfh,
            0.1, 100.
        )

    @property
    def vp_matrix(self) -> np.ndarray:
        return self.proj_matrix @ self.view_matrix
