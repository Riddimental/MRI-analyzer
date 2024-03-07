import time
import customtkinter as ctk
import numpy as np
import tkinter as tk
import nibabel as nib
import matplotlib as mpl
import matplotlib.pyplot as plt
import filters
from tkinter import Toplevel, filedialog
from PIL import Image, ImageTk, ImageDraw

root = ctk.CTk()

# Window dimensions and centering
window_width = 800
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.title("MRI Segmentation Tool")

# to find the range of the threshold slider
max_value = 0
pen_color = ""
pen_size = 7
gaussian_intensity = 1
file_path = ""
nii_2d_image = []
nii_3d_image = []
nii_3dimage_backup = []
slice_portion = 100
ksize_amount = 5
scale_number = 1
delta_factor = 0
threshold_value = 100
isodata_tolerance = 0.001
isodata_threshold = 200
tolerance_value=10


# Radio buttons (0) Axial, (1) Coronal, (2) Sagittal
view_mode = ctk.StringVar(value="Axial")
selection_image = Image.new("RGB",(200,200),(255,255,255))

def refresh_image():
    global selection_image
    # placing plot in the canvas
    time.sleep(0.0008)
    plot_image = Image.open("temp/plot.png")
    #width, height = int(plot_image.width * 3), int(plot_image.height * 3) # upscaling the plot_image
    #plot_image = plot_image.resize((width, height))
    
    # adjusting the canvas to be the same size
    drawing_canvas.config(width=plot_image.width, height=plot_image.height)
    picture_canvas.config(width=plot_image.width, height=plot_image.height)
    selection_image = Image.new("RGB",(plot_image.width,plot_image.height),(0,0,0))
    selection_image.save("temp/selection_canvas.png",format='png')
    selection_image.save("temp/green_mask.png",format='png')
    selection_image.save("temp/red_mask.png",format='png')
    selection_image.save("temp/visited_mask.png",format='png')

    
    image = ImageTk.PhotoImage(plot_image)
    picture_canvas.image = image
    picture_canvas.create_image(0, 0, image=image, anchor="nw")
    #drawing_canvas.image = image
    #drawing_canvas.create_image(0, 0, image=image, anchor="nw")

def plot_image():
    global max_value, nii_2d_image, nii_3d_image, pen_color, slice_portion
    
    #mpl.rcParams['savefig.pad_inches'] = 0
    
    # selecting a slice out of the 3d image
    
    if(view_mode.get() == "Axial"):
        nii_2d_image = nii_3d_image[:,:,slice_portion]
    elif(view_mode.get() == "Coronal"):
        nii_2d_image = nii_3d_image[:,slice_portion,:]
    elif(view_mode.get() == "Sagittal"):
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
    filters_button.configure(state="normal")
    slice_slider.configure(state="normal")
    segmentation_button.configure(state="normal")
    Tolerance_slider.configure(state="normal")
    pen_color="#00cd00"

def add_image():
    global file_path, pen_color, nii_2d_image, nii_3dimage_backup, nii_3d_image
    file_path = filedialog.askopenfilename(filetypes=[("NIfTI files", "*.nii")])
    if file_path:
        try:
            # reading file
            nii_file = nib.load(file_path).get_fdata()
            nii_file.shape
            
            # getting data
            #nii_data = nii_file[:,:,slice_portion]
            nii_3d_image = nii_file[:,:,:]
            nii_3dimage_backup = nii_3d_image
            
            # runs function to update background
            plot_image()
        except Exception as e:
            print("Error loading image:", e)
    else:
        print("No file selected")
        
def change_pen_size(val):
    global pen_size
    pen_size = int(val)
    
def change_slice_portion(val):
    global slice_portion
    slice_portion = int(val)
    plot_image()
    
def change_gaussian_val(val):
    global gaussian_intensity
    gaussian_intensity = int(val)
    filters.gaussian(nii_2d_image,gaussian_intensity)
    refresh_image()
    
def change_ksize_val(val):
    global ksize_amount
    ksize_amount = int(val)
    filters.laplacian(nii_2d_image,ksize_amount,scale_number, delta_factor)
    refresh_image()
    
def change_scale_val(val):
    global scale_number
    scale_number = int(val)
    filters.laplacian(nii_2d_image,ksize_amount,scale_number, delta_factor)
    refresh_image()
    
def change_delta_val(val):
    global delta_factor
    delta_factor = int(val)
    filters.laplacian(nii_2d_image,ksize_amount,scale_number, delta_factor)
    refresh_image()
    
def change_threshold_val(val):
    global threshold_value
    threshold_value = int(val)
    filters.thresholding(nii_2d_image,threshold_value)
    refresh_image()
    
def change_isodata_threshold_val(val):
    global isodata_threshold
    isodata_threshold = int(val)
    
def change_isodata_tolerance_val(val):
    global isodata_tolerance
    isodata_tolerance = int(val)
    
def change_tolerance_val(val):
    global tolerance_value
    tolerance_value = int(val)
    Tolerance_slider.set(val)

    
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
    #drawing_canvas.create_line(last_x, last_y, x, y, fill=pen_color, width=pen_size*2, capstyle="round", smooth=True)
    picture_canvas.create_line(last_x, last_y, x, y, fill=pen_color, width=pen_size*2, capstyle="round", smooth=True)
    
    # Save canvas image
    draw_selection = Image.open("temp/selection_canvas.png")
    
    # Draw on the canvas image
    draw = ImageDraw.Draw(draw_selection)
    draw.line((last_x, last_y, x, y), fill=pen_color, width=pen_size*2)
    drawing_canvas.create_line(last_x, last_y, x, y, fill=pen_color, width=pen_size*2, capstyle="round", smooth=True)
    draw_selection.save("temp/selection_canvas.png", format='png')
    
    #draw = ImageDraw.Draw(draw_selection)
    #draw.line((last_x, last_y, x, y), fill=pen_color, width=pen_size*2, joint='curve')
    #draw_selection.save("temp/selection_canvas.png",format='png')
    
    last_x, last_y = x, y

def start_draw(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def end_draw(event):
    #referencia.save()
    pass
 
def clear_canvas():
    global pen_size, pen_color
    drawing_canvas.delete("all")
    picture_canvas.create_image(0, 0, image=picture_canvas.image, anchor="nw")
    plot_image = Image.open("temp/plot.png")
    plot_original = Image.open("temp/original.png")
    plot_original.save("temp/plot.png", format='png')
    selection_image = Image.new("RGB",(plot_image.width,plot_image.height),(0,0,0))
    selection_image.save("temp/selection_canvas.png",format='png')
    selection_image.save("temp/green_mask.png",format='png')
    selection_image.save("temp/red_mask.png",format='png')
    pen_size_scale.set(7)
    pen_color = "#00cd00"
    mode_switch.select()
    refresh_image()     


def filters_window():
    
    global nii_2d_image
    
    def restore_sliders():
        global threshold_value,gaussian_intensity,slice_portion,ksize_amount, scale_number, delta_factor
        gaussian_intensity=0
        gaussian_slider.set(0)
        ksize_amount=5
        ksize_slider.set(5)
        scale_number=1
        scale_slider.set(1)
        delta_factor=0
        delta_slider.set(0)
        threshold_value=100
        threshold_slider.set(100)
        isodata_threshold_slider.set(0)
        
    def apply_isodata():
        new_threshold = filters.isodata(nii_2d_image,isodata_threshold,isodata_tolerance)
        change_isodata_threshold_val(new_threshold)
        isodata_threshold_slider.set(new_threshold)
        refresh_image()

    
    # Toplevel object which will 
    # be treated as a new window
    filters_window = Toplevel(root)
    
    options = []
    
    # deactivate the filters button while this windows is open to avoid repeated instances
    filters_button.configure(state="disabled")
    
    # sets the title of the
    # Toplevel widget
    filters_window.title("Image Filters Selector")
 
    # sets the geometry of toplevel
    filters_window.geometry("900x450")

    # spacer
    ctk.CTkLabel(master=filters_window,text="Filtering Options", height=40).pack(pady=15)
    
    # frame grid for filters
    filters_frame = tk.Frame(master=filters_window)
    filters_frame.pack()
    
    # Gaussian frame
    gaussian_frame = tk.Frame(master=filters_frame)
    gaussian_frame.grid(row=0, column=0, padx=15, pady=5)
    #gaussian_frame.pack()
    
    # Gaussian slider
    gaussian_label = ctk.CTkLabel(master=gaussian_frame, text="Gaussian Options", height=10)
    gaussian_label.pack(pady=15)

    # Label for the Gaussian slider
    label_Gaussian = ctk.CTkLabel(master=gaussian_frame, text="Gaussian intensity:")
    label_Gaussian.pack()

    # Gaussian filter slider
    gaussian_slider = ctk.CTkSlider(master=gaussian_frame, from_=1, to=13, command=change_gaussian_val, width=120)
    gaussian_slider.set(0)
    gaussian_slider.pack(pady=5)

    
    # Laplacian frame
    laplacian_frame = tk.Frame(master=filters_frame)
    laplacian_frame.grid(row=0, column=1, padx=15, pady=5)
    #laplacian_frame.pack()
    
    # Laplacian Label
    laplacian_label = ctk.CTkLabel(master=laplacian_frame, text="Laplacian Options", height=10)
    laplacian_label.pack(pady=15)
    
    # Label for the ksize slider
    label_ksize = ctk.CTkLabel(master=laplacian_frame, text="Laplacian Kernel Size")
    label_ksize.pack()

    # ksize slider
    ksize_slider = ctk.CTkSlider(master=laplacian_frame, from_=0, to=13, command=change_ksize_val, width=120)
    ksize_slider.set(5)
    ksize_slider.pack(pady=5)
    
    # Label for the scale slider
    label_scale = ctk.CTkLabel(master=laplacian_frame, text="Laplacian Scale")
    label_scale.pack()

    # scale slider
    scale_slider = ctk.CTkSlider(master=laplacian_frame, from_=1, to=10, command=change_scale_val, width=120)
    scale_slider.set(1)
    scale_slider.pack(pady=5)
    
    # Label for the scale slider
    label_delta = ctk.CTkLabel(master=laplacian_frame, text="Laplacian Delta")
    label_delta.pack()

    # scale slider
    delta_slider = ctk.CTkSlider(master=laplacian_frame, from_=1, to=10, command=change_delta_val, width=120)
    delta_slider.set(1)
    delta_slider.pack(pady=5)
    
    # Thresholding frame
    thresholding_frame = tk.Frame(master=filters_frame)
    thresholding_frame.grid(row=0, column=2, padx=15, pady=5)
    
    # Thresholding options
    gaussian_label = ctk.CTkLabel(master=thresholding_frame, text="Thresholding Options", height=10)
    gaussian_label.pack(pady=15)

    # Label for the Threshold slider
    label_Threshold = ctk.CTkLabel(master=thresholding_frame, text="Threshold:")
    label_Threshold.pack()

    # Threshold  slider
    threshold_slider = ctk.CTkSlider(master=thresholding_frame, from_=0, to=max_value, command=change_threshold_val, width=120)
    threshold_slider.set(100)
    threshold_slider.pack(pady=5)
    
    buttons_frame = tk.Frame(master=filters_window)
    buttons_frame.pack(pady=30)
    
    
    # Isodata frame
    isodata_frame = tk.Frame(master=filters_frame)
    isodata_frame.grid(row=0, column=3, padx=15, pady=5)
    #gaussian_frame.pack()
    
    # Gaussian slider
    isodata_label = ctk.CTkLabel(master=isodata_frame, text="Isodata Options", height=10)
    isodata_label.pack(pady=15)

    # Label for the Gaussian slider
    label_Isodata = ctk.CTkLabel(master=isodata_frame, text="Isodata initial threshold:")
    label_Isodata.pack()

    # Isodata threshold slider
    isodata_threshold_slider = ctk.CTkSlider(master=isodata_frame, from_=0, to=max_value, command=change_isodata_threshold_val, width=120)
    isodata_threshold_slider.set(100)
    isodata_threshold_slider.pack(pady=5)
    
    # An apply button for isodata iterations
    isodata_apply_button = ctk.CTkButton(master=isodata_frame, text ="Apply Isodata", command=apply_isodata)
    isodata_apply_button.pack(pady=5)
    
    # restore image Button
    restore_image_button = ctk.CTkButton(master=buttons_frame, text="Restore Image",  command=lambda: [restore_data(),restore_sliders()])
    restore_image_button.grid(row=0, column=0, padx=5, pady=5)
    
    # A cancel button to discard changes
    close_button = ctk.CTkButton(master=buttons_frame, text ="Close", command=lambda: [filters_window.destroy(),filters_button.configure(state="normal")])
    close_button.grid(row=0, column=1, padx=5, pady=5)
    
def apply_segmentation():
    selection_image = Image.open("temp/selection_canvas.png")
    selection_array = np.array(selection_image)
    
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
    #print("Mask created")
    
    original_image = Image.open("temp/original.png").convert('L')
    original_image_plot = np.array(original_image)
    
    #print("shapeshape",original_image_plot.shape)
    filters.regionGrowing(original_image_plot ,tolerance_value,10000)
    refresh_image()
    
def restore_data():
    global nii_2d_image, nii_3dimage_backup
    nii_2d_image = nii_3dimage_backup
    plot_image()



# left Frame which contains the tools and options
left_frame = ctk.CTkFrame(root, height=screen_height)
left_frame.pack(side='left', fill='y')

# Create a Canvas widget for left frame
left_frame_canvas = ctk.CTkCanvas(left_frame, height=600)
left_frame_canvas.pack(side='left', fill='both', expand=True)

# Add a scrollbar
scrollbar = ctk.CTkScrollbar(left_frame_canvas, orientation='vertical', command=left_frame_canvas.yview)
scrollbar.pack_forget()  # Hide the scrollbar

# Configure the canvas to scroll with the scrollbar
left_frame_canvas.configure(yscrollcommand=scrollbar.set)

# Frame to contain the tools and options
tools_frame = ctk.CTkFrame(left_frame_canvas)
left_frame_canvas.create_window((0, 0), window=tools_frame, anchor='nw')

# Function to update scroll region
def update_scroll_region(event):
    left_frame_canvas.configure(scrollregion=left_frame_canvas.bbox('all'))
    
# Bind event to update scroll region
tools_frame.bind('<Configure>', update_scroll_region)

# diferent Canvas overlaped on the rest of the window
# the main canvas frame
canvas_frame = ctk.CTkFrame(root, width=750, height=600)
canvas_frame.pack(pady=50, padx=15)


# the picture canvas where we show the image (under the drawing canvas)
picture_canvas = ctk.CTkCanvas(canvas_frame, width=750, height=600)
picture_canvas.pack()

# the drawing canvas where we keep the user selection
drawing_canvas = tk.Canvas(canvas_frame, width=750, height=600)
#drawing_canvas.grid(column=1,row=0)

# Logo
logo_frame = ctk.CTkFrame(master=left_frame_canvas,bg_color="transparent")
logo_frame.grid(row=0, pady=15, padx=30)
canvas_logo = tk.Canvas(master=logo_frame, width=100, height=100)
canvas_logo.grid(row=0)
logo_image = tk.PhotoImage(file="images/logo.png").subsample(4, 4)
canvas_logo.create_image(50, 50, image=logo_image)

# Title of the tool under the logo
title_label = ctk.CTkLabel(logo_frame, text="MRI Slice \n Segmentation Tool \n (beta)")
title_label.grid(row=1, pady=15)

# Upload Button
upload_button = ctk.CTkButton(left_frame_canvas, text='Upload Image', command=add_image)
upload_button.grid(row=2,pady=10, padx=20)

# Frame for radio buttons
radio_frame = ctk.CTkFrame(master=left_frame_canvas)
radio_frame.grid(row=3,pady=10)

axial_radio = ctk.CTkRadioButton(master=radio_frame, text="Axial", variable=view_mode, value="Axial", command=plot_image)
axial_radio.grid(row=0, column=0, padx=5, pady=2)

coronal_radio = ctk.CTkRadioButton(master=radio_frame, text="Coronal", variable=view_mode, value="Coronal", command=plot_image)
coronal_radio.grid(row=1, column=0, padx=5, pady=2)

sagittal_radio = ctk.CTkRadioButton(master=radio_frame, text="Sagittal", variable=view_mode, value="Sagittal", command=plot_image)
sagittal_radio.grid(row=2, column=0, padx=5, pady=2)

# slice slider
# Label for the slider
label_slice = ctk.CTkLabel(master=left_frame_canvas, text="Slice portion:")
label_slice.grid(row=4,pady=5)

# slider
slice_slider = ctk.CTkSlider(master=left_frame_canvas, from_=0, to=192,state="disabled", command=change_slice_portion, width=120)
slice_slider.set(slice_portion)
slice_slider.grid(row=5)

# margin
ctk.CTkFrame(master=left_frame_canvas, height=20,bg_color="transparent").grid(row=6,pady=5)

# switch for include/eclude pen
label = ctk.CTkLabel(master=left_frame_canvas, text="Pen Mode:")
label.grid(row=7,pady=5)
switch_var = ctk.StringVar(value="on")


mode_switch = ctk.CTkSwitch(master=left_frame_canvas, text="Include", state="disabled", command=switch_event,
                                   variable=switch_var, onvalue="on", offvalue="off")
mode_switch.grid(row=8, pady=5)

# margin
ctk.CTkFrame(master=left_frame_canvas, height=20).grid(row=9,pady=5)

# Pen size slider
# Label for the slider
label = ctk.CTkLabel(master=left_frame_canvas, text="Pen Size:")
label.grid(row=9,pady=5)

# slider
pen_size_scale = ctk.CTkSlider(master=left_frame_canvas, from_=1, to=13,state="disabled", command=change_pen_size, width=120)
pen_size_scale.set(pen_size)
pen_size_scale.grid(row=10)

ctk.CTkFrame(master=left_frame_canvas, height=20).grid(row=11,pady=5)

# Clear canva button
clear_button = ctk.CTkButton(left_frame_canvas, text="Clear Selection", state="disabled", command=clear_canvas)
clear_button.grid(row=12,pady=10)

# Frame for segmentation tools
segmentation_tools_frame = ctk.CTkFrame(master=left_frame_canvas)
segmentation_tools_frame.grid(row=13,pady=10,padx=20)

# Label for the tolerance slider
label_tolerance = ctk.CTkLabel(master=segmentation_tools_frame, text="Tolerance:")
label_tolerance.pack(pady=5)

# slider tolerance
Tolerance_slider = ctk.CTkSlider(master=segmentation_tools_frame, from_=1, to=192,state="disabled", command=change_tolerance_val, width=120)
Tolerance_slider.set(25)
Tolerance_slider.pack(pady=5)

# Process image segmentation button
segmentation_button = ctk.CTkButton(segmentation_tools_frame, text="Apply Region Growing", state="disabled", command=apply_segmentation)
segmentation_button.pack(pady=5)

# Filters button
filters_button = ctk.CTkButton(left_frame_canvas, text="Filters", state="disabled", command=filters_window)
filters_button.grid(row=14,pady=10, padx=20)

picture_canvas.bind("<Button-1>", start_draw)
picture_canvas.bind("<B1-Motion>", draw)
picture_canvas.bind("<ButtonRelease-1>", end_draw)


root.mainloop()


#mymask = growing(80,84,image_data,25.3,,1000000)
#regionGrowing(x0,y0,Image,Tolerance,max_iter):