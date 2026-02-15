import slangpy as spy
import numpy as np

# Euler based camera
class Camera:
    def __init__(self):
        self.fov = 55.0
        self.pitch = 0.0
        self.yaw = 0.0

        self.print_current_data()


    def update(self):
        pass

    def print_current_data(self):
        print(f'camera: \n\tfov={self.fov}')



# Quaternion based camera   
class CameraQuat:
    def __init__(self):
        pass

