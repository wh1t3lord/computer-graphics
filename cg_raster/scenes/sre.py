# Author: wh1t3lord

import core

import slangpy as spy
from pathlib import Path

class SceneRasterEmpty(core.IScene):
    def __init__(self):
        pass

    def _init(
            self,
            device : spy.Device, 
            window : spy.Window,
            ui : spy.ui.Context,
            ui_main_window : spy.ui.Window,
            shaders_path : Path
        ):
        print(f'{self.__class__.__name__}: init called')

        self.device = device
        self.ui = ui
        if self.device:
            if window:
                self.swapchain = self.device.create_surface(window)
                self.swapchain.configure(width=window.width,height=window.height)
        
        self.clear_color : spy.float3 = [0,1,0]
        self.ui_main_window = ui_main_window
        if self.ui and ui_main_window:
            
            self.ui_text = spy.ui.Text(ui_main_window, '\tSimple and start point of experimenting with slangpy!\n\tThis sample demonstrates how "clear render target" function works.')

            self.ui_clear_color_slider = spy.ui.DragFloat3(
                ui_main_window, 
                'clear color', 
                self.clear_color,
                lambda value: setattr(self, 'clear_color', value),
                0.001,
                0.0,
                1.0
            )


    def _update(
            self,
            dt : spy.math.float1
        ):
        pass

    def _render(
            self
        ):
        if self.device and self.swapchain:
            command_encoder : spy.CommandEncoder = self.device.create_command_encoder()
            texture_surface : spy.Texture = self.swapchain.acquire_next_image()

            if not texture_surface:
                return
            
            command_encoder.clear_texture_float(texture_surface, clear_value=spy.float4(self.clear_color, 1.0))

            self.ui.new_frame(texture_surface.width, texture_surface.height)
            self.ui.render(texture=texture_surface, command_encoder=command_encoder)
            self.device.submit_command_buffer(command_encoder.finish())
            del texture_surface

            self.swapchain.present()

    def _shutdown(
            self
        ):
        if self.device:
           self.device.wait()
           self.swapchain.unconfigure()
           del self.swapchain

        if self.ui_main_window:
            self.ui_main_window.remove_child(self.ui_clear_color_slider)
            self.ui_main_window.remove_child(self.ui_text)

        print(f'{self.__class__.__name__}: resources are destroyed!')


    def _on_resize(
            self,
            width : int,
            height : int
        ):
        if self.device:
            self.device.wait()

        if width > 0 and height > 0:
            self.swapchain.configure(width=width,height=height)
        else:
            self.swapchain.unconfigure()

    def _on_mouse_event(
            self,
            event : spy.MouseEvent
        ):
        pass

    def _on_keyboard_event(
            self,
            event : spy.KeyboardEvent
    ):
        pass