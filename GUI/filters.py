import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import cv2

def gaussian(data):
   data = cv2.GaussianBlur(data,(13,13),0)
   # plotting data
   plt.imshow(data)
   plt.axis('off')
   plt.imsave("output/plot.png", data
               , cmap='gray'
               )
   print("gaussian applied")
   
def laplacian(data):
   data = cv2.Laplacian(data, -1, ksize=5, scale=1,delta=0, borderType=cv2.BORDER_DEFAULT)
   plt.imshow(data)
   plt.axis('off')
   plt.imsave("output/plot.png", data
               , cmap='gray'
               )
   print("laplacian applied")