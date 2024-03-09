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

def get_white_pixels(image):
    # Convert image to grayscale if it's not already
    if image.mode != "L":
        image = image.convert("L")

    # Get image dimensions
    width, height = image.size

    # Initialize list to store white pixel coordinates
    white_pixels = []

    # Iterate through image pixels
    for y in range(height):
        for x in range(width):
            # Get pixel value
            pixel = image.getpixel((x, y))
            # Check if pixel is white (255)
            if pixel == 255:
                white_pixels.append((x, y))

    return white_pixels

def regionGrowing(image, threshold):
   # Create a mask to keep track of visited pixels
   visited_mask = np.zeros_like(image, dtype=bool)

   # Get image dimensions
   height, width = image.shape[:2]
   # Initialize segmented image
   segmented_image = np.zeros_like(image)

   # Define 4-connectivity neighbors
   neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)
               #,(-1,-1),(1,1),(-1,1),(1,-1) #it works the same with 8 or 4 neighbors, still dont know which one is more efficient
               ]
   # Load PNG image of selected region
   selected_image = Image.open("temp/green_mask.png")

   # load visited mask png image
   visited_image = Image.open("temp/visited_mask.png").convert('L')
   visited_tuples = get_white_pixels(visited_image)
   # Set visited pixels to True in the mask
   for x, y in visited_tuples:
      visited_mask[y, x] = True

   # Perform region growing
   starting_list = get_white_pixels(selected_image)
   stack = starting_list
   count = 0
   seed_value = 0
   while stack:
      x, y = stack.pop()
      segmented_image[y, x] = 255  # Mark pixel as part of the segmented region
      visited_mask[y, x] = True  # Mark pixel as visited
      
      # Update seed value and count for dynamic mean calculation
      count += 1
      seed_value += (image[y, x] - seed_value) / count

      # Check 4-connectivity neighbors
      for dx, dy in neighbors:
         nx, ny = x + dx, y + dy
         # Check if neighbor is within image bounds and not visited
         if 0 <= nx < width and 0 <= ny < height and not visited_mask[ny, nx]:
               # Check intensity difference
               if abs(int(image[ny, nx]) - int(seed_value)) < threshold:
                  stack.append((nx, ny))
                    
   # GrownRegion image
   grownRegion_fig = plt.figure(facecolor='black')
   grownRegion_image_plot = grownRegion_fig.add_subplot(111)
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   grownRegion_image_plot.imshow(segmented_image, cmap='gray')
   plt.savefig("temp/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)