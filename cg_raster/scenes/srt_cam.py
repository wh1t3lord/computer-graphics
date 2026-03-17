# Author: wh1t3lord

import core
import random
import slangpy as spy
from pathlib import Path
import numpy as np

class SceneRasterTriangleCamera(core.IScene):
    def __init__(self):
        super().__init__()
        self.ui_shader_data_triangle_color = None
        self.ui_shader_data_triangle_position = None

    def _init(
            self,
            device : spy.Device, 
            window : spy.Window,
            ui : spy.ui.Context,
            ui_main_window : spy.ui.Window,
            shaders_path : Path
        ):
        if ui_main_window != None and self.ui_shader_data_triangle_color != None and self.ui_shader_data_triangle_position != None:
            ui_main_window.add_child(self.ui_shader_data_triangle_color)
            ui_main_window.add_child(self.ui_shader_data_triangle_position)

        print(f'{self.__class__.__name__}: init called')

        self.device = device

        if self.device:
            shader_name = shaders_path / 'raster_triangle' / '2d_camera.slang'
            self.program = self.device.load_program(str(shader_name), ['mainVertex', 'mainPixel'])
            input_layout = self.device.create_input_layout(
                input_elements=[
                    {
                        "semantic_name": "POSITION",
                        "semantic_index": 0,
                        "format": spy.Format.rgb32_float,
                    }
                ],
                vertex_streams=[{"stride": 12}],
            )

            self.pipeline = self.device.create_render_pipeline(
                program=self.program,
                input_layout=input_layout,
                targets=[{"format": spy.Format.rgba32_float}]
            )

            vertices = np.array(
                [
                    -1, -1, 0, # bottom left
                    1, -1, 0,  # bottom right
                    0, 1, 0    # center top
                ], 
                dtype=np.float32
            )

            indices = np.array(
                [0, 1, 2], 
                dtype=np.uint32
            )

            self.shader_data_triangle_color = np.array([1,1,1], dtype=np.float32)
            self.vTrianglePosition = np.array([0,0,0], dtype=np.float32)
            self.mTriangleOrientation = np.identity(4, dtype=np.float32)
            self.mTriangleOrientation[0,3]=0.0
            self.mTriangleOrientation[1,3]=0.0
            self.mTriangleOrientation[2,3]=0.0
            self.mTriangleOrientation[3,3]=1.0

            self.mProjection : spy.math.float4x4 = spy.math.float4x4()

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


            self.input = core.Input()

            # let's create our camera based on euler rotations
            self.camera = core.Camera(self.input)

            self.binding_cam_pitch = self.input.get_binding_state(core.eInputBindingsType.kCamLookPitch)
            self.binding_cam_yaw = self.input.get_binding_state(core.eInputBindingsType.kCamLookYaw)

            if window != None:
                self.swapchain = self.device.create_surface(window)
                self.swapchain.configure(width=window.width,height=window.height)

                self.ui = ui
                self.window = window

            if ui_main_window != None and self.ui_shader_data_triangle_position == None and self.ui_shader_data_triangle_color == None:
                    self.ui_shader_data_triangle_color = spy.ui.DragFloat3(
                        ui_main_window,
                        'triangle color',
                        self.shader_data_triangle_color,
                        lambda value: setattr(self, 'shader_data_triangle_color', value),
                        0.01,
                        0.0,
                        1.0
                    )

                    self.ui_shader_data_triangle_position = spy.ui.DragFloat3(
                        ui_main_window,
                        'triangle position',
                        self.vTrianglePosition,
                        lambda value: setattr(self, 'vTrianglePosition', value),
                        0.01,
                        -100.0,
                        100.0
                    )

                    self.ui_main_window = ui_main_window



    def _update(
            self,
            dt : spy.math.float1
        ):
        if self.camera:

            if self.window.cursor_mode != spy.CursorMode.disabled:
                self.camera.can_update_input = False
            else:
                self.camera.can_update_input = True

            self.camera.update(dt)

        if self.input:
            self.input.update()

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

           #     self.mTriangleOrientation = self.mTriangleOrientation.identity()
           #     self.mTriangleOrientation = spy.math.translate(self.mTriangleOrientation, self.vTrianglePosition)

                self.mTriangleOrientation[3,0] = self.vTrianglePosition[0]
                self.mTriangleOrientation[3,1] = self.vTrianglePosition[1]
                self.mTriangleOrientation[3,2] = self.vTrianglePosition[2]

                self.mProjection = spy.math.perspective(
                    spy.math.radians(self.camera.fov),
                    texture_surface.width / texture_surface.height,
                    0.1,
                    100.0
                )

                cursor.g_mModel = self.mTriangleOrientation
                cursor.g_mView = self.camera.mView
                cursor.g_mProjection = self.mProjection


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
       if self.input:
           del self.input
           self.input = None

       if self.camera:
           del self.camera
           self.camera = None

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
           self.ui_main_window.remove_child(self.ui_shader_data_triangle_position)

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

                # we want to disable and try to use raw mouse cursor handling
                self.input.update_capture_mouse(event, self.window)


    def _on_keyboard_event(
            self,
            event : spy.KeyboardEvent
    ):
        if self.input:
            if event:
                self.input.update_keyboard(event)
