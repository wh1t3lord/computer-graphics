import core

import slangpy as spy
from pathlib import Path

class DebugGridPass:
    def __init__(self):
        pass

    def init(
            self,
            device : spy.Device,
            shader_folder_path : Path,
            textures_path : Path,
            models_path : Path
    ):
        pass

    def shutdown(
            self      
    ):
        pass

    def update(
      self,
      device : spy.Device      
    ):
        pass

    def render(
            self, 
            device : spy.Device,
            ce : spy.CommandEncoder
    ):
        pass