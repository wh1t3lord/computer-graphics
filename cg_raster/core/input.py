import slangpy as spy
import configparser
from dataclasses import dataclass
from enum import Enum, IntFlag, auto

class eEventState(Enum):
    kPressed = 1
    kReleased = 2
    kHolding = 3
    kMoving = 4
    kNone = -1

# determine how we store data from input if absolute 
# it means we each frame set value to 0.0 
# otherwise we each frame add to current value without resetting it to 0.0
class eAxisType(Enum):
    kAbsolute = 1,
    kRelative = 2,
    kNone = -1

class eDeviceType(IntFlag):
    kMouse = auto(),
    kKeyboard = auto(),
    kJoy = auto(),
    kNone = 0

@dataclass
class InputBindingState:
    events : list
    value : spy.math.float1
    value_prev : spy.math.float1
    axis_type : eAxisType
    device_type : eDeviceType
    state : eEventState

class eBindingsType(Enum):
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
            self.convert_bindings_to_str(eBindingsType.kMoveForward) : InputBindingState(
                events=[spy.KeyCode.w],
                value=0.0,
                value_prev=0.0,
                axis_type=eAxisType.kAbsolute,
                device_type=eDeviceType.kNone,
                state=eEventState.kNone
            ),
            self.convert_bindings_to_str(eBindingsType.kMoveBackward) : InputBindingState(
                events=[spy.KeyCode.s],
                value=0.0,
                value_prev=0.0,
                axis_type=eAxisType.kAbsolute,
                device_type=eDeviceType.kNone,
                state=eEventState.kNone
            ),
            self.convert_bindings_to_str(eBindingsType.kMoveLeft) : InputBindingState(
                events=[spy.KeyCode.a],
                value=0.0,
                value_prev=0.0,
                axis_type=eAxisType.kAbsolute,
                device_type=eDeviceType.kNone,
                state=eEventState.kNone
            ),
            self.convert_bindings_to_str(eBindingsType.kMoveRight) : InputBindingState(
                events=[spy.KeyCode.d],
                value=0.0,
                value_prev=0.0,
                axis_type=eAxisType.kAbsolute,
                device_type=eDeviceType.kNone,
                state=eEventState.kNone
            ),
            self.convert_bindings_to_str(eBindingsType.kCamLookPitch) : InputBindingState(
                events=[spy.MouseEventType.move],
                value=0.0,
                value_prev=0.0,
                axis_type=eAxisType.kAbsolute,
                device_type=eDeviceType.kNone,
                state=eEventState.kNone
            ),
            self.convert_bindings_to_str(eBindingsType.kCamLookYaw) : InputBindingState(
                events=[spy.MouseEventType.move],
                value=0.0,
                value_prev=0.0,
                axis_type=eAxisType.kAbsolute,
                device_type=eDeviceType.kNone,
                state=eEventState.kNone
            ),
        }

        self._init_bindings(self.bindings)

        for bind_name, state in self.bindings.items():
            assert state.device_type != eDeviceType.kNone, 'Failed to initialize your bindings due to incorrect device type deduction based on events fields'
    

    def _init_bindings(self, bindings):
        if bindings:
            for bind_name, state in bindings.items():
                if len(state.events) != 0:
                    for event in state.events:
                        if event:
                            if type(event) is spy.KeyCode:
                                state.device_type |= eDeviceType.kKeyboard

                            if type(event) is spy.MouseEventType:
                                state.device_type |= eDeviceType.kMouse

    def convert_bindings_to_str(self, binding_type : eBindingsType) -> str:
        match binding_type:
            case eBindingsType.kMoveForward:
                return 'MOVE_FORWARD'
            case eBindingsType.kMoveBackward:
                return 'MOVE_BACKWARD'
            case eBindingsType.kMoveLeft:
                return 'MOVE_LEFT'
            case eBindingsType.kMoveRight:
                return 'MOVE_RIGHT'
            case eBindingsType.kCamLookPitch:
                return 'CAM_LOOK_PITCH'
            case eBindingsType.kCamLookYaw:
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
            CONST_CAM_YAW = self.convert_bindings_to_str(eBindingsType.kCamLookYaw)

        if CONST_CAM_PITCH==None:
            CONST_CAM_PITCH = self.convert_bindings_to_str(eBindingsType.kCamLookPitch)

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
            binding_type : eBindingsType
    ) -> InputBindingState:
        if self.bindings:
            if self.bindings.get(self.convert_bindings_to_str(binding_type)):
                return self.bindings.get(self.convert_bindings_to_str(binding_type))
            
        return InputBindingState()

    def update(self):
        if self.bindings:
            for bind_name, state in self.bindings.items():
                if state.axis_type == eAxisType.kAbsolute:
                    state.value = 0.0

    def load_bindings(self, configname : str):
        pass

    def save_bindings(self, configname : str):
        pass