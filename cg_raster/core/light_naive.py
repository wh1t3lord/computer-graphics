import slangpy as spy
import numpy as np

class LightAmbientNaive:
    def __init__(self):
        self.color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.intensity = 1.0
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32) 

class LightAmbientBlinnPhong:
    def __init__(self):
        self.intensity_ambient = np.array([0.2, 0.2, 0.2], dtype=np.float32)
        self.intensity_diffuse = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.intensity_specular = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)

class LightDirectionalBlinnPhong:
    def __init__(self):
        self.intensity_ambient = np.array([0.2, 0.2, 0.2], dtype=np.float32)
        self.intensity_diffuse = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.intensity_specular = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.direction = np.array([0.0, 0.0, 0.0], dtype=np.float32)

class LightPointBlinnPhong:
    def __init__(self):
        self.intensity_ambient = np.array([0.2, 0.2, 0.2], dtype=np.float32)
        self.intensity_diffuse = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.intensity_specular = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        self.constant = 1.0
        self.linear = 0.09
        self.quadratic = 0.032