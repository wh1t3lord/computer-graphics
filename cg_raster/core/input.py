import slangpy as spy
import configparser
from dataclasses import dataclass
from enum import Enum

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

@dataclass
class InputElementState:
    events : list
    value : spy.math.float1
    axis_type : eAxisType
    state : eEventState



class Input:
    def __init__(self):
        # defaults
        self.bindings = {
            "MOVE_FORWARD" : InputElementState(
                events=[spy.KeyCode.w],
                value=0.0,
                axis_type=eAxisType.kAbsolute,
                state=eEventState.kNone
            ),
            "MOVE_BACKWARD" : InputElementState(
                events=[spy.KeyCode.s],
                value=0.0,
                axis_type=eAxisType.kAbsolute,
                state=eEventState.kNone
            ),
            "MOVE_LEFT" : InputElementState(
                events=[spy.KeyCode.a],
                value=0.0,
                axis_type=eAxisType.kAbsolute,
                state=eEventState.kNone
            ),
            "MOVE_RIGHT" : InputElementState(
                events=[spy.KeyCode.d],
                value=0.0,
                axis_type=eAxisType.kAbsolute,
                state=eEventState.kNone
            ),
            'LOOK' : InputElementState(
                events=[spy.MouseEventType.move],
                value=0.0,
                axis_type=eAxisType.kAbsolute,
                state=eEventState.kNone
            ),
        }
    
    def update_keyboard(
            self, 
            event : spy.KeyboardEvent
    ):
        if self.bindings:
            for bind_name, state in self.bindings.items():
                pass


    def update_mouse(
            self,
            event : spy.MouseEvent
    ):
        if self.bindings:
            for bind_name, state in self.bindings.items():
                pass

    def update(self):
        if self.bindings:
            for bind_name, state in self.bindings.items():
                state.value = 0.0

    def load_bindings(self, configname : str):
        pass

    def save_bindings(self, configname : str):
        pass