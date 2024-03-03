import math
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import cv2

def gaussian(data, intensity):
   data = cv2.GaussianBlur(data,(math.trunc(intensity),math.trunc(intensity)),0)
   plt.imshow(data, cmap="gray")
   plt.axis('off')
   plt.savefig("output/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
   print("gaussian applied")
   
def laplacian(data):
   data = cv2.Laplacian(data, -1, ksize=5, scale=1,delta=0, borderType=cv2.BORDER_DEFAULT)
   plt.imshow(data, cmap="gray")
   plt.axis('off')
   plt.savefig("output/plot.png", format='png', dpi= 120, bbox_inches='tight', pad_inches=0)
   print("laplacian applied")