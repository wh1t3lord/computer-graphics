import slangpy as spy
import numpy as np
import configparser
from enum import Enum

class EventState(Enum):
    kPressed = 1
    kReleased = 2
    kHolding = 3
    kMoving = 4
    kNone = -1

# determine how we store data from input if absolute 
# it means we each frame set value to 0.0 
# otherwise we each frame add to current value without resetting it to 0.0
class AxisType(Enum):
    kAbsolute = 1,
    kRelative = 2,
    kNone = -1

class Input:
    def __init__(self):
        # defaults
        self.bindings = {
            "MOVE_FORWARD" : {
                'events': [spy.KeyCode.w],
                'value': 0.0,
                'axis_type': AxisType.kAbsolute,
                'state': EventState.kNone
            },
            "MOVE_BACKWARD" : {
                'events': [spy.KeyCode.s],
                'value': 0.0,
                'axis_type': AxisType.kAbsolute,
                'state': EventState.kNone
            },
            "MOVE_LEFT" : {
                'events': [spy.KeyCode.a],
                'value': 0.0,
                'axis_type': AxisType.kAbsolute,
                'state': EventState.kNone
            },
            "MOVE_RIGHT" : {
                'events': [spy.KeyCode.d],
                'value': 0.0,
                'axis_type': AxisType.kAbsolute,
                'state': EventState.kNone
            },
            'LOOK' : {
                'events': [spy.MouseEventType.move],
                'value': 0.0,
                'axis_type': AxisType.kAbsolute,
                'state': EventState.kNone
            }
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
                state['value'] = 0.0

    def load_bindings(self, configname : str):
        pass

    def save_bindings(self, configname : str):
        pass