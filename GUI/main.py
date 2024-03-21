import math
import time
import os
import sys
import customtkinter as ctk
import cv2
import numpy as np
import tkinter as tk
import nibabel as nib
import matplotlib.pyplot as plt
import filters
from tkinter import Toplevel, filedialog
import napari
from PIL import Image, ImageTk, ImageDraw

root = ctk.CTk()

# Window dimensions and centering
window_width = 800
window_height = 620
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
ctk.set_appearance_mode="dark"
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.title("MRI Segmentation Tool")
# Make the window not resizable
root.resizable(False, False)

# Ruta del directorio "temp"
temp_directory = "temp"

# Verificar si el directorio no existe
if not os.path.exists(temp_directory):
    # Crear el directorio "temp" si no existe
    os.makedirs(temp_directory)

# Defining global variables
max_value = 0
pen_color = "#00cd00"
pen_size = 3
gaussian_intensity = 0
k_means_value = 0
file_path = ""
seeds = [] # this wil store all the (x,y,z) points that the user drew over
nii_2d_image = []
nii_3d_image = []
nii_3d_selection = []
nii_display = []
nii_3d_image_original = []
slice_portion = 100
kernel_size_amount = 5
scale_number = 1
delta_factor = 0
threshold_value = 100
isodata_tolerance = 0.001
isodata_threshold = 200
tolerance_value=30

view_mode = ctk.StringVar(value="Axial")
selection_image = Image.new("RGB",(200,200),(0,0,0))

def close_program():
    filters.delete_temp()
    root.destroy()
    sys.exit()
    
root.protocol("WM_DELETE_WINDOW", close_program)

def open_napari():
    global nii_3d_image
    viewer = napari.Viewer()
    viewer.add_image(nii_3d_image, name='3D Image')
    viewer.dims.ndisplay = 3
    
    # Hide the layer controls
    viewer.window.qt_viewer.dockLayerControls.toggleViewAction().trigger()
    viewer.window.qt_viewer.dockLayerList.toggleViewAction().trigger()

    # Show the viewer
    viewer.window.show()

# function to refresh the canva with the lates plot update
def refresh_image():
    global selection_image
    # givin the function time to avoid over-refreshing
    plot_image = Image.open("temp/plot.jpeg")
    
    # adjusting the canvas to be the same size as the plot
    drawing_canvas.config(width=plot_image.width, height=plot_image.height)
    picture_canvas.config(width=plot_image.width, height=plot_image.height)

    # printing the picture in the canvas
    image = ImageTk.PhotoImage(plot_image)
    picture_canvas.image = image
    picture_canvas.create_image(0, 0, image=image, anchor="nw")

# function to plot the readed .nii image
def plot_image():
    global max_value, nii_2d_image, nii_3d_image, pen_color, slice_portion
    
    # selecting a slice out of the 3d image
    if(view_mode.get() == "Coronal"): # im the y axis "Coronal"
        if slice_portion >= 191: slice_portion = 190
        nii_2d_image = nii_3d_image[:,slice_portion,:]
    elif(view_mode.get() == "Axial"): # im the z axis "Axial"
        if slice_portion >= 191: slice_portion = 190
        nii_2d_image = nii_3d_image[:,:,slice_portion]
    elif(view_mode.get() == "Sagittal"): # im the x axis "Sagital"
        if slice_portion >= 168: slice_portion = 167
        nii_2d_image = nii_3d_image[slice_portion,:,:]
        
    # to find the range of the threshold slider
    max_value = np.max(nii_3d_image)
    
    # rotate the figure 90 degrees and resize
    nii_2d_image = np.array(nii_2d_image, dtype=np.float32)
    nii_2d_image = np.rot90(nii_2d_image)
    nii_2d_image = cv2.resize(nii_2d_image, None, fx=2.4, fy=2.4)  # Resize to twice the size

    # Save the images
    plt.imsave("temp/plot.jpeg", nii_2d_image, cmap='gray')
    
    refresh_image()
    
    pen_size_scale.configure(state="normal")
    clear_button.configure(state="normal")
    #filters_button.configure(state="normal")
    slice_slider.configure(state="normal")
    view_dropdown.configure(state="normal")
    segmentation_button.configure(state="normal")
    Tolerance_slider.configure(state="normal")
    filters_button.configure(state="normal")
    label_pen_size.grid(row=9,pady=5)
    pen_size_scale.grid(row=10)
    segmentation_tools_frame.grid(row=13,pady=5,padx=20)
    file_tools_frame.grid(row=14, column=0, pady=25, padx=20)
    restore_button.pack(pady=5,padx=20)
    view_3D_button.pack(pady=5,padx=20)
    save_button.pack(pady=5,padx=20)

def add_image():
    global file_path, nii_2d_image, nii_3d_image_original, nii_3d_image, nii_3d_selection
    filters.delete_temp()
    file_path = filedialog.askopenfilename(filetypes=[("NIfTI files", "*.nii")])
    if file_path:
        try:
            # reading file
            nii_file = nib.load(file_path).get_fdata()
            nii_file.shape
            
            # getting data
            nii_3d_image = nii_file[:,:,:]
            nii_3d_selection = np.zeros_like(nii_3d_image)
            nii_3d_image_original = nii_3d_image
            
            # runs function to update background
            plot_image()
            restore_original()
            
        except Exception as e:
            print("Error loading image:", e)
    else:
        print("No file selected")
        
def change_pen_size(val):
    global pen_size
    pen_size = int(val)
    text_val = "Pen Size: " + str(pen_size)
    label_pen_size.configure(text=text_val)
    
def change_slice_portion(val):
    global slice_portion
    slice_portion = int(val)
    text_val = "Slice: " + str(slice_portion)
    label_slice.configure(text=text_val)
    plot_image()

def change_tolerance_val(val):
    global tolerance_value
    tolerance_value = int(val)
    Tolerance_slider.set(val)
    text_val = "Tolerance: " + str(tolerance_value)
    label_tolerance.configure(text=text_val)

def draw(event):
    global last_x, last_y
    x, y = event.x, event.y
    picture_canvas.create_line(last_x, last_y, x, y, fill=pen_color, width=pen_size*2, capstyle="round", smooth=True)
    
    # Check if selection_canvas exists
    try:
        draw_selection = Image.open("temp/green_mask.png")
    except FileNotFoundError:
        # Create a new image if selection_canvas doesn't exist
        reference = Image.open('temp/plot.jpeg')
        draw_selection = Image.new("RGB", (reference.width, reference.height), (0,0,0))

    
    # Draw on the canvas image
    draw = ImageDraw.Draw(draw_selection)
    draw.line((last_x, last_y, x, y), fill='white', width=pen_size*2)
    drawing_canvas.create_line(last_x, last_y, x, y, fill='white', width=pen_size*2, capstyle="round", smooth=True)
    draw_selection.save("temp/green_mask.png", format='png')
    
    last_x, last_y = x, y

def start_draw(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def end_draw(event):
    global nii_3d_selection, slice_portion, drawing_canvas, seeds
    
    drawings = Image.open("temp/green_mask.png").convert('L')
    drawings_resized = drawings.resize((int(drawings.width/2.4), int(drawings.height/2.4)))
    selection = filters.get_white_pixels(drawings_resized)
    
    # this wil save the anotations in a 3d array copy of the original 3d image
    for coord in selection:
        x, y = coord
        if view_mode.get() == "Coronal":  # eje y "Coronal"
            slice_portion = min(slice_portion, 190)
            point = (y, slice_portion, x)
        elif view_mode.get() == "Axial":  # eje z "Axial"
            slice_portion = min(slice_portion, 190)
            point = (y , x, slice_portion)
        elif view_mode.get() == "Sagittal":  # eje x "Sagital"
            slice_portion = min(slice_portion, 167)
            point = (slice_portion, y, x)

        nii_3d_selection[point] = 200
        seeds.append(point)
        
    os.remove("temp/green_mask.png")

def restore_original():
    global nii_3d_image, nii_3d_image_original
    nii_3d_image = nii_3d_image_original
    plot_image()     

def save_file():
    global nii_3d_image
    # obtain the data
    data = nii_3d_image
    
    # Open dialog window to save the file
    file_path = filedialog.asksaveasfilename(defaultextension=".nii", filetypes=[("NIfTI files", "*.nii"), ("All files", "*.*")])
    
    # If the user cancels, the path will be empty
    if not file_path:
        return
    
    # Create a NIfTI From the data
    nii_file = nib.Nifti1Image(data, np.eye(4))  # Reemplaza 'np.eye(4)' con tu transformación afín si es necesario
    nib.save(nii_file, file_path)

def erase_selection():
    global nii_3d_selection, nii_3d_image
    nii_3d_selection = np.zeros_like(nii_3d_image)
    plot_image = Image.open("temp/plot.jpeg")
    drawing_canvas.delete("all")
    refresh_image()     

def apply_segmentation():
    global nii_3d_image, tolerance_value, seeds
    
    nii_3d_image = filters.regionGrowing(nii_3d_image, tolerance_value, seeds)
    plot_image()

def filters_window():
    
    global nii_2d_image, nii_3d_image
    
    ploted_image = Image.open('temp/plot.jpeg').convert('L')
    ploted_array = np.array(ploted_image)
    
    def restore_sliders():
        global threshold_value,gaussian_intensity,slice_portion,kernel_size_amount, scale_number, delta_factor
        gaussian_intensity=0
        gaussian_slider.set(0)
        threshold_slider.set(100)
        isodata_threshold_slider.set(100)
        
        
    def apply_isodata():
        global nii_3d_image,isodata_threshold, isodata_tolerance
        nii_3d_image = filters.isodata(nii_3d_image,isodata_threshold,isodata_tolerance)
        plot_image()

    def change_gaussian_val(val):
        global gaussian_intensity
        # Truncate intensity to ensure it's an integer and make it odd
        kernel_size = max(1, math.trunc(val))
        if kernel_size % 2 == 0:
            kernel_size += 1  # Make it odd if it's even
        gaussian_intensity = kernel_size
        filters.gaussian2d(ploted_array,gaussian_intensity)
        text_val = "Gaussian Intensity: " + str(gaussian_intensity)
        label_Gaussian.configure(text=text_val)
        refresh_image()
              
    def change_k_val(val):
        global k_means_value
        k_means_value = max(1, math.trunc(val))
        text_val = "Random Points: " + str(k_means_value)
        label_K_means.configure(text=text_val)
        
    
    def change_threshold_val(val):
        global threshold_value, nii_2d_image
        threshold_value = int(val)
        text_val = "Threshold: " + str(threshold_value)
        label_Threshold.configure(text=text_val)
        filters.thresholding2d(nii_2d_image, threshold_value)
        refresh_image()
        
    def apply_threshold():
        global threshold_value, nii_3d_image
        nii_3d_image = filters.thresholding(nii_3d_image,threshold_value)
        plot_image()
        
    def change_isodata_threshold_val(val):
        global isodata_threshold
        isodata_threshold = int(val)
        text_val = "Isodata Threshold: " + str(isodata_threshold)
        label_Isodata.configure(text=text_val)
             
    def change_isodata_tolerance_val(val):
        global isodata_tolerance
        isodata_tolerance = int(val)
        if isodata_tolerance == 0 : isodata_tolerance = 0.001
        text_val = "Tolerance: " + str(isodata_tolerance)
        label_Isodata_tolerance.configure(text=text_val)
    
    def apply_gaussian_3d():
        global nii_3d_image, gaussian_intensity
        nii_3d_image = filters.gaussian3d(nii_3d_image,gaussian_intensity)
        plot_image()
    
    def apply_k_means():
        global nii_3d_image, k_means_value
        nii_3d_image = filters.kmeans_segmentation_3d(nii_3d_image, k_means_value)
        #nii_3d_image = filters.k_means(nii_3d_image,k_means_value)
        plot_image()
    
    def cancel_filter():
        plot_image()
        restore_sliders()
        filters_window.destroy()
        filters_button.configure(state="normal")

    
    # Toplevel object which will 
    # be treated as a new window
    filters_window = Toplevel(root)
    
    # deactivate the filters button while this windows is open to avoid repeated instances
    filters_button.configure(state="disabled")
    filters_window.protocol("WM_DELETE_WINDOW", cancel_filter)
    
    # sets the title of the
    # Toplevel widget
    filters_window.title("Image Filters Selector")
 
    # sets the geometry of toplevel
    filters_window.geometry("350x420")
    filters_window.resizable(True, False)
    # Set the maximum width of the window
    filters_window.maxsize(700, filters_window.winfo_screenheight())

    # spacer
    ctk.CTkLabel(master=filters_window,text="Filtering Options", height=40).pack(pady=15)
    
    # frame grid for filters
    filters_frame = ctk.CTkScrollableFrame(master=filters_window, width=300,height=230, orientation="horizontal")
    filters_frame.pack(fill="x", expand=True, padx=15)
    
    # Gaussian frame
    gaussian_frame = ctk.CTkFrame(master=filters_frame)
    gaussian_frame.grid(row=0, column=0, padx=15, pady=5)
    #gaussian_frame.pack()
    
    # Gaussian slider
    gaussian_label = ctk.CTkLabel(master=gaussian_frame, text="Gaussian Options", height=10)
    gaussian_label.pack(pady=15)

    # Label for the Gaussian slider
    text_val = "Gaussian intensity: " + str(gaussian_intensity)
    label_Gaussian = ctk.CTkLabel(master=gaussian_frame, text=text_val)
    label_Gaussian.pack()

    # Gaussian filter slider
    gaussian_slider = ctk.CTkSlider(master=gaussian_frame, from_=1, to=13 , command=change_gaussian_val, width=120)
    gaussian_slider.set(0)
    gaussian_slider.pack(pady=5)
    
    # Gaussian button
    gaussian_button = ctk.CTkButton(master=gaussian_frame, text="Apply Gaussian", command=apply_gaussian_3d, width=120)
    gaussian_button.pack(pady=5)
    
    # K-means frame
    k_means_frame = ctk.CTkFrame(master=filters_frame)
    k_means_frame.grid(row=0, column=1, padx=15, pady=5)
    
    # K-means slider
    k_means_label = ctk.CTkLabel(master=k_means_frame, text="K-means Options", height=10)
    k_means_label.pack(pady=15)

    # Label for the K-means slider
    text_val = "Random Points: " + str(k_means_value)
    label_K_means = ctk.CTkLabel(master=k_means_frame, text=text_val)
    label_K_means.pack()

    # K-means filter slider
    k_means_slider = ctk.CTkSlider(master=k_means_frame, from_=0, to=10, command=change_k_val, width=120)
    k_means_slider.set(0)
    k_means_slider.pack(pady=5)
    
    # K-means button
    k_means_button = ctk.CTkButton(master=k_means_frame, text="Apply K-means", command=apply_k_means, width=120)
    k_means_button.pack(pady=5)
    
    # Thresholding frame
    thresholding_frame = ctk.CTkFrame(master=filters_frame)
    thresholding_frame.grid(row=0, column=2, padx=15, pady=5)
    
    # Thresholding options
    gaussian_label = ctk.CTkLabel(master=thresholding_frame, text="Thresholding Options", height=10)
    gaussian_label.pack(pady=15)

    # Label for the Thresholding slider
    text_val = "Threshold: " + str(threshold_value)
    label_Threshold = ctk.CTkLabel(master=thresholding_frame, text=text_val)
    label_Threshold.pack()

    # Threshold  slider
    threshold_slider = ctk.CTkSlider(master=thresholding_frame, from_=0, to=max_value, command=change_threshold_val, width=120)
    threshold_slider.set(100)
    threshold_slider.pack(pady=5)
    
    # An apply button for Threshold iterations
    threshold_apply_button = ctk.CTkButton(master=thresholding_frame, text ="Apply Threshold", command=apply_threshold)
    threshold_apply_button.pack(pady=5)
    
    buttons_frame = tk.Frame(master=filters_window)
    buttons_frame.pack(pady=25)
    
    
    # Isodata frame
    isodata_frame = ctk.CTkFrame(master=filters_frame)
    isodata_frame.grid(row=0, column=3, padx=15, pady=5)
    #gaussian_frame.pack()
    
    # isodata options label
    isodata_label = ctk.CTkLabel(master=isodata_frame, text="Isodata Options", height=10)
    isodata_label.pack(pady=15)

    # Label for the Gaussian slider
    text_val = "Treshold: " + str(isodata_threshold)
    label_Isodata = ctk.CTkLabel(master=isodata_frame, text=text_val)
    label_Isodata.pack()

    # Isodata threshold slider
    isodata_threshold_slider = ctk.CTkSlider(master=isodata_frame, from_=0, to=max_value, command=change_isodata_threshold_val, width=120)
    isodata_threshold_slider.set(100)
    isodata_threshold_slider.pack(pady=5)
    
    # Label for the isodata tolerance slider
    text_val = "Tolerance: " + str(isodata_tolerance)
    label_Isodata_tolerance = ctk.CTkLabel(master=isodata_frame, text=text_val)
    label_Isodata_tolerance.pack()

    # Isodata tolerance slider
    isodata_tolerance_slider = ctk.CTkSlider(master=isodata_frame, from_=0.1, to=10, number_of_steps=1000, command=change_isodata_tolerance_val, width=120)
    isodata_tolerance_slider.set(0.001)
    isodata_tolerance_slider.pack(pady=5)
    
    # An apply button for isodata iterations
    isodata_apply_button = ctk.CTkButton(master=isodata_frame, text ="Apply Isodata", command=apply_isodata)
    isodata_apply_button.pack(pady=5)
    
    # cancel Button
    cancel_filter_button = ctk.CTkButton(master=buttons_frame, text="Close",  command=cancel_filter)
    cancel_filter_button.grid(row=0, column=0, padx=5, pady=5)
    
    # restore filters button
    restore_button_filter = ctk.CTkButton(buttons_frame, text="Restore Original", command=restore_original)
    restore_button_filter.grid(row=0, column=1, padx=5, pady=5)

# left Frame which contains the tools and options
left_frame = ctk.CTkFrame(root, height=screen_height)
left_frame.pack(side='left', fill='y')

# Create a Canvas widget for left frame
left_frame_canvas = ctk.CTkFrame(left_frame, height=screen_height)
left_frame_canvas.pack(side='left', fill='both', expand=True)

# diferent Canvas overlaped on the rest of the window
# the main canvas frame
right_frame = ctk.CTkFrame(root, width=750, height=600)
right_frame.pack(pady=10, padx=10, fill="both", expand=True)

# the main canvas frame
canvas_frame = ctk.CTkFrame(right_frame, width=750, height=600)
canvas_frame.pack(pady=10, padx=10)

# the picture canvas where we show the image (under the drawing canvas)
picture_canvas = ctk.CTkCanvas(canvas_frame, width=750, height=600)
picture_canvas.pack()

# the drawing canvas where we keep the user selection (not shown)
drawing_canvas = ctk.CTkCanvas(canvas_frame, width=750, height=600)

# frame that contains the canvas tools
canva_tools_frame = ctk.CTkFrame(right_frame, width=750, height=600)
canva_tools_frame.pack(pady=10, padx=10, fill="x", expand=True)

canva_tools_frame.rowconfigure(1, weight=1)
canva_tools_frame.columnconfigure(0, weight=1)
canva_tools_frame.columnconfigure(1, weight=1)
canva_tools_frame.columnconfigure(2, weight=1)

# frame for buttons
tools_button_frame = tk.Frame(canva_tools_frame)
tools_button_frame.grid(row=0,column=0,pady=5)

# Clear canva button
clear_button = ctk.CTkButton(tools_button_frame, text="Clear Selection", state="disabled", command=erase_selection)
clear_button.pack(pady=5)

# Filters button
filters_button = ctk.CTkButton(tools_button_frame, text="More Filters", command=filters_window)
filters_button.pack(pady=5)

view_frame = tk.Frame(canva_tools_frame)
view_frame.grid(row=0,column=1,pady=5)

# Define the options for the dropdown
view_options = ["Axial", "Coronal", "Sagittal"]

def handle_dropdown_selection(selection):
    view_mode.set(selection)
    plot_image()    

# view mode label
title_label = ctk.CTkLabel(view_frame, text="View Mode:")
title_label.pack(padx=10)

# Create the custom dropdown
view_dropdown = ctk.CTkComboBox(master=view_frame, variable=view_mode, values=view_options, command=handle_dropdown_selection, state="disabled")
view_dropdown.pack(padx=10)

# slice frame
slice_frame = tk.Frame(canva_tools_frame)
slice_frame.grid(row=0,column=2,pady=5)

# Label for the slider
text_val = "Slice: " + str(slice_portion)
label_slice = ctk.CTkLabel(master=slice_frame, text=text_val)
label_slice.pack( padx=10)

# slider
slice_slider = ctk.CTkSlider(master=slice_frame, from_=1, to=190,state="disabled", command=change_slice_portion, width=120)
slice_slider.set(slice_portion)
slice_slider.pack( padx=10)



# Logo
logo_frame = tk.Frame(master=left_frame_canvas)
logo_frame.grid(row=0, pady=15, padx=30)
canvas_logo = ctk.CTkCanvas(master=logo_frame, width=100, height=100)
canvas_logo.grid(row=0)
logo_image = tk.PhotoImage(file="images/logo.png").subsample(4, 4)
canvas_logo.create_image(50, 50, image=logo_image)

# Title of the tool under the logo
title_label = ctk.CTkLabel(logo_frame, text="MRI Slice \n Segmentation Tool \n (beta)")
title_label.grid(row=1, pady=5)

# Upload Button
upload_button = ctk.CTkButton(left_frame_canvas, text='Upload Image', command=add_image)
upload_button.grid(row=2,pady=10, padx=20)

# Pen size slider
# Label for the slider
text_val = "Pen Size: " + str(pen_size)
label_pen_size = ctk.CTkLabel(master=left_frame_canvas, text=text_val)

# slider
pen_size_scale = ctk.CTkSlider(master=left_frame_canvas, from_=1, to=13,state="disabled", command=change_pen_size, width=120)
pen_size_scale.set(pen_size)



# Frame for segmentation tools
segmentation_tools_frame = tk.Frame(master=left_frame_canvas)

# Label for the tolerance slider
text_val = "Tolerance: " + str(tolerance_value)
label_tolerance = ctk.CTkLabel(master=segmentation_tools_frame, text=text_val)
label_tolerance.pack(pady=5)

# slider tolerance
Tolerance_slider = ctk.CTkSlider(master=segmentation_tools_frame, from_=1, to=100,state="disabled", command=change_tolerance_val, width=120)
Tolerance_slider.set(30)
Tolerance_slider.pack(pady=5)

# Process image segmentation button
segmentation_button = ctk.CTkButton(segmentation_tools_frame, text="Apply Region Growing", state="disabled", command=apply_segmentation)
segmentation_button.pack(pady=20)

# file tools frame
file_tools_frame = tk.Frame(left_frame_canvas)

# Clear canva button
restore_button = ctk.CTkButton(file_tools_frame, text="Restore Original", command=restore_original)

# 3D view button
view_3D_button = ctk.CTkButton(file_tools_frame,text="3D View",command=open_napari)

# Process image segmentation button
save_button = ctk.CTkButton(file_tools_frame, text="Save NIfTI", command=save_file)

picture_canvas.bind("<Button-1>", start_draw)
picture_canvas.bind("<B1-Motion>", draw)
picture_canvas.bind("<ButtonRelease-1>", end_draw)


root.mainloop()