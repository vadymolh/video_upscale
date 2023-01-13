import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing
import threading as td
from upscale import upscale_nn
import dlib

video = cv.VideoCapture("vid.mp4")
frames = video.get(cv.CAP_PROP_FRAME_COUNT)
fps = video.get(cv.CAP_PROP_FPS)
fr_width = video.get(cv.CAP_PROP_FRAME_WIDTH)
fr_height = video.get(cv.CAP_PROP_FRAME_HEIGHT)
seconds = round(frames / fps, 1)

startX, startY = 0, 0
endX, endY = 0, 0
rect = False
cut_img = 0
res = 0
old_res = 0
k = 0
tracker = dlib.correlation_tracker()
track_flag = False

def cropping_rect(startX, startY, endX, endY, koef=0.25):
    """Функція для зменшення прямокутника, з подальшим передавання координат у трекер"""
    lenX = endX - startX
    lenY = endY - startY
    lenX = lenX * koef
    lenY = lenY * koef
    return (int(lenX), int(lenY))
def tracking(frame, box):
    global tracker, track_flag
    tracker.start_track(frame, box)
    track_flag = True

# Функція знаходження координат виділеної зони
def coords(event,mouseX,mouseY, flags, param):
    global startX, startY, endX, endY 
    if event == cv.EVENT_LBUTTONDOWN:
        startX, startY = mouseX,mouseY
    elif event == cv.EVENT_LBUTTONUP:
        endX, endY = mouseX, mouseY
        if ret:
            lenX, lenY = cropping_rect(startX, startY, endY, endY)
            box = dlib.rectangle(int(startX + lenX), int(startY+lenY), int(endX-lenX), int(endY-lenY))
            tracking(frame, box)
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
    global cut_img, rect, res
    if rect == True:
        cut_img = frame[startY+1:endY-1, startX+1:endX-1]
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
                width = int(im.shape[1]*0.4)
                height = int(im.shape[0]*0.4)
                size = (width, height)
                resized_im = cv.resize(im, size)
                cv.imshow('Upscaled',resized_im)
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
        cv.namedWindow('Frame')
        cv.setMouseCallback('Frame', coords)
        if track_flag and not is_border(startX, startY, endY, endY):
            tracker.update(frame)
            pos = tracker.get_position()
            X1 = int(pos.left()) 
            Y1 = int(pos.top()) 
            X2 = int(pos.right())
            Y2 = int(pos.bottom())
            lenX, lenY = cropping_rect(startX, startY, endY, endY)
            # малюємо внутрішній прямокутник
            cv.rectangle(frame, (int(X1), int(Y1)), (int(X2), int(Y2)), (0, 255, 0), 2)
            startX, startY, endX, endY = X1-lenX, Y1-lenY, X2+lenX, Y2+lenY
        draw_rectangle()
        cv.imshow('Frame', frame)
        #cv.imshow("Otsu", image_result)
        k=cv.waitKey(round(1000/fps)) 
        if k == 27:
            break
        if k == ord("p"):
            cv.waitKey(-1)


cv.destroyAllWindows()