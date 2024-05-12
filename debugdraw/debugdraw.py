from abc import ABC, abstractmethod
from dataclasses import dataclass
from ctypes import c_float, sizeof
import ctypes
from logging import getLogger

import numpy as np

logger = getLogger(__name__)


@dataclass
class DebugLine:
    pos0: np.ndarray
    col0: np.ndarray
    pos1: np.ndarray
    col1: np.ndarray

@dataclass
class DebugPoint:
    pos: np.ndarray
    col: np.ndarray
    size: float

class RenderBackend(ABC):
    @abstractmethod
    def begin_draw(self): ...

    @abstractmethod
    def end_draw(self): ...

    @abstractmethod
    def draw_lines(self): ...

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

class LineVertexRecord(ctypes.Structure):
    _fields_ = [
        ('x', c_float),
        ('y', c_float),
        ('z', c_float),
        ('r', c_float),
        ('g', c_float),
        ('b', c_float),
    ]

class PointVertexRecord(ctypes.Structure):
    _fields_ = [
        ('x', c_float),
        ('y', c_float),
        ('z', c_float),
        ('r', c_float),
        ('g', c_float),
        ('b', c_float),
        ('size', c_float),
    ]

class VertexRecord(ctypes.Union):
    _fields_ = [
        ('line', LineVertexRecord),
        ('point', PointVertexRecord),
    ]

class VertexBuffer[T: ctypes.Structure|ctypes.Union]:
    def __init__(self, fmt: type[T], max_size: int):
        self.buffer = (fmt * max_size)()
        self.size = max_size
        self.used = 0

    def __len__(self) -> int:
        return len(self.size)

    def clear(self):
        self.used = 0

    def next(self) -> T:
        v = self.buffer[self.used]
        self.used += 1

        return v

VERTEX_BUFFER_SIZE = 4096
class DebugDrawCtx:
    def __init__(self, backend: RenderBackend):
        self.backend = backend

        self.line_queue = []
        self.point_queue = []

        self.vertexbuf = VertexBuffer(fmt=VertexRecord, max_size=VERTEX_BUFFER_SIZE)

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

    def point(
        self,
        pos: np.ndarray,
        color: np.ndarray,
        size: float,
    ):
        point = DebugPoint(
            pos=pos,
            col=color,
            size=size,
        )

        self.point_queue.append(point)

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

    def axes(self, transform: np.ndarray, axis_length: float, head_size: float):
        origin = np.array([0,0,0,1])
        x_end = np.array([axis_length,0,0,1])
        y_end = np.array([0,axis_length,0,1])
        z_end = np.array([0,0,axis_length,1])

        origin = transform @ origin
        x_end = transform @ x_end
        y_end = transform @ y_end
        z_end = transform @ z_end

        self.arrow(origin[:3],
            x_end[:3],
            color=np.array([1,0,0]),
            head_size=head_size)
        self.arrow(origin[:3],
            y_end[:3],
            color=np.array([0,1,0]),
            head_size=head_size)
        self.arrow(origin[:3],
            z_end[:3],
            color=np.array([0,0,1]),
            head_size=head_size)


    ### mechanisms

    def flush(self):
        self._draw_lines()
        self._draw_points()

        # flush draw queues
        self.line_queue.clear()
        self.point_queue.clear()

    def _draw_lines(self):
        for line in self.line_queue:
            self._line2vertbuf(line)

        # logger.debug(f'calling backend.draw_lines(..., {self.vertices_used})')
        self.backend.draw_lines(self.vertexbuf)
        self.vertexbuf.clear()

    def _draw_points(self):
        for point in self.point_queue:
            self._point2vertbuf(point)

        self.backend.draw_points(self.vertexbuf)
        self.vertexbuf.clear()


    def _line2vertbuf(self, line: DebugLine):
        # TODO: force a draw if we've filled the vertex buffer
        assert (self.vertexbuf.used + 2) < self.vertexbuf.size

        v0 = self.vertexbuf.next()
        v0.line.x = line.pos0[0]
        v0.line.y = line.pos0[1]
        v0.line.z = line.pos0[2]
        v0.line.r = line.col0[0]
        v0.line.g = line.col0[1]
        v0.line.b = line.col0[2]

        v1 = self.vertexbuf.next()
        v1.line.x = line.pos1[0]
        v1.line.y = line.pos1[1]
        v1.line.z = line.pos1[2]
        v1.line.r = line.col1[0]
        v1.line.g = line.col1[1]
        v1.line.b = line.col1[2]

    def _point2vertbuf(self, point: DebugPoint):
        # TODO: force a draw if we've filled the vertex buffer
        assert (self.vertexbuf.used + 1) < self.vertexbuf.size

        v0 = self.vertexbuf.next()
        v0.point.x = point.pos[0]
        v0.point.y = point.pos[1]
        v0.point.z = point.pos[2]
        v0.point.r = point.col[0]
        v0.point.g = point.col[1]
        v0.point.b = point.col[2]
        v0.point.size = point.size
