import slangpy as spy
import configparser
from dataclasses import dataclass
from enum import Enum, IntFlag, auto

class eInputEventState(Enum):
    kPressed = 1
    kReleased = 2
    kHolding = 3
    kMoving = 4
    kNone = -1

# determine how we store data from input if absolute 
# it means we each frame set value to 0.0 
# otherwise we each frame add to current value without resetting it to 0.0
class eInputAxisType(Enum):
    kAbsolute = 1,
    kRelative = 2,
    kNone = -1

class eInputDeviceType(IntFlag):
    kMouse = auto(),
    kKeyboard = auto(),
    kJoy = auto(),
    kNone = 0

@dataclass
class InputBindingState:
    events : list
    value : spy.math.float1
    value_prev : spy.math.float1
    axis_type : eInputAxisType
    device_type : eInputDeviceType
    state : eInputEventState

class eInputBindingsType(Enum):
    kMoveForward=auto(),
    kMoveBackward=auto(),
    kMoveLeft=auto(),
    kMoveRight=auto(),
    kCamLookPitch=auto(),
    kCamLookYaw=auto()

CONST_CAM_YAW = None
CONST_CAM_PITCH = None

class Input:
    def __init__(self):
        # defaults
        self.bindings = {
            self.convert_bindings_to_str(eInputBindingsType.kMoveForward) : InputBindingState(
                events=[spy.KeyCode.w],
                value=0.0,
                value_prev=0.0,
                axis_type=eInputAxisType.kAbsolute,
                device_type=eInputDeviceType.kNone,
                state=eInputEventState.kNone
            ),
            self.convert_bindings_to_str(eInputBindingsType.kMoveBackward) : InputBindingState(
                events=[spy.KeyCode.s],
                value=0.0,
                value_prev=0.0,
                axis_type=eInputAxisType.kAbsolute,
                device_type=eInputDeviceType.kNone,
                state=eInputEventState.kNone
            ),
            self.convert_bindings_to_str(eInputBindingsType.kMoveLeft) : InputBindingState(
                events=[spy.KeyCode.a],
                value=0.0,
                value_prev=0.0,
                axis_type=eInputAxisType.kAbsolute,
                device_type=eInputDeviceType.kNone,
                state=eInputEventState.kNone
            ),
            self.convert_bindings_to_str(eInputBindingsType.kMoveRight) : InputBindingState(
                events=[spy.KeyCode.d],
                value=0.0,
                value_prev=0.0,
                axis_type=eInputAxisType.kAbsolute,
                device_type=eInputDeviceType.kNone,
                state=eInputEventState.kNone
            ),
            self.convert_bindings_to_str(eInputBindingsType.kCamLookPitch) : InputBindingState(
                events=[spy.MouseEventType.move],
                value=0.0,
                value_prev=0.0,
                axis_type=eInputAxisType.kAbsolute,
                device_type=eInputDeviceType.kNone,
                state=eInputEventState.kNone
            ),
            self.convert_bindings_to_str(eInputBindingsType.kCamLookYaw) : InputBindingState(
                events=[spy.MouseEventType.move],
                value=0.0,
                value_prev=0.0,
                axis_type=eInputAxisType.kAbsolute,
                device_type=eInputDeviceType.kNone,
                state=eInputEventState.kNone
            ),
        }

        self._init_bindings(self.bindings)

        for bind_name, state in self.bindings.items():
            assert state.device_type != eInputDeviceType.kNone, 'Failed to initialize your bindings due to incorrect device type deduction based on events fields'
    

    def _init_bindings(self, bindings):
        if bindings:
            for bind_name, state in bindings.items():
                if len(state.events) != 0:
                    for event in state.events:
                        if event:
                            if type(event) is spy.KeyCode:
                                state.device_type |= eInputDeviceType.kKeyboard

                            if type(event) is spy.MouseEventType:
                                state.device_type |= eInputDeviceType.kMouse

    def convert_bindings_to_str(self, binding_type : eInputBindingsType) -> str:
        match binding_type:
            case eInputBindingsType.kMoveForward:
                return 'MOVE_FORWARD'
            case eInputBindingsType.kMoveBackward:
                return 'MOVE_BACKWARD'
            case eInputBindingsType.kMoveLeft:
                return 'MOVE_LEFT'
            case eInputBindingsType.kMoveRight:
                return 'MOVE_RIGHT'
            case eInputBindingsType.kCamLookPitch:
                return 'CAM_LOOK_PITCH'
            case eInputBindingsType.kCamLookYaw:
                return 'CAM_LOOK_YAW'
            case _:
                return 'BINDING_UNKNOWN'

    def update_keyboard(
            self, 
            event : spy.KeyboardEvent
    ):
        if self.bindings:
            for bind_name, state in self.bindings.items():
                if event.key in state.events and event.is_key_press():
                    state.value = 1.0

    # obviously there's lazy fat expernsive code and it should be optimized due to input being but, but... 
    # we program in python and generally it is only for demo so some little laziness might exist for fast 'iterationable' development
    def update_mouse(
            self,
            event : spy.MouseEvent
    ):
        global CONST_CAM_PITCH
        global CONST_CAM_YAW

        if CONST_CAM_YAW==None:
            CONST_CAM_YAW = self.convert_bindings_to_str(eInputBindingsType.kCamLookYaw)

        if CONST_CAM_PITCH==None:
            CONST_CAM_PITCH = self.convert_bindings_to_str(eInputBindingsType.kCamLookPitch)

        if self.bindings:
            for bind_name, state in self.bindings.items():
                if event.is_move() and spy.MouseEventType.move in state.events:
                    if bind_name == CONST_CAM_PITCH:
                        state.value = event.pos.y - state.value_prev
                        state.value_prev = event.pos.y
                    elif bind_name == CONST_CAM_YAW:
                        state.value = event.pos.x - state.value_prev
                        state.value_prev = event.pos.x

    def get_binding_state(
      self,
      binding_name : str      
    ) -> InputBindingState:
        if self.bindings:
            if self.bindings.get(binding_name):
                return self.bindings.get(binding_name)

        return InputBindingState()

    def get_binding_state(
            self,
            binding_type : eInputBindingsType
    ) -> InputBindingState:
        if self.bindings:
            if self.bindings.get(self.convert_bindings_to_str(binding_type)):
                return self.bindings.get(self.convert_bindings_to_str(binding_type))
            
        return InputBindingState()

    def update(self):
        if self.bindings:
            for bind_name, state in self.bindings.items():
                if state.axis_type == eInputAxisType.kAbsolute:
                    state.value = 0.0

    def load_bindings(self, configname : str):
        pass

    def save_bindings(self, configname : str):
        pass