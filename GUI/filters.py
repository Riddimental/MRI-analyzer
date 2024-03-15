import math
import time
import numpy as np
import nibabel as nib
#np.set_printoptions(threshold=sys.maxsize)
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import os
import shutil

def delete_temp():
   # Delete the contents of the temp folder
   folder_path = "temp"

   # Check if the folder exists
   if os.path.exists(folder_path):
      # Iterate over the files in the folder and delete them
      for filename in os.listdir(folder_path):
         file_path = os.path.join(folder_path, filename)
         try:
               if os.path.isfile(file_path):
                  os.unlink(file_path)
               elif os.path.isdir(file_path):
                  shutil.rmtree(file_path)
         except Exception as e:
               print(f"Failed to delete {file_path}. Reason: {e}")
   else:
      print(f"The folder {folder_path} does not exist.")

def gaussian(data, intensity):
   data = cv2.GaussianBlur(data,(math.trunc(intensity),math.trunc(intensity)),0)
   #print("data",data)
   plt.imshow(data, cmap="gray")
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   plt.savefig("temp/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
   
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
   
def isodata(image_data, threshold_0=200, tolerance= 0.001):
   iteraciones = 0
   threshold = threshold_0
   # print("data",image_data[0,1])

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
   plt.imshow(data, cmap="gray")
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   plt.savefig("temp/plot.png", format='png', dpi= 120, bbox_inches='tight', pad_inches=0)

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

def regionGrowing2D(image, threshold):
   # Create a mask to keep track of visited pixels
   visited_mask = np.zeros_like(image, dtype=bool)

   # Get image dimensions
   height, width = image.shape[:2]
   # Initialize segmented image
   segmented_image = np.zeros_like(image)

   # Define 4-connectivity neighbors
   neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)
               ,(-1,-1),(1,1),(-1,1),(1,-1) #it works the same with 8 or 4 neighbors, still dont know which one is more efficient
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
   
def regionGrowing3D(image3d, threshold, slice, view_mode):
   # Get image dimensions
   height_x, width_y, depth_z = image3d.shape
   
   # Create a mask to keep track of visited pixels
   visited_3dmask = np.zeros_like(image3d, dtype=bool)
   #print("visited shape",visited_3dmask.shape) #visited shape (176, 192, 192)

   # Initialize segmented image
   segmented_3dimage = np.zeros_like(image3d)

   # Define 3d 6-connectivity neighbors
   # center is (0,0,0)
   neighbors6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
   
   # Define 3d 26-connectivity neighbors
   # center is (0,0,0)
   #neighbors26 = [(dx, dy, dz) for dx in range(-1, 2) for dy in range(-1, 2) for dz in range(-1, 2) if (dx, dy, dz) != (0, 0, 0)]
   #print(neighbors2)
   
   # Load PNG image of selected region
   selected_image = Image.open("temp/green_mask.png").transpose(Image.FLIP_TOP_BOTTOM)
   #print("selected size:", selected_image.size)  # selected size: (406, 443)

   # load visited mask png image
   visited_image = Image.open("temp/visited_mask.png").convert('L')
   if view_mode == "Coronal":  # im the y axis
      new_size = (176, 192)
   elif view_mode == "Axial":  # im the z axis
      new_size = (176, 192)
   elif view_mode == "Sagittal":  # im the x axis
      new_size = (192, 192)

   # Resize the selected and visited images
   selected_image = selected_image.resize(new_size)
   visited_image = visited_image.resize(new_size)
   
   #print("selected image new shape is", visited_image.size)
   starting_tuples = get_white_pixels(selected_image)
   starting_triples = []

   visited_tuples = get_white_pixels(visited_image)
   visited_triples = []
   
   # Set visited pixels to True in the mask depending on the slice and the viewing angle
   # and setting the selection plane depending on how it was shown to the user
   if(view_mode == "Coronal"): # im the y axis, bottom to top
      # Transform list of tuples into triples
      visited_triples = [(x, slice, y) for x, y in visited_tuples]
      starting_triples = [(x, slice, y) for x, y in starting_tuples]
      for x, y, z in visited_triples:
         visited_3dmask[x, y, z] = True
   elif(view_mode == "Axial"): # im the z axis, back to front
      visited_triples = [(x, y, slice) for x, y in visited_tuples]
      starting_triples = [(x, y, slice) for x, y in starting_tuples]
      for x, y, z in visited_triples:
         visited_3dmask[x, y, z] = True
   elif(view_mode == "Sagittal"): # im the x axis, left to right
      visited_triples = [(slice, x, y) for x, y in visited_tuples]
      starting_triples = [(slice, x, y) for x, y in starting_tuples]
      for x, y, z in visited_triples:
         visited_3dmask[x, y, z] = True
   

   # Perform region growing
   stack = starting_triples
   count = 0
   seed_value = 0
   while stack:
      x, y, z = stack.pop()
      segmented_3dimage[x, y, z] = 255  # Mark pixel as part of the segmented region
      visited_3dmask[x, y, z] = True  # Mark pixel as visited
      
      # Update seed value and count for dynamic mean calculation
      count += 1
      seed_value += (image3d[x, y, z] - seed_value) / count

      # Check 3d 6-connectivity neighbors
      for dx, dy, dz in neighbors6:
         nx, ny, nz = x + dx, y + dy, z + dz
         # Check if neighbor is within image bounds and not visited
         if 0 <= ny < width_y and 0 <= nx < height_x and 0 <= nz < depth_z and not visited_3dmask[nx, ny, nz]:
               # Check intensity difference
               if abs(int(image3d[nx, ny, nz]) - int(seed_value)) < threshold:
                  stack.append((nx, ny, nz))
                    
   # GrownRegion image
   grownRegion_fig = plt.figure(facecolor='black')
   grownRegion_image_plot = grownRegion_fig.add_subplot(111)
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)

   # Rotar la imagen 90 grados en sentido horario intercambiando las dimensiones
   if view_mode == "Coronal":  # im the y axis
      rotated_image = np.rot90(segmented_3dimage[:, slice, :])
   elif view_mode == "Axial":  # im the z axis
      rotated_image = np.rot90(segmented_3dimage[:, :, slice])
   elif view_mode == "Sagittal":  # im the x axis
      rotated_image = np.rot90(segmented_3dimage[slice, :, :])

   grownRegion_image_plot.imshow(rotated_image, cmap='gray')
   plt.savefig("temp/plot.png", format='png', dpi=120, bbox_inches='tight', pad_inches=0)
   
   # Assuming your 3D matrix is named 'matrix'
   # Create a NIfTI image object
   #nii_output = nib.Nifti1Image(segmented_3dimage, affine=np.eye(4))

   # Save the NIfTI image to a file
   #nib.save(nii_output, 'output/output.nii')
   return segmented_3dimage
