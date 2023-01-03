import cv2
import matplotlib.pyplot as plt
import time


def upscale_nn(im):
    img = im # cv2.imread(im)
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
 
    path = "LapSRN_x4.pb"
 
    sr.readModel(path)
 
    sr.setModel("lapsrn",4)
 
    result = sr.upsample(img)
    return result

"""timer = time.time()
img = cv2.imread("gelikopter.jpg")
sr = cv2.dnn_superres.DnnSuperResImpl_create()
path = "LapSRN_x4.pb"
 
sr.readModel(path)
 
sr.setModel("lapsrn",4)
 
result = sr.upsample(img)
cv2.imshow("result", result)
print(time.time() - timer)
cv2.waitKey(10000000)"""