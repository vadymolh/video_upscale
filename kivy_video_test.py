


if __name__=="__main__":
    from kivy.app import App
    import sys
    from kivy.uix.video import Video
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.button import Button, Label
    from kivy.graphics import Rectangle, Color, Rectangle, Line
    from kivy.properties import ReferenceListProperty
    import numpy as np
    import cv2
    #import multiprocessing
    import threading as td
    from plyer import filechooser
    from upscale import UpscaleNN
    from detection import detectVehicleCoords
    import dlib
    import math
    import os

    class VideoExt(Video):
        #absolute coordinates of rectangle on Video
        x1, y1, x2, y2 = None, None, None, None
        tracker_flag = False
        NN_FLAG = False
        tracker = dlib.correlation_tracker()
        # reference distance from zone corner to object corner
        ref_x, ref_y = 0, 0 

        def __init__(self, **kwargs):
            super().__init__(**kwargs)        
            self.frame = None
            self.pool = None
            self.res  = None
            self.cut_img = None
            print("Widget POS: " , self.x,self.y)
            #tuple to store relative coordinates of rectangle on Video Widget 
            self.start_pos, self.end_pos = None, None
            #tuple to store coordinates of rectangle in cv2 Coordinates format
            self.cv_start_pos, self.cv_end_pos = None, None
            self.upscaleInstance = UpscaleNN(frame=self.frame)
            with self.canvas:
                Color(0,1,0,0.3, mode="rgba")
            self.bind(pos=self.redraw, size=self.redraw)
            self.bind(texture=self.on_texture)
        def redraw(self, *args):
            self.canvas.remove_group('rect')
            #print("REDRAWING RECT")
            #print(f"WIDGET SIZE: {self.size[0]}, {self.size[1]}")
            #print(f"WIDGET position: {self.pos}")
            with self.canvas:
                x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
                if x1 and y1 and x2 and y2:
                    Line(rectangle=(x1, y1, x2-x1, y2-y1),width=2, group='rect')
                

        def _on_video_frame(self, *largs):
            super()._on_video_frame(*largs)
            #print(f"WIDGET SIZE: {self.size[0]}, {self.size[1]}")
            #print(f"WIDGET position: {self.pos}")
            if self.tracker_flag:
                self.tracker.update(self.frame)
                pos = self.tracker.get_position()
                obj_x1, obj_y1, obj_x2, obj_y2  = int(pos.left()), \
                                                  int(pos.top()),  \
                                                  int(pos.right()),\
                                                  int(pos.bottom())
                print("tracker ", obj_x1, obj_y1, obj_x2, obj_y2)
                obj_x1, obj_y1, obj_x2, obj_y2 = self.transform_coords(obj_x1, 
                                                                       obj_y1, 
                                                                       obj_x2, 
                                                                       obj_y2, 
                                                                       to_kivy=True)
                print("Transform tracker ", obj_x1, obj_y1, obj_x2, obj_y2)
                lr_space = (self.width - self.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (self.height - self.norm_image_size[1]) / 2  
                with self.canvas:
                    Line(rectangle=(obj_x1, obj_y1, obj_x2-obj_x1, obj_y2-obj_y1),width=2, group='rect')
                dx, dy = (obj_x1-self.x1)-self.ref_x, (obj_y1-self.y1)-self.ref_y + 2*tb_space
                self.x1, self.y1, self.x2, self.y2 = self.x1+dx, self.y1+dy, self.x2+dx, self.y2+dy
            #print((self.x1, self.y1, self.x2, self.y2))
            self.redraw()
            self.set_upscale_frame(self)

        def on_texture(self, instance, texture, *args):
            super(VideoExt, self).on_texture(instance, texture)
            texture_coords = texture.uvpos[:]
            # Print or use the texture_coords as needed
            #print("Texture Coords:", texture_coords)

        def get_visible_image_touch_coords(self, touch):
            if not self.collide_point(*touch.pos):
                return False
            lr_space = (self.width - self.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
            tb_space = (self.height - self.norm_image_size[1]) / 2
            pixel_x = touch.x - lr_space - self.x  # x coordinate of touch measured from lower left of actual image
            pixel_y = touch.y - tb_space - self.y  # y coordinate of touch measured from lower left of actual image
            return pixel_x, pixel_y
        
        def get_true_image_pixel_coords(self, visible_coords):
            if not visible_coords:
                return False
            pixel_x, pixel_y = visible_coords
            true_x = pixel_x * self.texture_size[0] / self.norm_image_size[0]
            true_y = pixel_y * self.texture_size[1] / self.norm_image_size[1]
            #revert Y Axis for cv2 usage
            true_y = self.texture_size[1] - true_y
            return int(true_x), int(true_y)
        
        def get_texture_coords(self, cv_coords):
            """Transform x, y from cv2 pixel image coord to texture coords"""
            if not cv_coords:
                return False
            pixel_x, pixel_y = cv_coords
            x = pixel_x * self.norm_image_size[0] / self.texture_size[0]
            y = pixel_y * self.norm_image_size[1] / self.texture_size[1] 
            y = self.norm_image_size[1] - y
            return int(x), int(y)
        
        def set_upscale_frame(self, *args):
            height, width = self.texture.height, self.texture.width
            start_flag = True
            if not isinstance(self.frame, np.ndarray):
                if self.frame == None: 
                    start_flag=False
                    self.NN_FLAG=False
            self.frame = np.frombuffer(self.texture.pixels, np.uint8)
            self.frame = self.frame.reshape(height, width, 4)
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGBA2BGR)
            self.upscaleInstance.frame = self.frame
            if type(self.start_pos)==tuple and type(self.end_pos)==tuple:
                ups = self.upscaleInstance
                x1, y1, x2, y2 = self.transform_coords(*self.start_pos, *self.end_pos, to_cv=True)
                ups.x1, ups.y1, ups.x2, ups.y2  = (int(x1), int(y1), int(x2), int(y2))
            if start_flag and not self.NN_FLAG:
                t = td.Thread(target=self.upscaleInstance.run_upscale) 
                t.start()
                self.NN_FLAG=True
        def on_touch_down(self, touch):
            with self.canvas:  
                self.start_pos = self.get_visible_image_touch_coords(touch)
                self.cv_start_pos = self.get_true_image_pixel_coords( self.start_pos)
                self.tracker_flag = False
        def on_touch_up(self, touch):
            with self.canvas:  
                lr_space = (self.width - self.norm_image_size[0]) / 2  # empty space in Image widget left and right of actual image
                tb_space = (self.height - self.norm_image_size[1]) / 2
                self.end_pos = self.get_visible_image_touch_coords(touch)
                self.cv_end_pos = self.get_true_image_pixel_coords(self.end_pos)
                if not self.end_pos or not self.start_pos:
                    return
                self.x1, self.y1 = self.start_pos[0] + lr_space + self.x, self.start_pos[1] + tb_space + self.y
                self.x2, self.y2 = self.end_pos[0] + lr_space + self.x, self.end_pos[1] + tb_space + self.y
                x1, y1, x2, y2 = self.x1, self.y1, self.x2, self.y2
                Line(rectangle=(x1, y1, x2-x1, y2-y1),width=2, group='rect')
            if not self.tracker_flag and None not in (x1, y1, x2, y2):
                x1, y1, x2, y2 = self.transform_coords(*self.start_pos, *self.end_pos, to_cv=True) 
                print("ZONE: ", x1, y1, x2, y2)
                obj_x1, obj_y1, obj_x2, obj_y2 =detectVehicleCoords(self.frame[y1:y2, x1:x2])
                print("Vehicle",obj_x1, obj_y1, obj_x2, obj_y2)
                obj_x1, obj_y1, obj_x2, obj_y2 = x1 + obj_x1, y1 + obj_y1, x1 + obj_x2, y1 + obj_y2
                box = dlib.rectangle(obj_x1, obj_y1, obj_x2, obj_y2)
                self.tracker.start_track(self.frame, box)
                self.tracker_flag = True
                self.ref_x, self.ref_y = int(math.fabs(obj_x1-x1)), int(math.fabs(obj_y2-y2))

        def transform_coords(self, x1, y1, x2, y2, to_cv=False, to_kivy=False):
            if to_cv:
                x1, y1 = self.get_true_image_pixel_coords((x1, y1))
                x2, y2 = self.get_true_image_pixel_coords((x2, y2))
                return x1, y2, x2, y1
            elif to_kivy:
                x1, y1 =  self.get_texture_coords((x1, y1))
                x2, y2 =  self.get_texture_coords((x2, y2))
                return x1, y2, x2, y1
            return x1, y1, x2, y2
               
    class VideoApp(App):
        def build(self):
            # create a Video widget to display the video filechooser.video_source


            self.video = VideoExt(source=None,
                                  state='stop', 
                                  size_hint = (0.8, 1), 
                                  pos_hint = {'x': 0, 'y': 0.12},
                                  keep_ratio= True)
            #print(self.video.source)
            # create a box layout to hold the video and control buttons
            layout = FloatLayout(height = 1080, width = 1920)
            #video_box = GridLayout(rows=1, cols=1)
            # add the Video widget to the layout
            layout.add_widget(self.video)
            #video_box.add_widget(self.video)
            
            # create buttons to play, pause, and stop the video
            upscale_button = Button(text='Upscale',
                                size_hint = (.10, .10),
                                pos_hint = {'x': 0.15, 'y': 0.01},)
            
            tracking_button = Button(text='Tracking', 
                                size_hint = (.10, .10),
                                pos_hint = {'x': 0.75, 'y': 0.01},)
            
            play_button = Button(text='Play', 
                                size_hint = (.10, .10),
                                pos_hint = {'x': 0.85, 'y': 0.85},
                                on_press=self.play_video)

            stop_button = Button(text='Stop', 
                                size_hint = (.10, .10),
                                pos_hint = {'x': 0.85, 'y': 0.7},
                                on_press=self.pause_video)

            nn_button = Button(text='Choose NN', 
                                size_hint = (.10, .10),
                                pos_hint = {'x': 0.85, 'y': 0.55},
                                on_press = self.choose_nn)

            clean_button = Button(text='Choose video', 
                                size_hint = (.10, .10),
                                pos_hint = {'x': 0.85, 'y': 0.4},
                                on_press = self.choose_video)


            # add the buttons to the layout
            layout.add_widget(upscale_button)
            layout.add_widget(tracking_button)
            layout.add_widget(play_button)
            layout.add_widget(stop_button)
            layout.add_widget(nn_button)
            layout.add_widget(clean_button)
            
            # bind the state of the Video widget to update the play/pause button
            self.video.bind(state=self.update_play_pause_button)
            return layout
        
        def choose_video(self, instance):
            self.video_source = filechooser.open_file()
            self.video.source = self.video_source[0]

        def choose_nn(self, instance):
            self.nn = filechooser.open_file()
            self.nn = os.path.join(self.nn[0])
            self.video.upscaleInstance.path = self.nn

        def play_video(self, instance):
            # play the video
            self.video.state = 'play'
            
        def pause_video(self, instance):
            # pause the video
            self.video.state = 'pause'
                
        def update_play_pause_button(self, instance, state):
            # update the play/pause button based on the state of the video
            play_button = instance.parent.children[3]
            stop_button = instance.parent.children[2]
            if state == 'play':
                play_button.disabled = True
                stop_button.disabled = False
            else:
                play_button.disabled = False
                stop_button.disabled = True
    #multiprocessing.freeze_support()
    #filechooser.FileChooserApp().run()
    app=VideoApp()
    app.run()
