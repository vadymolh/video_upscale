import cv2
import matplotlib.pyplot as plt
import time


def upscale_nn(im):
    img = im # cv2.imread(im)
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
 
    path = "LapSRN_x8.pb"
 
    sr.readModel(path)
 
    sr.setModel("lapsrn",8)
 
    result = sr.upsample(img)
    return result

img = cv2.imread("gelikopter.jpg")
sr = cv2.dnn_superres.DnnSuperResImpl_create()
path = "LapSRN_x8.pb"
 
sr.readModel(path)
 
sr.setModel("lapsrn",8)
 
result = sr.upsample(img)
cv2.imshow("result", result)
cv2.waitKey(10000000)