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

        self.vPosition = self.mModel[3]

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
        indicies
    ):
        if device is None:
            return False
        
        self.vertex_size = vertices.itemsize * vertices.shape[0]
        self.vertex_count = vertices.shape[0]
        self.index_count = indicies.shape[0]

        if self.buffer_vertex is None:
            self.buffer_vertex = device.create_buffer(
                usage=spy.BufferUsage.vertex_buffer,
                label="model_vertex_buffer",
                data=vertices,
            )

        if self.buffer_index is None:
            self.buffer_index = device.create_buffer(
                usage=spy.BufferUsage.index_buffer,
                label="model_index_buffer",
                data=indicies,
            )

        return True
    
def model_get_box_vertices_no_color_attrb():
    vertices = np.array(
        [
            -1, -1, -1,
             1, -1, -1,
             1,  1, -1,
            -1,  1, -1,
            -1, -1,  1,
             1, -1,  1,
             1,  1,  1,
            -1,  1,  1
        ], 
        dtype=np.float32
    )

    return vertices

def model_get_box_indicies_no_color_attrb():
    indicies = np.array(
        [
            0, 1, 2, 2, 3, 0,
            1, 5, 6, 6, 2, 1,
            5, 4, 7, 7, 6, 5,
            4, 0, 3, 3, 7, 4,
            3, 2, 6, 6, 7, 3,
            4, 5, 1, 1, 0, 4
        ], 
        dtype=np.uint32
    )

    return indicies