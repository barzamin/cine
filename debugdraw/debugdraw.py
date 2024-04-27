from abc import ABC, abstractmethod
from dataclasses import dataclass
from ctypes import Structure, c_float, sizeof
from logging import getLogger

import numpy as np

logger = getLogger(__name__)


@dataclass
class DebugLine:
    pos0: np.ndarray
    col0: np.ndarray
    pos1: np.ndarray
    col1: np.ndarray

class RenderBackend(ABC):
    @abstractmethod
    def begin_draw(self): ...

    @abstractmethod
    def end_draw(self): ...

    @abstractmethod
    def draw_lines(self): ...

class VertexRecord(Structure):
    _fields_ = [
        ('x', c_float),
        ('y', c_float),
        ('z', c_float),
        ('r', c_float),
        ('g', c_float),
        ('b', c_float),
    ]

def _make_orthonormal_basis(forward: np.ndarray) -> (np.ndarray, np.ndarray):
    # via glampert
    if abs(forward[2]) > 0.7:
        # up vector in YZ plane

        # norm(forward.yz)
        len_sqr = forward[1]*forward[1] + forward[2]*forward[2]
        inv_len = len_sqr**-0.5

        up = np.array([
            0.,
            forward[2] * inv_len, # Y <- Z
            -forward[1] * inv_len, # Z <- -Y
        ])

        right = np.array([
            len_sqr * inv_len,
            -forward[0] * up[2],
            forward[0] * up[1],
        ])

    else:
        # up vector in XY plane

        # norm(forward.yz)
        len_sqr = forward[0]*forward[0] + forward[1]*forward[1]
        inv_len = len_sqr**-0.5

        right = np.array([
            -forward[1] * inv_len, # Y <- Z
            forward[0] * inv_len, # Z <- -Y
            0.,
        ])

        up = np.array([
            -forward[2] * right[1],
            forward[2] * right[0],
            len_sqr * inv_len,
        ])


    return (up, right)

VERTEX_BUFFER_SIZE = 4096
class DebugDrawCtx:
    def __init__(self, backend: RenderBackend):
        self.backend = backend

        self.line_queue = []

        self.vertex_buffer = (VertexRecord * VERTEX_BUFFER_SIZE)()
        self.vertices_used = 0

    ###

    def line(
        self,
        pos_from: np.ndarray, pos_to: np.ndarray,
        color_from: np.ndarray, color_to: np.ndarray = None,
    ):
        line = DebugLine(
            pos0 = pos_from,
            pos1 = pos_to,
            col0 = color_from,
            col1 = color_to or color_from
        )

        self.line_queue.append(line)

    ### sugar
    def cross(self, pos: np.ndarray, length: float):
        hl = np.identity(3) * length/2.

        # red-x, green-y, blue-z
        RED   = np.array([1., 0., 0.])
        GREEN = np.array([0., 1., 0.])
        BLUE  = np.array([0., 0., 1.])

        # x
        self.line(pos + hl[0], pos - hl[0], RED)
        # y
        self.line(pos + hl[1], pos - hl[1], GREEN)
        # z
        self.line(pos + hl[2], pos - hl[2], BLUE)

    def arrow(self, start: np.ndarray, end: np.ndarray, color: np.ndarray,
              head_size: float, subdiv: int = 16):
        forward = end - start
        forward /= np.linalg.norm(forward)
        up, right = _make_orthonormal_basis(forward)

        self.line(start, end, color)
        # self.line(start, start+forward*0.3, np.array([1.,1.,0]))
        # self.line(start, start+up*0.1, np.array([0.,1.,1.]))
        # self.line(start, start+right*0.1, np.array([1.,0.,1.]))

        head_fwd = forward * head_size
        for i in range(subdiv):
            # head_fwd

            # current vertex on ring
            phi0 = i*2*np.pi/subdiv
            v0 = ((end - head_fwd)
                + np.cos(phi0)*0.5*head_size*right # x
                + np.sin(phi0)*0.5*head_size*up) #y

            # next vertex on ring
            phi1 = (i+1)*2*np.pi/subdiv
            v1 = ((end - head_fwd)
                + np.cos(phi1)*0.5*head_size*right # x
                + np.sin(phi1)*0.5*head_size*up) #y


            self.line(v0, end, color)
            self.line(v0, v1, color)

    ### mechanisms

    def flush(self):
        self._draw_lines()

        # flush draw queues
        self.line_queue.clear()

    def _draw_lines(self):
        for line in self.line_queue:
            self._line2vertbuf(line)

        # logger.debug(f'calling backend.draw_lines(..., {self.vertices_used})')
        self.backend.draw_lines(self.vertex_buffer, self.vertices_used)
        self.vertices_used = 0

    def _line2vertbuf(self, line: DebugLine):
        # TODO: force a draw if we've filled the vertex buffer
        assert (self.vertices_used + 2) < len(self.vertex_buffer)

        v0 = self.vertex_buffer[self.vertices_used]
        self.vertices_used += 1
        v0.x = line.pos0[0]
        v0.y = line.pos0[1]
        v0.z = line.pos0[2]
        v0.r = line.col0[0]
        v0.g = line.col0[1]
        v0.b = line.col0[2]

        v1 = self.vertex_buffer[self.vertices_used]
        self.vertices_used += 1
        v1.x = line.pos1[0]
        v1.y = line.pos1[1]
        v1.z = line.pos1[2]
        v1.r = line.col1[0]
        v1.g = line.col1[1]
        v1.b = line.col1[2]
