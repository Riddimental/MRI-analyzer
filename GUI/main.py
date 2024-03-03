import customtkinter as ctk
import tkinter as tk
import nibabel as nib
import matplotlib.pyplot as plt
import filters
from tkinter import Toplevel, filedialog
from PIL import Image, ImageTk

root = ctk.CTk()

# Window dimensions and centering
window_width = 1000
window_height = 700
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
nii_data = []
nii_data_backup = []

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

def plot_image(data):
    global pen_color
    
    # plotting data
    plt.figure(facecolor='black')
    plt.imshow(data, cmap='gray')
    plt.axis('off')
    plt.savefig("output/plot.png", format='png', dpi= 120)
    
    refresh_image()
    
    mode_switch.configure(state="normal")
    pen_size_scale.configure(state="normal")
    clear_button.configure(state="normal")
    process_segmentation_button.configure(state="normal")
    gaussian_filter_button.configure(state="normal")
    restore_image_button.configure(state="normal")
    gaussian_slider.configure(state="normal")
    pen_color="green3"

def add_image():
    global file_path, pen_color, nii_data, nii_data_backup
    file_path = filedialog.askopenfilename(filetypes=[("NIfTI files", "*.nii")])
    if file_path:
        try:
            # reading file
            nii_file = nib.load(file_path).get_fdata()
            nii_file.shape
            
            # getting data
            nii_data = nii_file[:,:,109]
            nii_data_backup = nii_data
            
            # runs function to update background
            plot_image(nii_data)
        except Exception as e:
            print("Error loading image:", e)
    else:
        print("No file selected")
        
def change_pen_size(val):
    global pen_size
    pen_size = int(val)
    
def change_gaussian_val(val):
    global gaussian_intensity
    gaussian_intensity = int(val)
    
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
    
    global nii_data
    
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
    ctk.CTkFrame(master=filters_window, height=40).pack()
    
    # options in radiobuttons
    var = tk.IntVar()
    
    # Gaussian option
    gaussian_filter_radio = ctk.CTkRadioButton(master=filters_window, text="Gaussian smoothing", variable=var, value=1, command=lambda: [filters.gaussian(nii_data,gaussian_intensity)])
    gaussian_filter_radio.pack()
    
    # Laplacian filter (edges)
    laplacian_filter_radio = ctk.CTkRadioButton(master=filters_window, text="Laplacian edges", variable=var, value=2, command= filters.laplacian(nii_data))
    laplacian_filter_radio.pack()
    
    # An apply button to confirm changes
    ctk.CTkButton(master=filters_window, text ="Apply", command=lambda: [filters_window.destroy(),apply_changes(options)]).pack()
    print("ventana filtros")
    
    # A cancel button to discard changes
    ctk.CTkButton(master=filters_window, text ="Cancel", command=lambda: [filters_window.destroy(),process_segmentation_button.configure(state="normal")]).pack()
    print("ventana filtros")
    
def restore_data():
    global nii_data, nii_data_backup
    nii_data = nii_data_backup
    plot_image(nii_data_backup)
    

def apply_changes(options):
    # run update image function
    plot_image(nii_data)
    
    # activate the filters button
    process_segmentation_button.configure(state="normal")
    print("boton apply")

def switch_event():
    if(switch_var.get() == "on"):
        include()
    else:
        exclude()
    print("switch toggled, current value:", switch_var.get())


# left Frame which contains the tools and options
left_frame = ctk.CTkFrame(root, height=600)
left_frame.pack(padx= 15, side='left', fill='y')

# Canvas Area on the rest of the window
canvas_frame = ctk.CTkFrame(root, width=750, height=600)
canvas_frame.pack()
drawing_canvas = ctk.CTkCanvas(canvas_frame, width=750, height=600)
drawing_canvas.pack()

# Logo
logo_frame = ctk.CTkFrame(master=left_frame)
logo_frame.grid(row=0, pady=10, padx=30)
canvas_logo = tk.Canvas(master=logo_frame, width=100, height=100)
canvas_logo.grid(row=0)
logo_image = tk.PhotoImage(file="images/logo.png").subsample(4, 4)
canvas_logo.create_image(50, 50, image=logo_image)
logo_frame.pack(pady=15)

# Title of the tool under the logo
title_label = ctk.CTkLabel(logo_frame, text="MRI Slice \n Segmentation Tool \n (beta)")
title_label.grid(row=1)

# Upload Button
upload_button = ctk.CTkButton(left_frame, text='Upload Image', command=add_image)
upload_button.pack(pady=15)

# switch for include/eclude pen
label = ctk.CTkLabel(master=left_frame, text="Pen Mode:")
label.pack(pady=5)
switch_var = ctk.StringVar(value="on")


mode_switch = ctk.CTkSwitch(master=left_frame, text="Include", state="disabled", command=switch_event,
                                   variable=switch_var, onvalue="on", offvalue="off")
mode_switch.pack(padx=20, pady=10)


# Size slider
margin = ctk.CTkFrame(master=left_frame, height=20)

# Label for the slider
label = ctk.CTkLabel(master=left_frame, text="Pen Size:")
label.pack(pady=5)

# slider
pen_size_scale = ctk.CTkSlider(master=left_frame, from_=5, to=25,state="disabled", command=change_pen_size, width=120)
pen_size_scale.set(pen_size)
pen_size_scale.pack()

# Clear canva button
clear_button = ctk.CTkButton(left_frame, text="Clear Selection", state="disabled", command=clear_canvas)
clear_button.pack(pady=10)

# Gaussian slider
margin = ctk.CTkFrame(master=left_frame, height=20)

# Label for the Gaussian slider
label_Gaussian = ctk.CTkLabel(master=left_frame, text="Gaussian intensity:")
label_Gaussian.pack(pady=5)

# slider
gaussian_slider = ctk.CTkSlider(master=left_frame, from_=1, to=13, state="disabled", command=change_gaussian_val, width=120)
gaussian_slider.set(1)
gaussian_slider.pack(pady=5)

# Gaussian filter Button
gaussian_filter_button = ctk.CTkButton(left_frame, text="Gaussian Filter", state="disabled", command=lambda: [filters.gaussian(nii_data,gaussian_intensity),refresh_image()])
gaussian_filter_button.pack(pady=5)

# restore image Button
restore_image_button = ctk.CTkButton(left_frame, text="Restore Image", state="disabled",  command=lambda: [restore_data(),plot_image(nii_data)])
restore_image_button.pack(pady=5)

# Process image button
process_segmentation_button = ctk.CTkButton(left_frame, text="Filters", state="disabled", command=filters_window)
process_segmentation_button.pack(pady=10, padx=20)

drawing_canvas.bind("<Button-1>", start_draw)
drawing_canvas.bind("<B1-Motion>", draw)
drawing_canvas.bind("<ButtonRelease-1>", end_draw)

root.mainloop()
