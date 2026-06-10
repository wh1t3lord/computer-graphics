import slangpy as spy
import numpy as np

class LightAmbientNaive:
    def __init__(self):
        self.color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.intensity = 1.0

    def get_color(self):
        return self.color

