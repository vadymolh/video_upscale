import cv2
import matplotlib.pyplot as plt
import time
import multiprocessing
import threading as td
import numpy as np
from alter_multiproc import MyPool

def upscale_nn( im, path = "models/LapSRN_x4.pb"):
    img = im # cv2.imread(im)
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    #cv2.imshow('NOT Upscaled', im)
    sr.readModel(path)
    filename =  path.split('/')[-1]
    modelName, x = "", int(filename[filename.find('x')+1])
    if "Lap" in filename:
        modelName = "lapsrn"
    elif "EDSR" in filename:
        modelName = "edsr"
    elif "ESPCN" in filename:
        modelName = "espcn"
    sr.setModel(modelName, x)
 
    result = sr.upsample(img)
    return result
    

class UpscaleNN():
    """coords = (x1,y1, x2,y2)"""
    pool = MyPool(4)
    def __init__(self, frame, path="models/LapSRN_x4.pb", x1=100, y1=100, x2=240, y2=240,):
        self.x1, self.y1, self.x2, self.y2 =  x1, y1, x2, y2
        self.frame = frame
        self.cut_img = None
        self.res  = None
        self.path = path 
    def run_upscale(self):
        print("RUN UPSCALE")
        self.cut_img = self.frame[self.y1:self.y2, self.x1:self.x2]
        self.res = self.pool.apply_async(upscale_nn, args=(self.cut_img, self.path), callback=self.callbacking)
        t = td.Thread(target=self.show_result)
        t.start()

    def callbacking(self, temp_res, *args):
        self.cut_img = self.frame[self.y1:self.y2, self.x1:self.x2]
        self.pool.apply_async(upscale_nn, args=(self.cut_img, self.path), callback=self.callbacking)
        if isinstance(temp_res, np.ndarray):
            self.res = temp_res
    
    def show_result(self): 
        while 1:
            if isinstance(self.res, np.ndarray):
                im = self.res[:,:,::-1]
                cv2.imshow('Upscaled',im)
                #cv2.imshow('cutted',self.cut_img)
                k = cv2.waitKey(1)
                if k == 27:
                    cv2.destroyWindow('Upscaled')
                    break

if __name__=="__main__":
    multiprocessing.freeze_support()