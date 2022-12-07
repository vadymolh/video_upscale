import cv2 as cv
import time
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from upscale import upscale_nn
import os

video = cv.VideoCapture("vid.mp4")
frames = video.get(cv.CAP_PROP_FRAME_COUNT)
fps = video.get(cv.CAP_PROP_FPS)
seconds = round(frames / fps, 1)

startX, startY = 0, 0
endX, endY = 0, 0
i = 1
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
    global rect, i
    if rect == True:   
        #cv.imwrite(f"frame{i}.png", frame)
        im = Image.fromarray(frame)
        cut = im.crop((startX+2, startY+2, endX-1, endY-1))
        cut_img = np.array(cut)
        result = upscale_nn(cut_img)
        plt.imshow(result[:,:,::-1])
        plt.show()
        #cut_img.save(f"cut_img{i}.png")
        #os.remove(f"frame{i}.png")
        i = i+1      
          
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
        #current_sec = time.time() -timer
        #print(f"TIME: {0 + (current_sec)}")
        #frame_id = int(frames/current_sec)
        #print(cv.CAP_PROP_POS_FRAMES)
        #print(frame_id)
        #video.set(cv.CAP_PROP_POS_FRAMES, frame_id)
        #ret, frame = video.read())
        cutting()
        cv.waitKey(-1)
        

cv.destroyAllWindows()
