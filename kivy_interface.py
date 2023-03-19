from kivy.app import App
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
import cv2
video = None
class VideoPlayerApp(App):
    def build(self):
        global video
        # create a Video widget to display the video
        video = Video(source='vid.mp4', state='stop', size_hint = (0.8, 1), pos_hint = {'x': 0, 'y': 0.12})
        # create a box layout to hold the video and control buttons
        layout = FloatLayout(height = 1080, width = 1920)
        
        # add the Video widget to the layout
        layout.add_widget(video)
        
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
                              pos_hint = {'x': 0.85, 'y': 0.55},)

        clean_button = Button(text='Clean frame', 
                              size_hint = (.10, .10),
                              pos_hint = {'x': 0.85, 'y': 0.4},)


        # add the buttons to the layout
        layout.add_widget(upscale_button)
        layout.add_widget(tracking_button)
        layout.add_widget(play_button)
        layout.add_widget(stop_button)
        layout.add_widget(nn_button)
        layout.add_widget(clean_button)
        
        # bind the state of the Video widget to update the play/pause button
        video.bind(state=self.update_play_pause_button)
        
        return layout
        
    def play_video(self, instance):
        # play the video
        video.state = 'play'
        
    def pause_video(self, instance):
        # pause the video
        video.state = 'pause'
            
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
if __name__ == '__main__':
    app = VideoPlayerApp()
    app.run()
