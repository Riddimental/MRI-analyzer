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
from sklearn.cluster import KMeans

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

def gaussian2d(data, intensity):
   data = cv2.GaussianBlur(data,(intensity,intensity),0)
   plt.imshow(data, cmap="gray")
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   plt.savefig("temp/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
   #plt.close()
   
def kmeans_segmentation_3d(image3d, num_clusters):
   # Obtener la forma original de la imagen 3D
   original_shape = image3d.shape
   # Reshape la imagen 3D en un array 2D para aplicar K-means
   image_2d = image3d.reshape(-1, original_shape[-1])

   # Aplica K-means
   kmeans = KMeans(n_clusters=num_clusters, random_state=0)
   kmeans.fit(image_2d)

   # Obtiene las etiquetas de cluster asignadas a cada píxel
   labels = kmeans.labels_
   # Reconstruye las etiquetas en la forma original de la imagen 3D
   segmented_image = labels.reshape(labels[0]/original_shape[1],labels[0]/original_shape[0],labels[1])
   return segmented_image

def gaussian3d(data3D, intensity):
   data = cv2.GaussianBlur(data3D,(intensity,intensity),0)
   return data
   
def thresholding(data, threshold):
   transformed_image = data > threshold
   return transformed_image
   
def thresholding2d(data, threshold):
   transformed_image = data > threshold
   plt.imshow(transformed_image, cmap="gray")
   plt.xticks([])
   plt.yticks([])
   time.sleep(0.0016)
   plt.savefig("temp/plot.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)

def isodata(image_data, threshold_0=200, tolerance= 0.001):
   iteraciones = 0
   threshold = threshold_0
   
   while True:

      # Thresholding
      iterated_image = image_data > threshold

      # find the mean
      m_region_of_interest = image_data[iterated_image == 1].mean()
      m_background = image_data[iterated_image == 0].mean()

      new_threshold = 0.5 * (m_region_of_interest + m_background)

      if abs(new_threshold - threshold) < tolerance:
         break
  
      iteraciones = iteraciones + 1

      threshold = new_threshold
      
   return iterated_image

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
   #plt.close()
   
def regionGrowing3D(image3d, threshold, slice, view_mode):
   # Get image dimensions
   height_x, width_y, depth_z = image3d.shape
   
   # Create a mask to keep track of visited pixels
   visited_3dmask = np.zeros_like(image3d, dtype=bool)

   # Initialize segmented image
   segmented_3dimage = np.zeros_like(image3d)

   # Define 3d 6-connectivity neighbors
   # center is (0,0,0)
   neighbors6 = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
   
   # Load PNG image of selected region
   selected_image = Image.open("temp/green_mask.png").transpose(Image.FLIP_TOP_BOTTOM)

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
   #plt.close()

   return segmented_3dimage

def select_random_points(array3d, k):
    # Flatten the 3D array to 1D
    flat_indices = np.random.choice(array3d.size, k, replace=False)
    
    # Convert flat indices to 3D indices
    x_indices, y_indices, z_indices = np.unravel_index(flat_indices, array3d.shape)
    
    # Stack x, y, and z values together to form random points
    points = np.column_stack((x_indices, y_indices, z_indices))
    
    # Return the selected random points
    return points
 
def k_means3d(image3D, k=3, max_iters=300, tol=1e-4):
   
   segmented_image = np.zeros_like(image3D)
   
   max_value = np.max(image3D)

   intensity = int(max_value / k)  # Fixed calculation of intensity

   amount = 0

   colors = [0] * k  # Initialize colors list
   
   seed = select_random_points(image3D, k) # this is an array of 3D points (x,y,z)
   
   means = [0] * k

   for i in range(len(seed)):
      point = seed[i]
      means[i] = image3D[point[0], point[1], point[2]]  # Accessing the value at the 3D point
   

   for i in range(k):
      colors[i] = amount
      amount += intensity
   
   
   for x, y, z in np.ndindex(image3D.shape):
      # take the vector
      point = np.array([x, y, z])
      # Calculate distance from the current value to each value in the means group
      point_distances = np.linalg.norm(point - seed)
      # Find the index of the closest point
      closest_index = np.argmin(point_distances)
      # Store the index of the closest point
      segmented_image[x, y, z] = colors[closest_index]

   return segmented_image