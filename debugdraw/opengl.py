from ctypes import sizeof, c_void_p, c_float

from OpenGL import GL
from OpenGL.GL import shaders

from . import debugdraw as dd


class GLDebugDrawBackend(dd.RenderBackend):
    LINEPT_SHADER_VERT = '''
#version 330

layout (location = 0) in vec3 i_pos;
layout (location = 1) in vec3 i_color;
layout (location = 2) in float point_size;

out vec4 v_color;

uniform mat4 u_mvp_matrix;

void main() {
    gl_Position = u_mvp_matrix * vec4(i_pos, 1.);
    v_color = vec4(i_color, 1.);
    gl_PointSize = point_size; // junk and ignored when we draw as GL_LINES
}
'''

    LINEPT_SHADER_FRAG = '''
#version 330

in vec4 v_color;
layout(location = 0) out vec4 o_diffuse;

void main() {
    o_diffuse = v_color;
}
'''


    def __init__(self):
        self.mvp_matrix = None

        GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)

        self._setup_programs()
        self._setup_vertex_buffers()

    def _setup_programs(self):
        self._linept_program = shaders.compileProgram(
            shaders.compileShader(self.LINEPT_SHADER_VERT, GL.GL_VERTEX_SHADER),
            shaders.compileShader(self.LINEPT_SHADER_FRAG, GL.GL_FRAGMENT_SHADER),
            validate=False, #HACK
        )

        line_program_uniforms = ['u_mvp_matrix']
        self._linept_program_uniform_locations = {
            name: GL.glGetUniformLocation(self._linept_program, name) for name in line_program_uniforms
        }

    def _setup_vertex_buffers(self):
        self._linept_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self._linept_vao)

        self._line_vbuf = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._line_vbuf)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,
                        dd.VERTEX_BUFFER_SIZE * sizeof(dd.VertexRecord),
                        None,
                        GL.GL_STREAM_DRAW)


        # could use glGetAttribLocation on the program once that's working

        offset = 0

        GL.glEnableVertexAttribArray(0); # vec3 i_pos
        GL.glVertexAttribPointer(
            0,                              # index
            3,                              # size
            GL.GL_FLOAT,                    # type
            GL.GL_FALSE,                    # normalized
            sizeof(dd.VertexRecord), # stride
            c_void_p(offset),        # offset
        )
        offset += sizeof(c_float) * 3

        GL.glEnableVertexAttribArray(1); # vec3 i_color
        GL.glVertexAttribPointer(
            1,                              # index
            3,                              # size
            GL.GL_FLOAT,                    # type
            GL.GL_FALSE,                    # normalized
            sizeof(dd.VertexRecord), # stride
            c_void_p(offset),        # offset
        )
        offset += sizeof(c_float) * 3

        GL.glEnableVertexAttribArray(2) # float point_size
        GL.glVertexAttribPointer(
            2,                              # index
            1,                              # size
            GL.GL_FLOAT,                    # type
            GL.GL_FALSE,                    # normalized
            sizeof(dd.VertexRecord), # stride
            c_void_p(offset),        # offset
        )

        # clean up..
        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    ###

    def begin_draw(self): ...
    def end_draw(self): ...

    def draw_lines(self, vtxbuffer: dd.VertexBuffer[dd.VertexRecord]):
        # remember! glDrawArrays (and our) count is the number of vertices consumed to render,
        # *not* the number of primitives.

        GL.glBindVertexArray(self._linept_vao)
        GL.glUseProgram(self._linept_program)

        assert self.mvp_matrix is not None
        GL.glUniformMatrix4fv(
            self._linept_program_uniform_locations['u_mvp_matrix'],
            1, # count
            GL.GL_TRUE, # transpose
            self.mvp_matrix
        )

        GL.glEnable(GL.GL_DEPTH_TEST)

        # upload data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._line_vbuf)
        GL.glBufferSubData(
            GL.GL_ARRAY_BUFFER,
            0, # offset
            vtxbuffer.used * sizeof(dd.VertexRecord), # size
            vtxbuffer.buffer # *data
        )

        # draw :3
        GL.glDrawArrays(GL.GL_LINES, 0, vtxbuffer.used)

        # cleanup
        GL.glUseProgram(0)
        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def draw_points(self, vtxbuffer: dd.VertexBuffer[dd.VertexRecord]):
        GL.glBindVertexArray(self._linept_vao)
        GL.glUseProgram(self._linept_program)

        assert self.mvp_matrix is not None
        GL.glUniformMatrix4fv(
            self._linept_program_uniform_locations['u_mvp_matrix'],
            1, # count
            GL.GL_TRUE, # transpose
            self.mvp_matrix
        )

        GL.glEnable(GL.GL_DEPTH_TEST)

        # upload data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._line_vbuf)
        GL.glBufferSubData(
            GL.GL_ARRAY_BUFFER,
            0, # offset
            vtxbuffer.used * sizeof(dd.VertexRecord), # size
            vtxbuffer.buffer # *data
        )

        # draw :3
        GL.glDrawArrays(GL.GL_POINTS, 0, vtxbuffer.used)

        # cleanup
        GL.glUseProgram(0)
        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
