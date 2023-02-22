import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing
import threading as td
import open_file
from upscale import upscale_nn
from detection import detectVehicleCoords
import tkinter.filedialog
import dlib
import math

startX, startY = 0, 0
endX, endY = 0, 0
lenX, lenY = 0, 0
rect = False
cut_img = 0
res = 0
old_res = 0
k = 0
tracker = dlib.correlation_tracker()
track_flag = False
new_zone = False

def cropping_rect(startX, startY, endX, endY, koef=0.25):
    """Функція для зменшення прямокутника, з подальшим передавання координат у трекер"""

    global frame
    
    x1,y1,x2,y2 = detectVehicleCoords(clear_frame[startY:endY, startX:endX+int(endX*koef)])
   
    res = ( startX+x1 , startY+y1, startX+x2, startY+y2)
    return res

def tracking(frame, box):
    global tracker, track_flag
    tracker.start_track(frame, box)
    track_flag = True

# Функція знаходження координат виділеної зони
def coords(event,mouseX,mouseY, flags, param):
    global startX, startY, endX, endY, lenX, lenY, new_zone, frame
    if event == cv.EVENT_LBUTTONDOWN:
        startX, startY = mouseX,mouseY
        new_zone = True
    elif event == cv.EVENT_MOUSEMOVE and new_zone:
        #print(startX, startY, mouseX,mouseY)
        cv.rectangle(frame, (startX, startY), (mouseX,mouseY),(0,255,0), 2)
    elif event == cv.EVENT_LBUTTONUP and new_zone:
        endX, endY = mouseX, mouseY
        if True:
            trX1, trY1 , trX2, trY2 = cropping_rect(startX, startY, endY, endY)
            #box = dlib.rectangle(int(startX + lenX), int(startY+lenY), int(endX-lenX), int(endY-lenY))
            box = dlib.rectangle(trX1, trY1 , trX2, trY2)
            lenX, lenY = int(math.fabs(trX1-startX)), int(math.fabs(trY1-startY))
            tracking(param, box)
        new_zone = False
    return (startX, startY, endX, endY)

# Функція малювання прямокутника по заданим координатам
def draw_rectangle():
    global rect
    if (endX>0 and endY>0):
        cv.rectangle(frame,(startX, startY),(endX, endY),(0,255,0), 2)
        rect = True
    else: rect = False    
    

# Фукнція для роботи асинхронної обробки зображення 
def callbacking(temp_res):
    global cut_img, rect, res, clear_frame
    if rect == True:
        cut_img = clear_frame[startY+1:endY-1, startX+1:endX-1]
    pool.apply_async(upscale_nn, args=(cut_img,), callback=callbacking)
    if isinstance(temp_res, np.ndarray):
        res = temp_res

# Функція виводу результату після апскейлу
def show_result():
    global res, old_res, k, event 
    while 1:
        if isinstance(res, np.ndarray):
            if not np.array_equal(res, old_res):
                im = res[:,:,::-1]
                cv.imshow('Upscaled',im)
                k = cv.waitKey(1)
                old_res = res
                if k == 27:
                    cv.destroyWindow('Upscaled')
                    break

def is_border(startX, startY, endX, endY):
    if startX < 15 or startY<15 or endX > fr_width-15 or endY> fr_height-15:
        return True
    return False

if __name__=="__main__":
    filepath_window = open_file.FilePathWindow()
    if open_file.filename != None:
        filepath_window.destroy()
    filepath_window.mainloop()

    video = cv.VideoCapture(open_file.filename)
    
    frames = video.get(cv.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv.CAP_PROP_FPS)
    fr_width = video.get(cv.CAP_PROP_FRAME_WIDTH)
    fr_height = video.get(cv.CAP_PROP_FRAME_HEIGHT)

    if not fps: fps=30
    seconds = round(frames / fps, 1)


    ret, first_frame = video.read()
    cut_img = first_frame[0:40, 0:40]

    """first_frame = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
    otsu_threshold, image_result = cv.threshold(
    first_frame, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU,)"""

    pool = multiprocessing.Pool(processes=3)
    res = pool.apply_async(upscale_nn, args=(cut_img,), callback=callbacking)
    t = td.Thread(target=show_result)
    t.start()
    while True:
        ret, frame = video.read()
        clear_frame = frame.copy()
        cv.namedWindow('Frame')

        cv.setMouseCallback('Frame', coords, param=clear_frame)

        if track_flag and not is_border(startX, startY, endY, endY):
            tracker.update(frame)
            pos = tracker.get_position()
            X1 = int(pos.left()) 
            Y1 = int(pos.top()) 
            X2 = int(pos.right())
            Y2 = int(pos.bottom())

            #lenX, lenY = cropping_rect(startX, startY, endY, endY)
            # малюємо внутрішній прямокутник
            cv.rectangle(frame, (int(X1), int(Y1)), (int(X2), int(Y2)), (255, 0), 2)
            dx, dy = (X1-startX)-lenX, (Y1-startY)-lenY
            startX, startY, endX, endY = startX+dx, startY+dy, endX+dx, endY+dy


        draw_rectangle()
        cv.imshow('Frame', frame)
        #cv.imshow("Otsu", image_result)
        k=cv.waitKey(round(1000/fps)) 
        if k == 27:
            break
        if k == ord("p"):
            cv.waitKey(-1)


cv.destroyAllWindows()