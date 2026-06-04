import slangpy as spy
import numpy as np

# trivial design of model
class ModelNaive:
    def __init__(self):
        self.buffer_vertex = None
        self.buffer_index = None
        self.vertex_size = 0
        self.vertex_count = 0
        self.index_count = 0

        self.mModel = np.identity(4, dtype=np.float32)
        self.mModel[0,3]=0.0
        self.mModel[1,3]=0.0
        self.mModel[2,3]=0.0
        self.mModel[3,3]=1.0

        self.vPosition = np.zeros(3, dtype=np.float32)

    def load_from_file(
        self,
        device : spy.Device,
        file
    ):
        pass

    def load_from_memory(
        self,
        device : spy.Device,
        vertices, 
        indicies,
        in_struct_size
    ):
        if device is None:
            return False
        
        self.vertex_size = vertices.itemsize * vertices.shape[0]
        self.vertex_count = vertices.shape[0] / in_struct_size
        self.index_count = indicies.shape[0]

        if self.buffer_vertex is None:
            self.buffer_vertex = device.create_buffer(
                usage=spy.BufferUsage.vertex_buffer,
                label="model_vertex_buffer",
                data=vertices,
                struct_size=in_struct_size,
                element_count=self.vertex_size//in_struct_size
            )

        if self.buffer_index is None:
            self.buffer_index = device.create_buffer(
                usage=spy.BufferUsage.index_buffer,
                label="model_index_buffer",
                data=indicies,
                struct_size=4,
                size=4*self.index_count
            )

        return True
    
def model_get_box_vertices_no_color_attrb():
    vertices = np.array(
        [
            # Front face (z = -1) 
            -1, -1, -1,
             1, -1, -1,
             1,  1, -1,
            -1,  1, -1,

            # Back face (z = 1) 
             1, -1,  1,
            -1, -1,  1,
            -1,  1,  1,
             1,  1,  1,

            # Right face (x = 1) 
             1, -1, -1,
             1, -1,  1,
             1,  1,  1,
             1,  1, -1,

            # Left face (x = -1)  
            -1, -1,  1,
            -1, -1, -1,
            -1,  1, -1,
            -1,  1,  1,

            # Top face (y = 1) 
            -1,  1, -1,
             1,  1, -1,
             1,  1,  1,
            -1,  1,  1,

            # Bottom face (y = -1)  
            -1, -1,  1, 
             1, -1,  1, 
             1, -1, -1, 
            -1, -1, -1, 
        ], 
        dtype=np.float32
    )

    return vertices

def model_get_box_indicies():
    indicies = np.array(
        [
            # Front (red)      # Back (green)
            0, 2, 1, 2, 0, 3,  4, 6, 5, 6, 4, 7,
            # Right (yellow)   # Left (blue)
            8, 10, 9, 10, 8, 11,  12, 14, 13, 14, 12, 15,
            # Top (white)      # Bottom (magenta)
            16, 18, 17, 18, 16, 19,  20, 22, 21, 22, 20, 23,
        ],
        dtype=np.uint32
    )

    return indicies
def model_get_box_vertices_with_color_attrb():
    vertices = np.array(
        [
            # Front face (z = -1) — RED
            -1, -1, -1,  1, 0, 0,   # 0
             1, -1, -1,  1, 0, 0,   # 1
             1,  1, -1,  1, 0, 0,   # 2
            -1,  1, -1,  1, 0, 0,   # 3

            # Back face (z = 1) — GREEN
             1, -1,  1,  0, 1, 0,   # 4
            -1, -1,  1,  0, 1, 0,   # 5
            -1,  1,  1,  0, 1, 0,   # 6
             1,  1,  1,  0, 1, 0,   # 7

            # Right face (x = 1) — YELLOW
             1, -1, -1,  1, 1, 0,   # 8
             1, -1,  1,  1, 1, 0,   # 9
             1,  1,  1,  1, 1, 0,   # 10
             1,  1, -1,  1, 1, 0,   # 11

            # Left face (x = -1) — BLUE
            -1, -1,  1,  0, 0, 1,   # 12
            -1, -1, -1,  0, 0, 1,   # 13
            -1,  1, -1,  0, 0, 1,   # 14
            -1,  1,  1,  0, 0, 1,   # 15

            # Top face (y = 1) — WHITE
            -1,  1, -1,  1, 1, 1,   # 16
             1,  1, -1,  1, 1, 1,   # 17
             1,  1,  1,  1, 1, 1,   # 18
            -1,  1,  1,  1, 1, 1,   # 19

            # Bottom face (y = -1) — MAGENTA
            -1, -1,  1,  1, 0, 1,   # 20
             1, -1,  1,  1, 0, 1,   # 21
             1, -1, -1,  1, 0, 1,   # 22
            -1, -1, -1,  1, 0, 1,   # 23
        ],
        dtype=np.float32
    )

    return vertices