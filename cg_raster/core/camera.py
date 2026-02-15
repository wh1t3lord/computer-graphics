import slangpy as spy

# Euler based camera
class Camera:
    def __init__(self):
        self.fov : spy.math.float1 = 55.0
        self.pitch : spy.math.float1 = 0.0
        self.yaw : spy.math.float1 = 0.0

        self.pitch_limit_up : spy.math.float1 = spy.math.radians(89.0)
        self.pitch_limit_down : spy.math.float1 = spy.math.radians(-89.0)

        self.orientation : spy.math.float4x4 = spy.math.float4x4()

        self.radian_step = 0.01

        self.print_current_data()


    def update(
            self,
            dt : spy.math.float1
    ):
        pass

    def print_current_data(self):
        print(f'camera: \n\tfov={self.fov} pitch={self.pitch} yaw={self.yaw}')



# Quaternion based camera   
class CameraQuat:
    def __init__(self):
        pass

