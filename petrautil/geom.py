import numpy as np

def rotate_around_x(theta: float):
    return np.array([
        [1., 0.,             0.,             0.],
        [0., np.cos(theta), -np.sin(theta),  0.],
        [0., np.sin(theta),  np.cos(theta),  0.],
        [0., 0.,             0.,             1.],
    ])

def rotate_around_y(theta: float):
    return np.array([
        [ np.cos(theta), 0., np.sin(theta), 0.],
        [ 0.,            1., 0.,            0.],
        [-np.sin(theta), 0., np.cos(theta), 0.],
        [ 0.,            0., 0.,            1.],
    ])

def rotate_around_z(theta: float):
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


def translate(x: float, y: float, z: float) -> np.ndarray:
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ])
