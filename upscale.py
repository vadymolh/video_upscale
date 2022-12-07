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


# Read image
""" timer = time.time()
img = cv2.imread("test1.jpg")
sr = cv2.dnn_superres.DnnSuperResImpl_create()
 
path = "LapSRN_x8.pb"
 
sr.readModel(path)
 
sr.setModel("lapsrn",8)
 
result = sr.upsample(img)
print(f"TIME: {time.time() - timer}")
plt.figure(figsize=(12,8))
plt.subplot(1,3,1)
# Original image
plt.imshow(img[:,:,::-1])
plt.subplot(1,3,2)
# SR upscaled
plt.imshow(result[:,:,::-1])
plt.show()"""