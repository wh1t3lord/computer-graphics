# Author: wh1t3lord

import slangpy as spy
from pathlib import Path
import scenes
import time


DIR_ROOT = Path(__file__).parent.parent
DIR_DATA = DIR_ROOT / 'data'
DIR_DATA_SHADERS = DIR_DATA / 'shaders'

app = None

# not good but better to use local private method from class and call it from lambda
# todo: refactor pls
def ui_callback_combobox_scenes(index : int) -> None:
    if app:
        scene_name = list(app.scenes.keys())[index]
        app.switch_scene(scene_name)

class App:
    def __init__(self):
        self.current_scene : scenes.IScene = None
        self.is_need_to_switch_scenes : bool = False
        self.current_scene_name = 'empty'
        self.prev_time = time.perf_counter()
        self.delta_time = 0.0

        self.__register_scenes()
        self.__init()


        self.set_current_scene(self.current_scene_name)

    def __register_scenes(self):
        self.scenes = {
            "empty": scenes.SceneRasterEmpty(),
            "2d - triangle": scenes.SceneRasterTriangle(),
            "2d - triangle with color": scenes.SceneRasterTriangleColor(),
            "2d - color triangle with camera": scenes.SceneRasterTriangleCamera()
        }

    def __window_callback_resize(
            self,
            width : int,
            height : int
    ):
        if self.current_scene:
            if self.window:
                self.current_scene.on_resize(width,height)

    def __window_callback_mouse_event(
            self,
            event : spy.MouseEvent
    ):
        if self.ui:
            if self.ui.handle_mouse_event(event):
                return

        if self.current_scene:
            if self.window:
                self.current_scene.on_mouse_event(event)

    def __window_callback_keyboard_event(
            self,
            event : spy.KeyboardEvent
    ):
        if self.ui:
            if self.ui.handle_keyboard_event(event):
                return

        if event.is_key_press() and event.key == spy.KeyCode.right:
            key_list = list(self.scenes.keys())
            index = key_list.index(self.current_scene_name)

            if index < len(key_list) - 1:
                scene_name = key_list[index+1]
                self.switch_scene(scene_name)
                self.ui_window_combobox_scenes.value = index + 1

        if event.is_key_press() and event.key == spy.KeyCode.left:
            key_list = list(self.scenes.keys())
            index = key_list.index(self.current_scene_name)

            if index > 0:
                scene_name = key_list[index-1]
                self.switch_scene(scene_name)
                self.ui_window_combobox_scenes.value = index - 1

        if self.current_scene:
            if self.window:
                self.current_scene.on_keyboard_event(event)

    def __init(self):
        self.window = spy.Window(
            width=640,
            height=480,
            title="",
            resizable=True
        )

        if self.window:
            self.window.on_resize = self.__window_callback_resize
            self.window.on_mouse_event = self.__window_callback_mouse_event
            self.window.on_keyboard_event = self.__window_callback_keyboard_event

        self.device = spy.Device(
            enable_debug_layers=True,
            type=spy.DeviceType.vulkan,
        )

        self.ui = None
        if self.device:
            self.ui = spy.ui.Context(self.device)

            if self.ui:
                self.ui_window = spy.ui.Window(
                    self.ui.screen, 
                    "Scenes", 
                    size=spy.float2(self.window.width*0.25, self.window.height*0.25)
                )
                
                self.ui_window_text_current_scene_name = spy.ui.Text(self.ui_window, '')
                keys_to_list = list(self.scenes.keys())
                self.ui_window_combobox_scenes = spy.ui.ComboBox(
                    self.ui_window,
                    'scenes', 
                    keys_to_list.index(self.current_scene_name), 
                    ui_callback_combobox_scenes, 
                    keys_to_list
                )

                self.ui_text_navigation = spy.ui.Text(self.ui_window, 'For switching scenes you can use:\n\t1) <- or -> (on your keyboard)\n\t2) combobox\n\nDescription:\n')

    def set_current_scene(self, scene_name : str):
        if not scene_name:
            return
        
        if len(scene_name)==0:
            return
        
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            self.current_scene_name = scene_name
            self.current_scene.init(
                self.device, 
                self.window,
                self.ui,
                self.ui_window,
                DIR_DATA_SHADERS
            )

            print(f'initialized scene -> {self.current_scene.__class__.__name__}')

            self.ui_window_text_current_scene_name.text = f'current scene: {self.current_scene.__class__.__name__}'

    def switch_scene(self, scene_name : str):
        self.is_need_to_switch_scenes = True
        print(f'switching scene {self.current_scene_name} to {scene_name}')
        self.current_scene_name = scene_name


    def update(self):
        if self.current_scene == None:
            return
        
        while not self.window.should_close():
            self.window.process_events()
            self.ui.process_events()

            if self.is_need_to_switch_scenes:
                if self.current_scene:
                    self.current_scene.shutdown()
                    print(f'destroyed scene -> {self.current_scene.__class__.__name__}')

                self.set_current_scene(self.current_scene_name)
                self.is_need_to_switch_scenes = False
                print('scene switched!')

            current_time = time.perf_counter()
            self.delta_time = current_time - self.prev_time
            self.prev_time = current_time
            
            self.current_scene.update(dt=self.delta_time)
            self.current_scene.render()

    def shutdown(self):
        if self.current_scene == None:
            return



if __name__ == "__main__":
    print(f'root dir: {DIR_ROOT}')
    print(f'data dir: {DIR_DATA}')

    if not DIR_ROOT.exists():
        raise "failed to determine root path"

    if not DIR_DATA.exists():
        raise "failed to determine data path"
    
    if not DIR_DATA_SHADERS.exists():
        raise 'failed to determine data/shaders path'
    app = App()
    app.update()
    app.shutdown()