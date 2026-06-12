import slangpy as spy
import numpy as np

class MaterialBlinnPhong:
    def __init__(self):
        self.color_ambient = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.color_diffuse = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.color_specular = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.specular_shininess = 32.0