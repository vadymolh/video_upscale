import cv2 as cv
import time
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from upscale import upscale_nn

video = cv.VideoCapture("vid.mp4")
frames = video.get(cv.CAP_PROP_FRAME_COUNT)
fps = video.get(cv.CAP_PROP_FPS)
seconds = round(frames / fps, 1)

startX, startY = 0, 0
endX, endY = 0, 0
rect = False

def coords(event,mouseX,mouseY, flags, param):
    global startX, startY, endX, endY 
    if event == cv.EVENT_LBUTTONDOWN:
        startX, startY = mouseX,mouseY
    elif event == cv.EVENT_LBUTTONUP:
        endX, endY = mouseX, mouseY
    return (startX, startY, endX, endY)

def draw_rectangle():
    global rect
    if (endX>0 and endY>0):
        cv.rectangle(frame,(startX, startY),(endX, endY),(0,255,0), 2)
        rect = True
    else: rect = False    
    

def cutting():
    global rect
    if rect == True:   
        #im = Image.fromarray(frame)
        #cut = im.crop((startX+2, startY+2, endX-1, endY-1))
        cut_img = frame[startY+1:endY-1, startX+1:endX-1]
        #cut_img = np.array(cut)
        result = upscale_nn(cut_img)
        #cv.imshow("cut",cut)
        plt.imshow(result[:,:,::-1])
        plt.show()     
    else:
        rect = False    


timer = time.time() 
while(True):
    ret, frame = video.read()

    cv.namedWindow('Frame')
    cv.setMouseCallback('Frame',coords)
    draw_rectangle()
    #cutting()
    cv.imshow('Frame',frame)
    k = cv.waitKey(round(1000/fps)) 
    if k == 27:
        break
    if k == ord("p"):
        cutting()
        cv.waitKey(-1)
        

cv.destroyAllWindows()
