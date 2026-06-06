import png
import slangpy as spy
import numpy as np
from pathlib import Path

class TextureNaive:
    def __init__(self):
        self.texture = None
        self.width = 0
        self.height = 0

    def load_from_file(
            self, 
            device : spy.Device, 
            file_path : Path
    ):
        if not file_path.exists():
            raise 'you specified wrong path to file!'
            return
        
        if device is None:
            raise 'device is None! Expected a valid device instance here'
            return
        
        reader = png.Reader(filename=file_path)

        width,height,rows,info = reader.asRGBA8()

        self.texture = device.create_texture(
            type=spy.TextureType.texture_2d,
            format=spy.Format.rgba8_unorm,
            width=width,
            height=height,
            usage=spy.TextureUsage.shader_resource
        )


        img_array = np.vstack(list(rows)).astype(np.uint8)

        # 4. Reshape to 3D array (height, width, channels) if it is a color/RGBA image
        channels = info['planes']
        if channels > 1:
            img_array = img_array.reshape((height, width, channels))
        else:
            img_array = img_array.reshape((height, width))

        self.texture.copy_from_numpy(img_array)

        self.width = width
        self.height = height
        
