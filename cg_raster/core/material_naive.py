import slangpy as spy
import numpy as np
import core.texture_naive as texture_naive
from pathlib import Path

class MaterialBlinnPhongColorBased:
    def __init__(self):
        self.color_ambient = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.color_diffuse = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.color_specular = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.specular_shininess = 32.0

class MaterialBlinnPhongTextureBased:
    def __init__(self):
        self.diffuse_texture_path : Path = ''
        self.specular_texture_path : Path = ''
        self.texture_diffuse : spy.Texture = None
        self.texture_specular : spy.Texture = None
        self.color_specular = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.specular_shininess = 32.0

    def load_textures(
            self,
            device : spy.Device
    ):
        if self.diffuse_texture_path.exists():
            self.texture_diffuse = texture_naive.TextureNaive()
            self.texture_diffuse.load_from_file(device, self.diffuse_texture_path)
        else:
            raise ValueError('diffuse_texture_path is empty! Please specify a valid path to texture file!')

        if self.specular_texture_path.exists():
            self.texture_specular = texture_naive.TextureNaive()
            self.texture_specular.load_from_file(device, self.specular_texture_path)
        else:
            raise ValueError('specular_texture_path is empty! Please specify a valid path to texture file!')