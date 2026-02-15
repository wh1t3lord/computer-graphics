import core
import random
import slangpy as spy
from pathlib import Path
import numpy as np

class SceneRasterTriangleCamera(core.IScene):
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

        if self.device:
            shader_name = shaders_path / 'raster_triangle' / '2d_color.slang'
            self.program = self.device.load_program(str(shader_name), ['mainVertex', 'mainPixel'])
            input_layout = self.device.create_input_layout(
                input_elements=[
                    {
                        "semantic_name": "POSITION",
                        "semantic_index": 0,
                        "format": spy.Format.rg32_float,
                    }
                ],
                vertex_streams=[{"stride": 8}],
            )

            self.pipeline = self.device.create_render_pipeline(
                program=self.program,
                input_layout=input_layout,
                targets=[{"format": spy.Format.rgba32_float}]
            )

            vertices = np.array(
                [-1, -1, 1, -1, 0, 1], 
                dtype=np.float32
            )

            indices = np.array(
                [0, 1, 2], 
                dtype=np.uint32
            )

            self.shader_data_triangle_color = np.array([1,1,1], dtype=np.float32)

            self.vertex_buffer = device.create_buffer(
                usage=spy.BufferUsage.vertex_buffer,
                label="vertex_buffer",
                data=vertices,
            )

            self.index_buffer = device.create_buffer(
                usage=spy.BufferUsage.index_buffer,
                label="index_buffer",
                data=indices,
            )

            # let's create our camera based on euler rotations
            self.camera = core.Camera()
            self.input = core.Input()

            if window:
                self.swapchain = self.device.create_surface(window)
                self.swapchain.configure(width=window.width,height=window.height)

                self.ui = ui

                if ui_main_window:
                    self.ui_shader_data_triangle_color = spy.ui.DragFloat3(
                        ui_main_window,
                        'triangle color',
                        self.shader_data_triangle_color,
                        lambda value: setattr(self, 'shader_data_triangle_color', value),
                        0.01,
                        0.0,
                        1.0
                    )

                    self.ui_main_window = ui_main_window



    def _update(
            self
        ):
        if self.input:
            self.input.update()

        if self.camera:
            self.camera.update()

    def _render(
            self
        ):
        if self.device and self.swapchain:
            command_encoder : spy.CommandEncoder = self.device.create_command_encoder()
            texture_surface : spy.Texture = self.swapchain.acquire_next_image()

            if not texture_surface:
                return
            
            # drawing our triangle

            render_target_view = texture_surface.create_view({})
            command_encoder.clear_texture_float(texture_surface, clear_value=[0,0,0,1])
                
            with command_encoder.begin_render_pass(
                {
                    "color_attachments": [
                        {"view": render_target_view}
                    ]
                }) as rp:
                shader_object = rp.bind_pipeline(self.pipeline)
                cursor = spy.ShaderCursor(shader_object)
                cursor.g_TriangleColor = self.shader_data_triangle_color

                rp.set_render_state(
                        {
                            "viewports": [spy.Viewport.from_size(texture_surface.width, texture_surface.height)],
                            "scissor_rects": [
                                spy.ScissorRect.from_size(texture_surface.width, texture_surface.height)
                            ],
                            "vertex_buffers": [self.vertex_buffer],
                            "index_buffer": self.index_buffer,
                            "index_format": spy.IndexFormat.uint32,
                        }
                    )
                rp.draw({"vertex_count": 3})

            # end of drawing our triangle

            if self.ui:
                self.ui.new_frame(width=texture_surface.width, height=texture_surface.height)
                self.ui.render(texture=texture_surface, command_encoder=command_encoder)

            self.device.submit_command_buffer(command_encoder.finish())
            del texture_surface

            self.swapchain.present()

    def _shutdown(
            self
        ):
       # we should destroy our resources
       if self.device:
           # sync point between GPU execution (wait until all operations on GPU is completed and we are ready to proceed) and CPU
           self.device.wait()
           self.swapchain.unconfigure()

           del self.swapchain
           del self.vertex_buffer
           del self.index_buffer

       if self.ui_main_window:
           self.ui_main_window.remove_child(self.ui_shader_data_triangle_color)

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
        if self.input:
            if event:
                self.input.update_mouse(event)

    def _on_keyboard_event(
            self,
            event : spy.KeyboardEvent
    ):
        if self.input:
            self.input.update_keyboard(event)
