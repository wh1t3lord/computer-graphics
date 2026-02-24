from enum import Enum

class RenderingType(Enum):
    FORWARD = 0
    DEFERRED = 1

class Settings:
    def __init__(self):
        self.enable_renderdoc_capture = False


g_Settings = Settings()