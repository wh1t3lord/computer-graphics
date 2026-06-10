# Author: wh1t3lord

import core
import random
import slangpy as spy
from pathlib import Path
import numpy as np

class SceneRasterStaticModelNaiveTextureBoxTransformNoGimbalCamera(core.IScene):
    def __init__(self):
        super().__init__()

        self.ui_cpu_data_model_position = None
        self.ui_cpu_data_model_rotation = None
        self.ui_cpu_data_model_scale = None
        self.ui_print_camera_basis = None
        self.ui_print_camera_orientation_matrix = None
        self.ui_print_camera_yaw_and_pitch = None
        self.ui_print_camera_position = None
        self.ui_cpu_data_camera_position = None
        self.ui_cpu_data_camera_fov = None
        self.ui_cpu_switch_wireframe = None
        self.EditorTransformStatus = np.array([False, False, False], dtype=np.bool)
        self.wireframe_mode = False

        self.debug_ui_cam = False

    def _init(
            self,
            device : spy.Device, 
            window : spy.Window,
            ui : spy.ui.Context,
            ui_main_window : spy.ui.Window,
            shaders_path : Path,
            textures_path : Path,
            models_path : Path
        ):
        print(f'{self.__class__.__name__}: init called')

        self.device = device

        if self.device:
            shader_name = shaders_path / 'raster' / 'srm3_cam.slang'
            self.program = self.device.load_program(str(shader_name), ['mainVertex', 'mainPixel'])
            

            float_size = spy.DataStruct.type_size(spy.DataStruct.Type.float32)
            
            input_layout = self.device.create_input_layout(
                input_elements=[
                    {
                        "semantic_name": "POSITION",
                        "semantic_index": 0,
                        "format": spy.Format.rgb32_float,
                        # don't forget that we need actually specify offsets explicitly!
                        "offset": 0,
                    },
                    {
                        "semantic_name": "COLOR",
                        "semantic_index": 0,
                        "format": spy.Format.rgb32_float,
                        # float_size * 3 like 4 * 3 because previously we defined that we have position 
                        # it consists of 3 components that represent x,y,z and each of 4 bytes (or float32 bits, because 1 bytes is 8 bits and 32 bits it is 4 bytes respectively)
                        # so our next data will be located after position and thus we need to tell driver
                        # that our color goes after position and it is 12 bytes
                        "offset": float_size * 3,
                    },
                    {
                        "semantic_name": "TEXCOORD",
                        "semantic_index": 0,
                        "format": spy.Format.rg32_float,
                        "offset": float_size * 6,
                    }
                ],
                vertex_streams=[{"stride": float_size * 8}],
            )

            self.pipeline = self.device.create_render_pipeline(
                program=self.program,
                input_layout=input_layout,
                targets=[{"format": spy.Format.rgba32_float}],
                # because if we have by default is None then we won't see back faces when
                # rendering our model (box)
                rasterizer={"cull_mode": spy.CullMode.back, 'front_face': spy.FrontFaceMode.clockwise}
            )

            self.pipeline_wireframe = self.device.create_render_pipeline(
                program=self.program,
                input_layout=input_layout,
                targets=[{"format": spy.Format.rgba32_float}],
                # because if we have by default is None then we won't see back faces when
                # rendering our model (box)
                rasterizer={"fill_mode": spy.FillMode.wireframe, "cull_mode": spy.CullMode.none, 'front_face': spy.FrontFaceMode.clockwise}
            )

            self.mProjection : spy.math.float4x4 = spy.math.float4x4()

            self.input = core.Input()

            # let's create our camera based on euler rotations
            self.camera = core.Camera(self.input)

            self.camera.vPosition[0] = 1.7
            self.camera.vPosition[1] = 1.2
            self.camera.vPosition[2] = -2.3

            self.camera.pitch = -15
            self.camera.yaw = -40

            self.model = core.ModelNaive()

            self.model.load_from_memory(
                device=self.device,
                vertices=core.model_naive.model_get_box_vertices_with_color_uv_attrb(),
                indicies=core.model_naive.model_get_box_indicies(),
                # because 3 position components per byte (3 * 4 = 12) + 3 color components per byte (3 * 4 = 12) in total 12 + 12 = 24
                # AND we add uv so 24 + 8 (2 uv components per byte) = 32
                in_struct_size=32
            )

            self.model_texture = core.TextureNaive()

            self.model_texture.load_from_file(device, textures_path / 'wall' / 'brick1.png')

            # for texture we need to use sampler that will define how we will sample our texture in shader 
            # (for example, if we want to use linear or point sampling, or how we will handle uv coordinates that are outside of 0-1 range and so on)
            self.sampler = self.device.create_sampler(
                {
                    "address_u": spy.TextureAddressingMode.wrap,
                    "address_v": spy.TextureAddressingMode.wrap,
                    "address_w": spy.TextureAddressingMode.wrap,
                    "min_filter": spy.TextureFilteringMode.linear,
                    "mag_filter": spy.TextureFilteringMode.linear,
                    "mip_filter": spy.TextureFilteringMode.linear,
                }
            )

            self.binding_cam_pitch = self.input.get_binding_state(core.eInputBindingsType.kCamLookPitch)
            self.binding_cam_yaw = self.input.get_binding_state(core.eInputBindingsType.kCamLookYaw)

            if window != None:
                self.swapchain = self.device.create_surface(window)
                self.swapchain.configure(width=window.width,height=window.height)

                self.ui = ui
                self.window = window

            if ui_main_window != None:
                self.ui_cpu_data_model_position = spy.ui.DragFloat3(
                    ui_main_window,
                    'model position',
                    self.model.vPosition[:3],
                    self._ui_set_dragfloat3_model_position,
                    0.01,
                    -100.0,
                    100.0
                )

                self.ui_cpu_data_model_rotation = spy.ui.DragFloat3(
                    ui_main_window,
                    'model rotation',
                    self.model.vRotation[:3],
                    self._ui_set_dragfloat3_model_rotation,
                    0.1,
                    -360.0,
                    360.0
                )

                self.ui_cpu_data_model_scale = spy.ui.DragFloat3(
                    ui_main_window,
                    'model scale',
                    self.model.vScale[:3],
                    self._ui_set_dragfloat3_model_scale,
                    0.01,
                    0.0,
                    10.0
                )

                self.ui_print_camera_position = spy.ui.Text(
                    ui_main_window,
                    ''
                )

                self.ui_cpu_switch_wireframe = spy.ui.CheckBox(
                    ui_main_window,
                    label='Wireframe',
                    value=self.wireframe_mode,
                    callback=self._ui_set_checkbox_wireframe
                )

                if self.debug_ui_cam == True:
                    self.ui_cpu_data_camera_position = spy.ui.DragFloat3(
                        ui_main_window,
                        'camera position',
                        self.camera.vPosition,
                        self._ui_set_dragfloat3_camera_position,
                        0.01,
                        -100.0,
                        100.0
                    )

                    self.ui_cpu_data_camera_fov = spy.ui.DragFloat(
                        ui_main_window,
                        'camera fov (degrees)',
                        self.camera.fov,
                        self._ui_set_dragfloat_camera_fov,
                        0.01,
                        10.0,
                        120.0
                    )

                    self.ui_print_camera_basis = spy.ui.Text(
                        ui_main_window,
                        r"""
    Camera basis:

    +Y (Up)
    |
    |    +Z (Forward)
    |   /
    |  /
    | /
    +-------- +X (Right)
                        """
                    )

                    self.ui_print_camera_yaw_and_pitch = spy.ui.Text(
                        ui_main_window,
                        ''
                    )

                    self.ui_print_camera_orientation_matrix = spy.ui.Text(
                        ui_main_window,
                        ''
                    )



                self.ui_main_window = ui_main_window

    def _ui_set_dragfloat3_camera_position(self, value):
        self.camera.vPosition = value

    def _ui_set_dragfloat_camera_fov(self, value):
        self.camera.fov = value 

    def _ui_set_dragfloat3_model_position(self, value):
        self.model.vPosition[:3] = value
        self.EditorTransformStatus[0] = True

    def _ui_set_dragfloat3_model_rotation(self, value):
        self.model.vRotation[:3] = value
        self.EditorTransformStatus[1] = True

    def _ui_set_dragfloat3_model_scale(self, value):
        self.model.vScale[:3] = value
        self.EditorTransformStatus[2] = True

    def _ui_set_checkbox_wireframe(self, value):
        self.wireframe_mode = value

    def _update(
            self,
            dt : spy.math.float1
        ):
        if self.camera:

            if self.window.cursor_mode != spy.CursorMode.disabled:
                self.camera.can_update_input = False
            else:
                self.camera.can_update_input = True


            if self.camera.can_update_input:
                if self.ui_cpu_data_camera_position is not None and self.debug_ui_cam == True:
                    # Because binding is not direct and slanpy creates underlying temp copy variable of binded value argument for DragFloat3
                    # So we need to emulate 'reference' updating if a such binding model would be provided by slangpy library
                    self.ui_cpu_data_camera_position.value = self.camera.vPosition

            if self.ui_print_camera_position is not None:
                self.ui_print_camera_position.text = f'Cam pos: {self.camera.vPosition[0]:.3f} {self.camera.vPosition[1]:.3f} {self.camera.vPosition[2]:.3f}'

            self.camera.update(dt)

            if self.ui_print_camera_orientation_matrix is not None and self.debug_ui_cam == True:
                self.ui_print_camera_orientation_matrix.text = f'[0] = {self.camera.mView[0][0]:.3f} {self.camera.mView[0][1]:.3f} {self.camera.mView[0][2]:.3f} {self.camera.mView[0][3]:.3f} (X | Right)\n[1] = {self.camera.mView[1][0]:.3f} {self.camera.mView[1][1]:.3f} {self.camera.mView[1][2]:.3f} {self.camera.mView[1][3]:.3f}  (Y | Up)\n[2] = {self.camera.mView[2][0]:.3f} {self.camera.mView[2][1]:.3f} {self.camera.mView[2][2]:.3f} {self.camera.mView[2][3]:.3f} (Z | Forward)\n[3] = {self.camera.mView[3][0]:.3f} {self.camera.mView[3][1]:.3f} {self.camera.mView[3][2]:.3f} {self.camera.mView[3][3]:.3f}'

            if self.ui_print_camera_yaw_and_pitch is not None and self.debug_ui_cam == True:
                self.ui_print_camera_yaw_and_pitch.text = f'yaw={self.camera.yaw:.3f} pitch={self.camera.pitch:.3f}'


        if self.input:
            self.input.update()


        if self.model is not None:
            if self.EditorTransformStatus[0] == True or self.EditorTransformStatus[1] == True or self.EditorTransformStatus[2] == True:
                # NOTE: mathematically it is impossible to implement a such setting where we operate degrees and apply rotations in order to not cause gimbal lock
                # so we just use less high-frequent model where Y-X-Z and limit 'pitch' to prevent gimbal lock
                self.model.apply_tsr(
                    self.model.vPosition,
                    self.model.vRotation,
                    self.model.vScale
                )

                self.EditorTransformStatus = np.array([False,False,False], dtype=np.bool)

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
                

                if self.wireframe_mode == False:
                    shader_object = rp.bind_pipeline(self.pipeline)
                else:
                    shader_object = rp.bind_pipeline(self.pipeline_wireframe)

                cursor = spy.ShaderCursor(shader_object)

                self.mProjection = spy.math.perspective(
                    spy.math.radians(self.camera.fov),
                    texture_surface.width / texture_surface.height,
                    0.1,
                    100.0
                )

                cursor.g_mModel = self.model.mModel
                cursor.g_mView = self.camera.mView
                cursor.g_mProjection = self.mProjection

                cursor.g_texture = self.model_texture.texture
                cursor.g_sampler = self.sampler


                rp.set_render_state(
                        {
                            "viewports": [spy.Viewport.from_size(texture_surface.width, texture_surface.height)],
                            "scissor_rects": [
                                spy.ScissorRect.from_size(texture_surface.width, texture_surface.height)
                            ],
                            "vertex_buffers": [self.model.buffer_vertex],
                            "index_buffer": self.model.buffer_index,
                            "index_format": spy.IndexFormat.uint32,
                        }
                    )
                rp.draw_indexed({"vertex_count": self.model.index_count})

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
           del self.program
           del self.pipeline
           del self.pipeline_wireframe

       if self.model is not None:
           if self.model.buffer_vertex is not None:
               del self.model.buffer_vertex
               self.model.buffer_vertex = None

           if self.model.buffer_index is not None:
               del self.model.buffer_index
               self.model.buffer_index = None
               
       if self.ui_main_window:
           self.ui_main_window.remove_child(self.ui_cpu_data_model_position)
           self.ui_main_window.remove_child(self.ui_cpu_data_model_rotation)
           self.ui_main_window.remove_child(self.ui_cpu_data_model_scale)
           self.ui_main_window.remove_child(self.ui_print_camera_position)
           self.ui_main_window.remove_child(self.ui_cpu_switch_wireframe)

           del self.ui_cpu_data_model_position
           del self.ui_cpu_data_model_rotation
           del self.ui_cpu_data_model_scale
           del self.ui_print_camera_position
           del self.ui_cpu_switch_wireframe
           
           if self.debug_ui_cam == True:
            self.ui_main_window.remove_child(self.ui_print_camera_orientation_matrix)
            self.ui_main_window.remove_child(self.ui_cpu_data_camera_position)
            self.ui_main_window.remove_child(self.ui_cpu_data_camera_fov)
            self.ui_main_window.remove_child(self.ui_print_camera_yaw_and_pitch)
            self.ui_main_window.remove_child(self.ui_print_camera_basis)

            del self.ui_print_camera_orientation_matrix
            del self.ui_cpu_data_camera_position
            del self.ui_cpu_data_camera_fov
            del self.ui_print_camera_yaw_and_pitch
            del self.ui_print_camera_basis

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
