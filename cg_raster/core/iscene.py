from enum import Enum
import slangpy as spy
from pathlib import Path

from core.settings import g_Settings

from pyRenderdocApp import load_render_doc

_g_render_doc = None
_g_render_doc_count = 0

def _press_button_renderdoc_capture():
    global _g_render_doc_count
    _g_render_doc_count+=1

class IScene:
    def __init__(self):
        global _g_render_doc
        global _g_render_doc_count
        self.ui_renderdoc_text=None

        if g_Settings.enable_renderdoc_capture:
            if _g_render_doc == None:
                _g_render_doc = load_render_doc()



    def init(
            self, 
            device : spy.Device, 
            window : spy.Window,
            ui : spy.ui.Context,
            ui_main_window : spy.ui.Window,
            shaders_path : Path
        ):
        self.ui_main_window = ui_main_window
        self.device = device

        assert(self.device)
        assert(self.ui_main_window)

        self._init(
            device, 
            window,
            ui,
            ui_main_window,
            shaders_path
        )

        self._init_renderdoc(ui_main_window=ui_main_window)

    def _init_renderdoc(
            self,
            ui_main_window : spy.ui.Window
    ):
        is_renderdoc_avail = spy.renderdoc.is_available()

        if g_Settings and ui_main_window and is_renderdoc_avail:
            if g_Settings.enable_renderdoc_capture == True:
                self.ui_renderdoc_text = spy.ui.Text(ui_main_window,f"\nRenderDoc - Enabled!\n\tSave directory -> [{_g_render_doc.get_capture_file_path_template()}]")

                


    def _shutdown_renderdoc(self):
        if self.ui_renderdoc_text and self.ui_main_window:
            self.ui_main_window.remove_child(self.ui_renderdoc_text)
            

    def update(
            self, 
            dt : spy.math.float1
    ):
        self._update(dt)

    def render(self):
        global _g_render_doc
        global _g_render_doc_count
        if _g_render_doc and _g_render_doc_count>0:
            _g_render_doc.start_frame_capture(None, None)

        self._render()

        if _g_render_doc and _g_render_doc_count>0:
            _g_render_doc.end_frame_capture(None, None)
            _g_render_doc_count -= 1

    def shutdown(self):
        self._shutdown_renderdoc()
        self._shutdown()

    def on_resize(
            self, 
            width : int, 
            height : int
        ):
        self._on_resize(width,height)

    def on_mouse_event(
            self,
            event : spy.MouseEvent
        ):
        self._on_mouse_event(event)

    def on_keyboard_event(
            self,
            event : spy.KeyboardEvent
        ):
        self._on_keyboard_event(event)