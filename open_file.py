from tkinter import *
from tkinter import filedialog

class FilePathWindow(Tk):
    def __init__(self):
        super().__init__()
        self.filename = None
        self.geometry("300x300")
        self.label = Label(text="Шлях до файлу:")
        self.label.pack()
        self.button1 = Button(text = "Вибрати файл", command=self.ask_open)
        self.button1.pack()
        #self.button2 = Button(text = "Почати", command=self.start)
        #self.button2.pack()
    
    def ask_open(self):
        self.filename = filedialog.askopenfilename()
        self.label["text"] = f"Шлях до файлу: {self.filename}"  
    
    def start (self):
        self.destroy()