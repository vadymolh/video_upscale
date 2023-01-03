import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing
import threading as td
from upscale import upscale_nn

video = cv.VideoCapture("vid.mp4")
frames = video.get(cv.CAP_PROP_FRAME_COUNT)
fps = video.get(cv.CAP_PROP_FPS)
seconds = round(frames / fps, 1)

startX, startY = 0, 0
endX, endY = 0, 0
rect = False
cut_img = 0
res = 0
old_res = 0
k = 0

tracker = cv.TrackerCSRT_create()
tracker_flag = False

def track_object_init(fr, bb):
    """Відслідковує об'єкт та оновлює 
    рамку навколо нього
    """
    global tracker, tracker_flag
    tracker.init(fr,bb)
    tracker_flag = True


# Функція знаходження координат виділеної зони
def coords(event,mouseX,mouseY, flags, param):
    global startX, startY, endX, endY 
    if event == cv.EVENT_LBUTTONDOWN:
        startX, startY = mouseX,mouseY
    elif event == cv.EVENT_LBUTTONUP:
        endX, endY = mouseX, mouseY
        if ret: #якщо кадр зчитано вдало
            bb = (startX, startY, endX, endY)
            track_object_init(frame, bb)
    return (startX, startY, endX, endY)

# Функція малювання прямокутника по заданим координатам
def draw_rectangle():
    global rect
    if (endX>0 and endY>0):
        cv.rectangle(frame,(startX, startY),(endX, endY),(0,255,0), 2)
        rect = True
    else: rect = False    
    

"""def cutting():
    global rect
    if rect == True:   
        cut_img = frame[startY+1:endY-1, startX+1:endX-1]
        result = upscale_nn(cut_img)
        plt.imshow(result[:,:,::-1])    
        plt.show()
    else:
        rect = False """
# Фукнція для роботи асинхронного апскейлу зображення 
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

if __name__=="__main__":
    ret, first_frame = video.read()
    cut_img = first_frame[0:40, 0:40]
    pool = multiprocessing.Pool(processes=3)
    res = pool.apply_async(upscale_nn, args=(cut_img,), callback=callbacking)
    t = td.Thread(target = show_result)
    t.start()
    while True:
        ret, frame = video.read()
        cv.namedWindow('Frame')
        cv.setMouseCallback('Frame',coords)
        if tracker_flag:
            (success, box) = tracker.update(frame)
            if success:
                startX, startY, \
                endX, endY  = [int(x) for x in box]
    
        draw_rectangle()
        cv.imshow('Frame',frame)
        k=cv.waitKey(round(1000/fps)) 
        if k == 27:
            break
        if k == ord("p"):
            cv.waitKey(-1)


            

cv.destroyAllWindows()


# перший фрейм для async, callback 