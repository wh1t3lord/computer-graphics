import slangpy as spy
import numpy as np
import core.input

# Euler based camera
class Camera:
    def __init__(
            self, 
            input : core.input.Input
    ):
        self.fov : np.float32 = 55.0
        self.pitch : np.float32 = 0.0
        self.yaw : np.float32 = 0.0

        self.pitch_limit_up : np.float32 = spy.math.radians(89.0)
        self.pitch_limit_down : np.float32 = spy.math.radians(-89.0)

        self.mView = np.identity(4, dtype=np.float32)
        self.mView[3, 3] = 1.0
        self.mView[0, 3] = 0.0
        self.mView[1, 3] = 0.0
        self.mView[2, 3] = 0.0

        self.vPosition = np.array([0.0,0.0,0.0], dtype=np.float32)

        self.binding_movement_forward = input.get_binding_state(core.input.eInputBindingsType.kMoveForward)
        self.binding_movement_backward = input.get_binding_state(core.input.eInputBindingsType.kMoveBackward)
        self.binding_movement_right = input.get_binding_state(core.input.eInputBindingsType.kMoveRight)
        self.binding_movement_left = input.get_binding_state(core.input.eInputBindingsType.kMoveLeft)

        self.binding_cam_pitch = input.get_binding_state(core.input.eInputBindingsType.kCamLookPitch)
        self.binding_cam_yaw = input.get_binding_state(core.input.eInputBindingsType.kCamLookYaw)

        self.camera_speed = 1.0
        self.can_update_input = True

        self.print_current_data()


    def update(
            self,
            dt : spy.math.float1
    ):
        if self.binding_cam_pitch and self.can_update_input == True:
            if self.binding_cam_pitch.state == core.input.eInputEventState.kMoving:
                self.pitch += self.binding_cam_pitch.value * dt
                pass

        if self.binding_cam_yaw and self.can_update_input == True:
            if self.binding_cam_yaw.state == core.input.eInputEventState.kMoving:
                self.yaw -= self.binding_cam_yaw.value * dt
                pass

        self.vFront = self.mView[2]

        self.vFront[0] = spy.math.sin(spy.math.radians(self.yaw)) * spy.math.cos(spy.math.radians(self.pitch))
        self.vFront[1] = spy.math.sin(spy.math.radians(self.pitch))
        self.vFront[2] = spy.math.cos(spy.math.radians(self.yaw)) * -spy.math.cos(spy.math.radians(self.pitch))

        self.vFront[:3] = self.vFront[:3] / np.linalg.norm(self.vFront[:3])

        self.mView[0][:3] = np.cross(self.vFront[:3], np.array([0.0, 1.0, 0.0], dtype=np.float32))
        self.mView[0][:3] = self.mView[0][:3] / np.linalg.norm(self.mView[0][:3])
        self.mView[1][:3] = np.cross(self.mView[0][:3], self.vFront[:3])
        self.mView[1][:3] = self.mView[1][:3] / np.linalg.norm(self.mView[1][:3])

        # be careful almost all variables in python is references so when we change -self.vFront we don't get a copy like we would like to get in languages in C++
        # but it changes self.mView[2] content and thus self.vFront is changed!!
        # so we would like to use front here and then negate then negate and calculate translation component
        self.mView[3, 0] = -np.dot(self.mView[0][:3], self.vPosition)
        self.mView[3, 1] = -np.dot(self.mView[1][:3], self.vPosition)
        self.mView[3, 2] = -np.dot(self.vFront[:3], self.vPosition)

        # we want to keep position of object if we change .z component when orientation of view and model matrix are idenitites then
        # -z = moves forward (from us like deep into screen)
        # +z = moves backward (to us like being behind camera)
        self.mView[2] = -self.vFront



        if self.binding_movement_forward and self.can_update_input == True:
            if self.binding_movement_forward.state == core.input.eInputEventState.kHolding:
                self.vPosition += self.vFront[:3] * dt * self.camera_speed

        if self.binding_movement_backward and self.can_update_input == True:
            if self.binding_movement_backward.state == core.input.eInputEventState.kHolding:
                self.vPosition -= self.vFront[:3] * dt * self.camera_speed

        if self.binding_movement_right and self.can_update_input == True:
            if self.binding_movement_right.state == core.input.eInputEventState.kHolding:
                self.vPosition += self.mView[0][:3] * dt * self.camera_speed

        if self.binding_movement_left and self.can_update_input == True:
            if self.binding_movement_left.state == core.input.eInputEventState.kHolding:
                self.vPosition -= self.mView[0][:3] * dt * self.camera_speed


    def print_current_data(self):
        print(f'camera: \n\tfov={self.fov} pitch={self.pitch} yaw={self.yaw}')



# Quaternion based camera   
class CameraQuat:
    def __init__(self):
        pass

