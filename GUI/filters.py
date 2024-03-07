import math
import sys
import time
import nibabel as nib
import numpy as np
#np.set_printoptions(threshold=sys.maxsize)
import matplotlib.pyplot as plt
from PIL import Image, ImageTk, ImageDraw
import cv2

def gaussian(data, intensity):
   data = cv2.GaussianBlur(data,(math.trunc(intensity),math.trunc(intensity)),0)
   #print("data",data)
   plt.imshow(data, cmap="gray")
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   plt.savefig("temp/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
   #print("gaussian applied")
   
def thresholding(data, threshold):
   transformed_image = data > threshold
   #print(transformed_image)
   transformed_fig = plt.figure(facecolor='black')
   transformed_image_plot = transformed_fig.add_subplot(111)
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   transformed_image_plot.imshow(transformed_image, cmap='gray')
   plt.savefig("temp/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
   #print("threshold applied")
   
def isodata(image_data, threshold_0=200, tolerance= 0.001):
   iteraciones = 0
   threshold = threshold_0
   print("data",image_data[0,1])

   while True:

      # umbralizacion
      iterated_image = image_data > threshold

      # hallamos el promedio
      m_region_of_interest = image_data[iterated_image == 1].mean()
      m_background = image_data[iterated_image == 0].mean()

      new_threshold = 0.5 * (m_region_of_interest + m_background)

      if abs(new_threshold - threshold) < tolerance:
         break
  
      iteraciones = iteraciones + 1

      threshold = new_threshold
      #print("nuevo threshold",new_threshold)
      
   
   # isodata image
   isodata_fig = plt.figure(facecolor='black')
   isodata_image_plot = isodata_fig.add_subplot(111)
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   isodata_image_plot.imshow(iterated_image, cmap='gray')
   plt.savefig("temp/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
   #print("Isodata applied")
   return new_threshold
   
def laplacian(data,inksize,inscale,indelta):
   data = cv2.Laplacian(data, -1, ksize=inksize, scale=inscale, delta=indelta, borderType=cv2.BORDER_DEFAULT)
   #data = cv2.Laplacian(data, -1, ksize=5, scale=1,delta=0, borderType=cv2.BORDER_DEFAULT)
   plt.imshow(data, cmap="gray")
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   plt.savefig("temp/plot.png", format='png', dpi= 120, bbox_inches='tight', pad_inches=0)
   #print("laplacian applied")

# Region Growing


# Distance Function to calculate how similar two pixels are
def distance(x0,y0,x1,y1,Imagen_data):
   print(Imagen_data.shape)
   return abs(Imagen_data[x1,y1] - Imagen_data[x0,y0])

# obtain the 4 neighbours of a pixel considering the size of the image
def N4(x0,y0,M,N):
   neighborhood = []
   # right border
   if x0+1 < M: neighborhood.append((x0+1,y0))
   # left border
   if x0-1 > 0: neighborhood.append((x0-1,y0))
   # lower border
   if y0+1 < N: neighborhood.append((x0,y0+1))
   # upper border
   if y0-1 > 0: neighborhood.append((x0,y0-1))
   return neighborhood

# obtain the neighbours of a pixel considering the size of the image
def N8(x0,y0,M,N):
   neighborhood = []
   # right border
   if x0+1 < M: neighborhood.append((x0+1,y0))
   # left border
   if x0-1 > 0: neighborhood.append((x0-1,y0))
   # lower border
   if y0+1 < N: neighborhood.append((x0,y0+1))
   # upper border
   if y0-1 > 0: neighborhood.append((x0,y0-1))
   # right upper corner
   if x0+1 < M and y0-1 > 0: neighborhood.append((x0+1,y0-1))
   # left upper corner
   if x0-1 > 0 and y0-1 > 0: neighborhood.append((x0-1,y0-1))
   # right lower corner
   if x0+1 < M and y0+1 < N: neighborhood.append((x0+1,y0+1))
   # left lower corner
   if x0-1 > 0 and y0+1 < N: neighborhood.append((x0-1,y0+1))
   #print("neigborhood size ",len(neighborhood), neighborhood)
   return neighborhood

#def regionGrowing(selection_mask, image ,Tolerance , max_iter=1e6):
   mask = np.zeros(image.shape)
   visited = np.zeros(image.shape)
   
   print("mask",selection_mask)
   visited_mask_image = Image.open("temp/visited_mask.png").convert("1")
   visited = np.array(visited_mask_image)
   #print("visited",visited)
   original_image = Image.open("temp/plot.png")
   Image_data = np.array(original_image)
   print("original",Image_data[20,20])
   
   
   # Get non-zero coordinates
   nonzero_coords = []
   for x in range(mask.shape[0]):
      for y in range(mask.shape[1]):
         if mask[x, y] != 0:
               nonzero_coords.append((x, y))
   # print("nonzero", nonzero_coords)
               
   # Get visited coordinates
   visited_coords = []
   for x in range(visited.shape[0]):
      for y in range(visited.shape[1]):
         if visited[x, y] != 0:
               visited_coords.append((x, y))
   #print("visited", visited_coords)
               
   #print("size",selection_mask.width, selection_mask.height)
   # actual size of the image
   N,M = image.shape
   #print("m y n son",M,N)

   # define a queue where the points to be procesed goes
   neighbor_queue = nonzero_coords
   
   #print("neighbors",neighbor_queue )

   iterations = 0

   # This will run until the neighbor list is empty
   while len(neighbor_queue) > 0:
      # Get the first element of the list
      x0, y0 = neighbor_queue.pop()

      # Iterate over the neighbors
      for x1, y1 in N4(x0, y0, M, N):
         if 0 <= x1 < M and 0 <= y1 < N and abs(Image_data[x1, y1,0] - Image_data[x0, y0,0]) <= Tolerance and np.all(mask[x1, y1,0] == 0) and np.all(visited[x1, y1,0] == 0):
            print('yes')
            neighbor_queue.append((x1, y1))

      mask[x0, y0,:] = 1
      visited[x0, y0,:] = 1
      iterations += 1

      if iterations > max_iter:
         print("overgrown")
         break

   growing_fig = plt.figure(facecolor='black')
   growing_image_plot = growing_fig.add_subplot(111)
   growing_image_plot.imshow(mask, cmap='gray')
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   plt.savefig("temp/plot.png", format='png', dpi=120, bbox_inches='tight', pad_inches=0)
   
   #return mask


def regionGrowing(Image_data ,Tolerance, max_iter):
   mask = np.zeros(Image_data.shape)
   visited = np.zeros(Image_data.shape)
   #print("mask size",mask.shape)
   
   mask_image = Image.open("temp/green_mask.png").convert('L')
   mask_array = np.array(mask_image)
   #print("dato?",mask_array)
   # get coordenates where the pixel has a value above 0
   true_coords = list(zip(*np.where(mask_array > 0)))
   #print("las tuplas",true_coords)
   
   N,M = Image_data.shape
   
   neighbors_queue = []
   neighbors_queue = true_coords
   #neighbors_queue.append(true_coords)
   #print("neigh queue", neighbors_queue)
    
   iterations = 0
   
   while neighbors_queue:
      x0,y0 = neighbors_queue.pop()
      print(x0,y0)
      for x1,y1 in N4(x0,y0,M,N):
         if(distance(x0,y0,x1,y1,Image_data)) <= Tolerance and mask[x1,y1] == 0 and visited[x1,y1] == 0:
            
            print("Dimensiones de Image_data:", Image_data.shape)
            print("Coordenadas (x1, y1):", x1, y1)
            neighbors_queue.append((x1,y1))
      mask[x0,y0] = 1
      visited[x0,y0] = 1
      iterations += 1
      
      if iterations > max_iter:
         print("overgrown")
         break
   
   # GrownRegion image
   grownRegion_fig = plt.figure(facecolor='black')
   grownRegion_image_plot = grownRegion_fig.add_subplot(111)
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   grownRegion_image_plot.imshow(mask, cmap='gray')
   plt.savefig("temp/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
      
   #return mask