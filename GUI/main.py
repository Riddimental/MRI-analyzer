import customtkinter as ctk
import numpy as np
import tkinter as tk
import nibabel as nib
import matplotlib as mpl
import matplotlib.pyplot as plt
import filters
from tkinter import Toplevel, filedialog
from PIL import Image, ImageTk

root = ctk.CTk()

# Window dimensions and centering
window_width = 800
window_height = 900
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.title("MRI Segmentation Tool")

pen_color = ""
pen_size = 15
gaussian_intensity = 1
file_path = ""
nii_2d_image = []
nii_3d_image = []
nii_3dimage_backup = []
slice_portion = 100
# Radio buttons (0) Axial, (1) Coronal, (2) Sagittal
view_mode = ctk.StringVar(value="Axial")

def refresh_image():
    # placing plot in the canvas
    plot_image = Image.open("output/plot.png")
    #width, height = int(plot_image.width * 3), int(plot_image.height * 3) # upscaling the plot_image
    #plot_image = plot_image.resize((width, height))
    
    # adjusting the canvas to be the same size
    drawing_canvas.config(width=plot_image.width, height=plot_image.height)
    
    image = ImageTk.PhotoImage(plot_image)
    drawing_canvas.image = image
    drawing_canvas.create_image(0, 0, image=image, anchor="nw")

def plot_image():
    global nii_2d_image, nii_3d_image, pen_color, slice_portion
    
    #mpl.rcParams['savefig.pad_inches'] = 0
    
    # selecting a slice out of the 3d image
    
    if(view_mode.get() == "Axial"):
        nii_2d_image = nii_3d_image[:,:,slice_portion]
    elif(view_mode.get() == "Coronal"):
        nii_2d_image = nii_3d_image[:,slice_portion,:]
    elif(view_mode.get() == "Sagittal"):
        nii_2d_image = nii_3d_image[slice_portion,:,:]
    
    # plotting data
    plt.axes(frameon=False)
    plt.figure(facecolor='black')
    # rotate the figure 90 degrees
    nii_2d_image = np.rot90(nii_2d_image)
    plt.imshow(nii_2d_image, cmap='gray')
    plt.xticks([])
    plt.yticks([])
    plt.autoscale(tight=True)
    plt.savefig("output/plot.png", format='png', dpi= 120, bbox_inches='tight', pad_inches=0)
    
    refresh_image()
    
    mode_switch.configure(state="normal")
    pen_size_scale.configure(state="normal")
    clear_button.configure(state="normal")
    process_segmentation_button.configure(state="normal")
    slice_slider.configure(state="normal")
    pen_color="green3"

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
    
def switch_event():
    if(switch_var.get() == "on"):
        include()
    else:
        exclude()

def include():
    global pen_color
    pen_color = "green3"
    
def exclude():
    global pen_color
    pen_color = "red"

def draw(event):
    global last_x, last_y
    x, y = event.x, event.y
    drawing_canvas.create_line(last_x, last_y, x, y, fill=pen_color, width=pen_size*2, capstyle="round", smooth=True)
    last_x, last_y = x, y

def start_draw(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def end_draw(event):
    pass
 
def clear_canvas():
    global pen_size, pen_color
    drawing_canvas.delete("all")
    drawing_canvas.create_image(0, 0, image=drawing_canvas.image, anchor="nw")
    pen_size = 15
    pen_size_scale.set(15)
    pen_color = "green3"
    mode_switch.select()     

def filters_window():
    
    global nii_2d_image
    
    # Toplevel object which will 
    # be treated as a new window
    filters_window = Toplevel(root)
    
    options = []
    
    # deactivate the filters button while this windows is open to avoid repeated instances
    process_segmentation_button.configure(state="disabled")
    
    # sets the title of the
    # Toplevel widget
    filters_window.title("Image Filters Selector")
 
    # sets the geometry of toplevel
    filters_window.geometry("400x600")

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

    # Laplacian filter button (edge detection)
    laplacian_filter_button = ctk.CTkButton(master=laplacian_frame, text="Laplacian edges", command= lambda: [filters.laplacian(nii_2d_image),refresh_image()])
    laplacian_filter_button.pack(pady=5)
    
    buttons_frame = tk.Frame(master=filters_window)
    buttons_frame.pack(pady=30)
    
    # An apply button to confirm changes
    apply_button = ctk.CTkButton(master=buttons_frame, text ="Apply", command=lambda: [filters_window.destroy()])
    apply_button.grid(row=0, column=0, padx=5, pady=5)
    
    # restore image Button
    restore_image_button = ctk.CTkButton(master=buttons_frame, text="Restore Image",  command=lambda: [restore_data(),gaussian_slider.set(0)])
    restore_image_button.grid(row=0, column=0, padx=5, pady=5)
    
    # A cancel button to discard changes
    close_button = ctk.CTkButton(master=buttons_frame, text ="Close", command=lambda: [filters_window.destroy(),process_segmentation_button.configure(state="normal")])
    close_button.grid(row=0, column=1, padx=5, pady=5)
    
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

# Canvas Area on the rest of the window
canvas_frame = ctk.CTkFrame(root, width=750, height=600)
canvas_frame.pack(pady=50, padx=15)
drawing_canvas = ctk.CTkCanvas(canvas_frame, width=750, height=600)
drawing_canvas.pack()

# Logo
logo_frame = ctk.CTkFrame(master=left_frame_canvas)
logo_frame.grid(row=0, pady=15, padx=30)
canvas_logo = tk.Canvas(master=logo_frame, width=100, height=100)
canvas_logo.grid(row=0)
logo_image = tk.PhotoImage(file="images/logo.png").subsample(4, 4)
canvas_logo.create_image(50, 50, image=logo_image)

# Title of the tool under the logo
title_label = ctk.CTkLabel(logo_frame, text="MRI Slice \n Segmentation Tool \n (beta)")
title_label.grid(row=1)

# Upload Button
upload_button = ctk.CTkButton(left_frame_canvas, text='Upload Image', command=add_image)
upload_button.grid(row=2,pady=15, padx=20)

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
ctk.CTkFrame(master=left_frame_canvas, height=20).grid(row=6,pady=5)

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
pen_size_scale = ctk.CTkSlider(master=left_frame_canvas, from_=5, to=25,state="disabled", command=change_pen_size, width=120)
pen_size_scale.set(pen_size)
pen_size_scale.grid(row=10)

ctk.CTkFrame(master=left_frame_canvas, height=20).grid(row=11,pady=5)

# Clear canva button
clear_button = ctk.CTkButton(left_frame_canvas, text="Clear Selection", state="disabled", command=clear_canvas)
clear_button.grid(row=12,pady=10)

# Process image button
process_segmentation_button = ctk.CTkButton(left_frame_canvas, text="Filters", state="disabled", command=filters_window)
process_segmentation_button.grid(row=13,pady=10, padx=20)

drawing_canvas.bind("<Button-1>", start_draw)
drawing_canvas.bind("<B1-Motion>", draw)
drawing_canvas.bind("<ButtonRelease-1>", end_draw)

root.mainloop()
