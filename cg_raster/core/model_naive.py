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

        self.vPosition = np.zeros(3, dtype=np.float32)
        self.vRotation = np.zeros(3, dtype=np.float32)
        self.vScale = np.array([1.0,1.0,1.0], dtype=np.float32)

    # simpler and plain version
    # but not optimized and not effective
    def apply_tsr_naive(
            self,
            translation,
            rotation,
            scale
    ):
        self.mModel = np.identity(4, dtype=np.float32)

        self.mModel = spy.math.translate(self.mModel, translation)
        self.mModel = spy.math.rotate(self.mModel, spy.math.radians(rotation[0]), np.array([1.0,0.0,0.0], dtype=np.float32))
        self.mModel = spy.math.rotate(self.mModel, spy.math.radians(rotation[1]), np.array([0.0,1.0,0.0], dtype=np.float32))
        self.mModel = spy.math.rotate(self.mModel, spy.math.radians(rotation[2]), np.array([0.0,0.0,1.0], dtype=np.float32))
        self.mModel = spy.math.scale(self.mModel, scale)

    def apply_tsr(self, translation, rotation, scale):
        self.mModel = np.identity(4, dtype=np.float32)
        self.mModel = spy.math.translate(self.mModel, translation)
        
        # Clamp X to avoid gimbal lock at X=90°
        # With extrinsic Y-X-Z order, lock happens when X=90°
        rotation[0] = np.clip(rotation[0], -89.0, 89.0)
        
        # Order: Y first, X second, Z last (Y-X-Z)
        # This moves lock from Y=90° (common) to X=90° (rare)
        self.mModel = spy.math.rotate(self.mModel, spy.math.radians(rotation[1]), np.array([0.0,1.0,0.0], dtype=np.float32))  # Y
        self.mModel = spy.math.rotate(self.mModel, spy.math.radians(rotation[0]), np.array([1.0,0.0,0.0], dtype=np.float32))  # X
        self.mModel = spy.math.rotate(self.mModel, spy.math.radians(rotation[2]), np.array([0.0,0.0,1.0], dtype=np.float32))  # Z
        
        self.mModel = spy.math.scale(self.mModel, scale)

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

def model_get_box_vertices_with_override_color_attrb(color):

    c_front  = [1, 0, 0]   # RED
    c_back   = [0, 1, 0]   # GREEN
    c_right  = [1, 1, 0]   # YELLOW
    c_left   = [0, 0, 1]   # BLUE
    c_top    = [1, 1, 1]   # WHITE
    c_bottom = [1, 0, 1]   # MAGENTA

    if color is not None:
        c_front  = color
        c_back   = color
        c_right  = color
        c_left   = color
        c_top    = color
        c_bottom = color

    vertices = np.array(
        [
            # Front face (z = -1) — RED
            -1, -1, -1,  c_front[0], c_front[1], c_front[2],   # 0
             1, -1, -1,  c_front[0], c_front[1], c_front[2],   # 1
             1,  1, -1,  c_front[0], c_front[1], c_front[2],   # 2
            -1,  1, -1,  c_front[0], c_front[1], c_front[2],   # 3

            # Back face (z = 1) — GREEN
             1, -1,  1,  c_back[0], c_back[1], c_back[2],   # 4
            -1, -1,  1,  c_back[0], c_back[1], c_back[2],   # 5
            -1,  1,  1,  c_back[0], c_back[1], c_back[2],   # 6
             1,  1,  1,  c_back[0], c_back[1], c_back[2],   # 7

            # Right face (x = 1) — YELLOW
             1, -1, -1,  c_right[0], c_right[1], c_right[2],   # 8
             1, -1,  1,  c_right[0], c_right[1], c_right[2],   # 9
             1,  1,  1,  c_right[0], c_right[1], c_right[2],   # 10
             1,  1, -1,  c_right[0], c_right[1], c_right[2],   # 11

            # Left face (x = -1) — BLUE
            -1, -1,  1,  c_left[0], c_left[1], c_left[2],   # 12
            -1, -1, -1,  c_left[0], c_left[1], c_left[2],   # 13
            -1,  1, -1,  c_left[0], c_left[1], c_left[2],   # 14
            -1,  1,  1,  c_left[0], c_left[1], c_left[2],   # 15

            # Top face (y = 1) — WHITE
            -1,  1, -1,  c_top[0], c_top[1], c_top[2],   # 16
             1,  1, -1,  c_top[0], c_top[1], c_top[2],   # 17
             1,  1,  1,  c_top[0], c_top[1], c_top[2],   # 18
            -1,  1,  1,  c_top[0], c_top[1], c_top[2],   # 19

            # Bottom face (y = -1) — MAGENTA
            -1, -1,  1,  c_bottom[0], c_bottom[1], c_bottom[2],   # 20
             1, -1,  1,  c_bottom[0], c_bottom[1], c_bottom[2],   # 21
             1, -1, -1,  c_bottom[0], c_bottom[1], c_bottom[2],   # 22
            -1, -1, -1,  c_bottom[0], c_bottom[1], c_bottom[2],   # 23
        ],
        dtype=np.float32
    )

    return vertices


def model_get_box_vertices_with_color_uv_attrb():
    vertices = np.array(
        [
            # Front face (z = -1) — RED
            -1, -1, -1,  1, 0, 0,  0, 1,   # 0
             1, -1, -1,  1, 0, 0,  1, 1,   # 1
             1,  1, -1,  1, 0, 0,  1, 0,   # 2
            -1,  1, -1,  1, 0, 0,  0, 0,   # 3

            # Back face (z = 1) — GREEN
             1, -1,  1,  0, 1, 0,  0, 1,   # 4
            -1, -1,  1,  0, 1, 0,  1, 1,   # 5
            -1,  1,  1,  0, 1, 0,  1, 0,   # 6
             1,  1,  1,  0, 1, 0,  0, 0,   # 7

            # Right face (x = 1) — YELLOW
             1, -1, -1,  1, 1, 0,  0, 1,   # 8
             1, -1,  1,  1, 1, 0,  1, 1,   # 9
             1,  1,  1,  1, 1, 0,  1, 0,   # 10
             1,  1, -1,  1, 1, 0,  0, 0,   # 11

            # Left face (x = -1) — BLUE
            -1, -1,  1,  0, 0, 1,  0, 1,   # 12
            -1, -1, -1,  0, 0, 1,  1, 1,   # 13
            -1,  1, -1,  0, 0, 1,  1, 0,   # 14
            -1,  1,  1,  0, 0, 1,  0, 0,   # 15

            # Top face (y = 1) — WHITE
            -1,  1, -1,  1, 1, 1,  0, 1,   # 16
             1,  1, -1,  1, 1, 1,  1, 1,   # 17
             1,  1,  1,  1, 1, 1,  1, 0,   # 18
            -1,  1,  1,  1, 1, 1,  0, 0,   # 19

            # Bottom face (y = -1) — MAGENTA
            -1, -1,  1,  1, 0, 1,  0, 1,   # 20
             1, -1,  1,  1, 0, 1,  1, 1,   # 21
             1, -1, -1,  1, 0, 1,  1, 0,   # 22
            -1, -1, -1,  1, 0, 1,  0, 0,   # 23
        ],
        dtype=np.float32
    )

    return vertices

def model_get_box_vertices_with_color_normal_uv_attrb():
    vertices = np.array(
        [
            # Front face (z = -1) — RED, normal = [0, 0, -1]
            -1, -1, -1,  1, 0, 0,  0, 0, -1,  0, 1,   # 0
             1, -1, -1,  1, 0, 0,  0, 0, -1,  1, 1,   # 1
             1,  1, -1,  1, 0, 0,  0, 0, -1,  1, 0,   # 2
            -1,  1, -1,  1, 0, 0,  0, 0, -1,  0, 0,   # 3

            # Back face (z = 1) — GREEN, normal = [0, 0, 1]
             1, -1,  1,  0, 1, 0,  0, 0, 1,  0, 1,   # 4
            -1, -1,  1,  0, 1, 0,  0, 0, 1,  1, 1,   # 5
            -1,  1,  1,  0, 1, 0,  0, 0, 1,  1, 0,   # 6
             1,  1,  1,  0, 1, 0,  0, 0, 1,  0, 0,   # 7

            # Right face (x = 1) — YELLOW, normal = [1, 0, 0]
             1, -1, -1,  1, 1, 0,  1, 0, 0,  0, 1,   # 8
             1, -1,  1,  1, 1, 0,  1, 0, 0,  1, 1,   # 9
             1,  1,  1,  1, 1, 0,  1, 0, 0,  1, 0,   # 10
             1,  1, -1,  1, 1, 0,  1, 0, 0,  0, 0,   # 11

            # Left face (x = -1) — BLUE, normal = [-1, 0, 0]
            -1, -1,  1,  0, 0, 1,  -1, 0, 0,  0, 1,   # 12
            -1, -1, -1,  0, 0, 1,  -1, 0, 0,  1, 1,   # 13
            -1,  1, -1,  0, 0, 1,  -1, 0, 0,  1, 0,   # 14
            -1,  1,  1,  0, 0, 1,  -1, 0, 0,  0, 0,   # 15

            # Top face (y = 1) — WHITE, normal = [0, 1, 0]
            -1,  1, -1,  1, 1, 1,  0, 1, 0,  0, 1,   # 16
             1,  1, -1,  1, 1, 1,  0, 1, 0,  1, 1,   # 17
             1,  1,  1,  1, 1, 1,  0, 1, 0,  1, 0,   # 18
            -1,  1,  1,  1, 1, 1,  0, 1, 0,  0, 0,   # 19

            # Bottom face (y = -1) — MAGENTA, normal = [0, -1, 0]
            -1, -1,  1,  1, 0, 1,  0, -1, 0,  0, 1,   # 20
             1, -1,  1,  1, 0, 1,  0, -1, 0,  1, 1,   # 21
             1, -1, -1,  1, 0, 1,  0, -1, 0,  1, 0,   # 22
            -1, -1, -1,  1, 0, 1,  0, -1, 0,  0, 0,   # 23
        ],
        dtype=np.float32
    )

    return vertices

def model_get_sphere_vertices_with_color_normal_uv_attrb(radius=1.0, stacks=16, slices=16):
    """
    Generate a UV sphere with per-vertex position, color, normal, and UV attributes.
    
    Vertex layout (11 floats per vertex):
        px, py, pz,  r, g, b,  nx, ny, nz,  u, v
    
    Parameters
    ----------
    radius : float
        Sphere radius.
    stacks : int
        Number of latitude divisions (>= 2).
    slices : int
        Number of longitude divisions (>= 3).
    
    Returns
    -------
    np.ndarray
        Flat float32 array of shape ((stacks+1)*(slices+1)*11,).
    """
    num_vertices = (stacks + 1) * (slices + 1)
    vertices = np.zeros(num_vertices * 11, dtype=np.float32)
    
    vidx = 0
    for i in range(stacks + 1):
        phi = np.pi * i / stacks          # 0 = north pole, pi = south pole
        for j in range(slices + 1):
            theta = 2.0 * np.pi * j / slices  # 0 .. 2pi
            
            # Position (y-up)
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.cos(phi)
            z = radius * np.sin(phi) * np.sin(theta)
            
            # Normal = normalized position (automatically correct for sphere)
            nx = np.sin(phi) * np.cos(theta)
            ny = np.cos(phi)
            nz = np.sin(phi) * np.sin(theta)
            
            # Color — white by default.
            # Swap the two lines below for normal-based RGB coloring:
            # r, g, b = (nx + 1.0) * 0.5, (ny + 1.0) * 0.5, (nz + 1.0) * 0.5
            r, g, b = 1.0, 1.0, 1.0
            
            # UV
            u = j / slices
            v = i / stacks
            
            vertices[vidx:vidx + 11] = [x, y, z, r, g, b, nx, ny, nz, u, v]
            vidx += 11
    
    return vertices


def model_get_sphere_indices(stacks=16, slices=16):
    """
    Generate triangle indices for the UV sphere.
    
    Winding is CCW when viewed from outside. Call with the same
    stacks/slices values used for the vertex function.
    
    Parameters
    ----------
    stacks : int
        Number of latitude divisions.
    slices : int
        Number of longitude divisions.
    
    Returns
    -------
    np.ndarray
        Flat uint32 array of triangle indices.
    """
    indices = []
    for i in range(stacks):
        for j in range(slices):
            a = i * (slices + 1) + j
            b = (i + 1) * (slices + 1) + j
            c = i * (slices + 1) + (j + 1)
            d = (i + 1) * (slices + 1) + (j + 1)
            
            # Two CCW triangles per quad
            indices.extend([a, c, b])
            indices.extend([c, d, b])
    
    return np.array(indices, dtype=np.uint32)