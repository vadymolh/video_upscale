from kivy.app import App
from kivy.core.window import Window
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button, Label
from plyer import filechooser

video_source = None
 
class FileChooserApp(App):
    def build(self):
        layout = FloatLayout()

        # create button to open file chooser dialog
        button = Button(text='Обрати файл',
                        size_hint=(0.3, 0.1),
                        pos_hint={'x': 0.35, 'y': 0.1})
        button.bind(on_press= lambda x: self.show_file_chooser())

        button_esc = Button(text='Запустити відео',
                        size_hint=(0.3, 0.1),
                        pos_hint={'x': 0.35, 'y': 0.2})
        button_esc.bind(on_press = lambda x:self.stop_app())
        self.label = Label(text = "Оберіть файл",
                      size_hint = (0.3, 0.1),
                      pos_hint = {'x': 0.35, 'y': 0.5})
        # add button to layout
        layout.add_widget(button)
        layout.add_widget(button_esc)
        layout.add_widget(self.label)
        return layout

    def show_file_chooser(self):
        # open file chooser dialog and get selected file
        filechooser.open_file(on_selection = self.selected)
    
    def selected(self, selection):
        global video_source
        video_source = selection[0]
        print(video_source)
        self.label.text = f"Ваш файл: {video_source}"
        return video_source
    
    def stop_app(App):
        App.stop()

        
