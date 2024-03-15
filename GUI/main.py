import math
import time
import os
import sys
import customtkinter as ctk
import numpy as np
import tkinter as tk
import nibabel as nib
import matplotlib.pyplot as plt
import filters
from tkinter import Toplevel, filedialog
from PIL import Image, ImageTk, ImageDraw

root = ctk.CTk()

# Window dimensions and centering
window_width = 800
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
ctk.set_appearance_mode="dark"
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.title("MRI Segmentation Tool")
# Make the window not resizable
root.resizable(False, False)

# Defining global variables
max_value = 0
pen_color = ""
pen_size = 7
gaussian_intensity = 0
file_path = ""
nii_2d_image = []
nii_3d_image = []
nii_display = []
nii_3d_image_original = []
slice_portion = 100
kernel_size_amount = 5
scale_number = 1
delta_factor = 0
threshold_value = 100
isodata_tolerance = 0.001
isodata_threshold = 200
tolerance_value=20


# Radio buttons (0) Axial, (1) Coronal, (2) Sagittal
view_mode = ctk.StringVar(value="Axial")
selection_image = Image.new("RGB",(200,200),(0,0,0))

def close_program():
    filters.delete_temp()
    root.destroy()
    sys.exit()
    
root.protocol("WM_DELETE_WINDOW", close_program)

# function to refresh the canva with the lates plot update
def refresh_image():
    global selection_image
    # givin the function time to avoid over-refreshing
    time.sleep(0.0008)
    plot_image = Image.open("temp/plot.png")
    
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
    
    #mpl.rcParams['savefig.pad_inches'] = 0
    #print(slice_portion)
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
    max_value = nii_2d_image[nii_2d_image > 0].flatten().max()
    
    # plotting data
    plt.axes(frameon=False)
    plt.figure(facecolor='black')
    # rotate the figure 90 degrees
    nii_2d_image = np.rot90(nii_2d_image)
    plt.imshow(nii_2d_image, cmap='gray')
    plt.xticks([])
    plt.yticks([])
    plt.autoscale(tight=True)
    time.sleep(0.0008)
    plt.savefig("temp/plot.png", format='png', dpi= 120, bbox_inches='tight', pad_inches=0)
    plt.savefig("temp/original.png", format='png', dpi= 120, bbox_inches='tight', pad_inches=0)
    
    refresh_image()
    
    mode_switch.configure(state="normal")
    pen_size_scale.configure(state="normal")
    clear_button.configure(state="normal")
    #filters_button.configure(state="normal")
    slice_slider.configure(state="normal")
    view_dropdown.configure(state="normal")
    segmentation_button.configure(state="normal")
    Tolerance_slider.configure(state="normal")
    filters_button.configure(state="normal")
    label_pen_mode.grid(row=7,pady=5)
    mode_switch.grid(row=8, pady=5)
    label_pen_size.grid(row=9,pady=5)
    pen_size_scale.grid(row=10)
    segmentation_tools_frame.grid(row=13,pady=5,padx=20)
    restore_button.grid(row=14,pady=10,padx=20)
    undo_button.grid(row=15,pady=10,padx=20)
    pen_color="#00cd00"
    
def undoIt():
    try:
        os.rename("temp/undo.png", "temp/plot.png")
        refresh_image()
        print("undone")
    except FileNotFoundError:
        print("No undo steps")
    except Exception as e:
        print("An error occurred:", e)

def add_image():
    global file_path, pen_color, nii_2d_image, nii_3d_image_original, nii_3d_image
    filters.delete_temp()
    file_path = filedialog.askopenfilename(filetypes=[("NIfTI files", "*.nii")])
    if file_path:
        try:
            # reading file
            nii_file = nib.load(file_path).get_fdata()
            nii_file.shape
            
            # getting data
            #nii_data = nii_file[:,:,slice_portion]
            nii_3d_image = nii_file[:,:,:]
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
    erase_selection()
    plot_image()

def change_tolerance_val(val):
    global tolerance_value
    tolerance_value = int(val)
    Tolerance_slider.set(val)
    text_val = "Tolerance: " + str(tolerance_value)
    label_tolerance.configure(text=text_val)

def switch_event():
    if(switch_var.get() == "on"):
        include()
    else:
        exclude()

def include():
    global pen_color
    pen_color = "#00cd00"
    
def exclude():
    global pen_color
    pen_color = "#FF0000"

def draw(event):
    global last_x, last_y
    x, y = event.x, event.y
    picture_canvas.create_line(last_x, last_y, x, y, fill=pen_color, width=pen_size*2, capstyle="round", smooth=True)
    
    # Check if selection_canvas exists
    try:
        draw_selection = Image.open("temp/selection_canvas.png")
    except FileNotFoundError:
        # Create a new image if selection_canvas doesn't exist
        reference = Image.open('temp/plot.png')
        draw_selection = Image.new("RGB", (reference.width, reference.height), (0,0,0))

    
    # Draw on the canvas image
    draw = ImageDraw.Draw(draw_selection)
    draw.line((last_x, last_y, x, y), fill=pen_color, width=pen_size*2)
    drawing_canvas.create_line(last_x, last_y, x, y, fill=pen_color, width=pen_size*2, capstyle="round", smooth=True)
    draw_selection.save("temp/selection_canvas.png", format='png')
    
    last_x, last_y = x, y

def start_draw(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def end_draw(event):
    #referencia.save()
    pass
 
def restore_original():
    global pen_color, nii_3d_image, nii_3d_image_original
    picture_canvas.create_image(0, 0, image=picture_canvas.image, anchor="nw")
    plot_original = Image.open("temp/original.png")
    plot_original.save("temp/plot.png", format='png')
    selection_image = Image.new("RGB",(plot_original.width,plot_original.height),(0,0,0))
    pen_color = "#00cd00"
    mode_switch.select()
    nii_3d_image = nii_3d_image_original
    erase_selection()
    plot_image()     

def erase_selection():
    global pen_size, pen_color
    plot_image = Image.open("temp/plot.png")
    drawing_canvas.delete("all")
    selection_image = Image.new("RGB",(plot_image.width,plot_image.height),(0,0,0))
    selection_image.save("temp/selection_canvas.png",format='png')
    selection_image.save("temp/green_mask.png",format='png')
    selection_image.save("temp/red_mask.png",format='png')
    selection_image.save("temp/visited_mask.png",format='png')
    pen_size_scale.set(7)
    pen_color = "#00cd00"
    mode_switch.select()
    refresh_image()     

def filters_window():
    
    global nii_2d_image, nii_3d_image
    
    ploted_image = Image.open('temp/plot.png').convert('L')
    ploted_array = np.array(ploted_image)
    
    def restore_sliders():
        global threshold_value,gaussian_intensity,slice_portion,kernel_size_amount, scale_number, delta_factor
        gaussian_intensity=0
        gaussian_slider.set(0)
        kernel_size_amount=5
        ksize_slider.set(5)
        scale_number=1
        scale_slider.set(1)
        delta_factor=0
        delta_slider.set(0)
        threshold_value=100
        threshold_slider.set(100)
        isodata_threshold_slider.set(100)
        
    def apply_isodata():
        new_threshold = filters.isodata(ploted_array,isodata_threshold,isodata_tolerance)
        change_isodata_threshold_val(new_threshold)
        isodata_threshold_slider.set(new_threshold)
        refresh_image()

    def change_gaussian_val(val):
        global gaussian_intensity
        # Truncate intensity to ensure it's an integer and make it odd
        kernel_size = max(1, math.trunc(val))
        if kernel_size % 2 == 0:
            kernel_size += 1  # Make it odd if it's even
        gaussian_intensity = int(kernel_size)
        filters.gaussian(ploted_array,gaussian_intensity)
        text_val = "Gaussian Intensity: " + str(gaussian_intensity)
        label_Gaussian.configure(text=text_val)
        refresh_image()
              
    def change_ksize_val(val):
        global kernel_size_amount
        kernel_size_amount = int(val)
        filters.laplacian(ploted_array,kernel_size_amount,scale_number, delta_factor)
        text_val = "Kernel Size: " + str(kernel_size_amount)
        label_ksize.configure(text=text_val)
        refresh_image()
        
    def change_scale_val(val):
        global scale_number
        scale_number = int(val)
        filters.laplacian(ploted_array,kernel_size_amount,scale_number, delta_factor)
        text_val = "Scale: " + str(scale_number)
        label_scale.configure(text=text_val)
        refresh_image()
        
    def change_delta_val(val):
        global delta_factor
        delta_factor = int(val)
        filters.laplacian(ploted_array,kernel_size_amount,scale_number, delta_factor)
        text_val = "Delta: " + str(delta_factor)
        label_delta.configure(text=text_val)
        refresh_image()
        
    def change_threshold_val(val):
        global threshold_value
        threshold_value = int(val)
        filters.thresholding(ploted_array,threshold_value)
        text_val = "Threshold: " + str(threshold_value)
        label_Threshold.configure(text=text_val)
        refresh_image()
        
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
    
    def cancel_filter():
        plot_image()
        restore_sliders()
        filters_window.destroy()
        filters_button.configure(state="normal")
        
    def apply_filter():
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

    
    # Laplacian frame
    laplacian_frame = ctk.CTkFrame(master=filters_frame)
    laplacian_frame.grid(row=0, column=1, padx=15, pady=5)
    #laplacian_frame.pack()
    
    # Laplacian Label
    laplacian_label = ctk.CTkLabel(master=laplacian_frame, text="Laplacian Options", height=10)
    laplacian_label.pack(pady=15)
    
    # Label for the ksize slider
    text_val = "Kernel Size: " + str(kernel_size_amount)
    label_ksize = ctk.CTkLabel(master=laplacian_frame, text=text_val)
    label_ksize.pack()

    # ksize slider
    ksize_slider = ctk.CTkSlider(master=laplacian_frame, from_=0, to=13, command=change_ksize_val, width=120)
    ksize_slider.set(5)
    ksize_slider.pack(pady=5)
    
    # Label for the scale slider
    text_val = "Scale: " + str(scale_number)
    label_scale = ctk.CTkLabel(master=laplacian_frame, text=text_val)
    label_scale.pack()

    # scale slider
    scale_slider = ctk.CTkSlider(master=laplacian_frame, from_=1, to=10, command=change_scale_val, width=120)
    scale_slider.set(1)
    scale_slider.pack(pady=5)
    
    # Label for the scale slider
    text_val = "Delta: " + str(delta_factor)
    label_delta = ctk.CTkLabel(master=laplacian_frame, text=text_val)
    label_delta.pack()

    # scale slider
    delta_slider = ctk.CTkSlider(master=laplacian_frame, from_=1, to=10, command=change_delta_val, width=120)
    delta_slider.set(1)
    delta_slider.pack(pady=5)
    
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
    threshold_slider = ctk.CTkSlider(master=thresholding_frame, from_=0, to=255, command=change_threshold_val, width=120)
    threshold_slider.set(100)
    threshold_slider.pack(pady=5)
    
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
    isodata_apply_button = ctk.CTkButton(master=isodata_frame, text ="Preview Isodata", command=apply_isodata)
    isodata_apply_button.pack(pady=5)
    
    # cancel Button
    cancel_filter_button = ctk.CTkButton(master=buttons_frame, text="Cancel",  command=cancel_filter)
    cancel_filter_button.grid(row=0, column=0, padx=5, pady=5)
    
    # apply filter Button
    apply_filter_button = ctk.CTkButton(master=buttons_frame, text="Apply Filter",  command=apply_filter)
    apply_filter_button.grid(row=0, column=1, padx=5, pady=5)

def step():
    undo_image = Image.open("temp/plot.png")
    undo_image_array = np.array(undo_image)
    
    unfo_fig = plt.figure(facecolor='black')
    undo_plot = unfo_fig.add_subplot(111)
    undo_image = plt.imshow(undo_image_array, cmap='gray')
    plt.xticks([])
    plt.yticks([])
    plt.savefig("temp/undo.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)

def apply_segmentation():
    global nii_3d_image
    selection_image = Image.open("temp/selection_canvas.png")
    selection_array = np.array(selection_image)
    
    step()
    
    red_mask = (selection_array[:,:,0] > 200)
    red_mask_fig = plt.figure(facecolor='black')
    red_mask_plot = red_mask_fig.add_subplot(111)
    red_mask_image = plt.imshow(red_mask, cmap='gray')
    plt.xticks([])
    plt.yticks([])
    plt.savefig("temp/red_mask.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
    time.sleep(0.0016)
    
    green_mask = (selection_array[:,:,1] > 200)
    #print("green mask", green_mask[1,1])
    green_mask_fig = plt.figure(facecolor='black')
    green_mask_plot = green_mask_fig.add_subplot(111)
    green_mask_plot.imshow(green_mask, cmap='gray')
    plt.xticks([])
    plt.yticks([])
    time.sleep(0.0016)
    plt.savefig("temp/green_mask.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
    
    visited_mask = np.logical_or(selection_array[:,:,1] > 200, selection_array[:,:,0] > 200)
    visited_mask_fig = plt.figure(facecolor='black')
    visited_mask_plot = visited_mask_fig.add_subplot(111)
    visited_mask_plot.imshow(visited_mask, cmap='gray')
    plt.xticks([])
    plt.yticks([])
    time.sleep(0.0016)
    plt.savefig("temp/visited_mask.png", format='png', dpi= 120 , bbox_inches='tight', pad_inches=0)
    
    #original_image = Image.open("temp/original.png").convert('L')
    ploted_image = Image.open("temp/plot.png").convert('L')
    image_plot = np.array(ploted_image)
    
    #filters.regionGrowing2D(image_plot, tolerance_value)
    nii_3d_image = filters.regionGrowing3D(nii_3d_image, tolerance_value, slice_portion, view_mode.get())
    
    plot_image()
    #refresh_image()
        

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


# switch for include/eclude pen
label_pen_mode = ctk.CTkLabel(master=left_frame_canvas, text="Pen Mode:")
switch_var = ctk.StringVar(value="on")

mode_switch = ctk.CTkSwitch(master=left_frame_canvas, text="Include", state="disabled", command=switch_event, variable=switch_var, onvalue="on", offvalue="off")

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
Tolerance_slider.set(25)
Tolerance_slider.pack(pady=5)

# Process image segmentation button
segmentation_button = ctk.CTkButton(segmentation_tools_frame, text="Apply Region Growing", state="disabled", command=apply_segmentation)
segmentation_button.pack(pady=10)

# Clear canva button
restore_button = ctk.CTkButton(left_frame_canvas, text="Restore Original", command=restore_original)

# Process image segmentation button
undo_button = ctk.CTkButton(left_frame_canvas, text="Undo", command=undoIt)

picture_canvas.bind("<Button-1>", start_draw)
picture_canvas.bind("<B1-Motion>", draw)
picture_canvas.bind("<ButtonRelease-1>", end_draw)


root.mainloop()