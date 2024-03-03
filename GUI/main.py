import customtkinter as ctk
import tkinter as tk
import nibabel as nib
import matplotlib.pyplot as plt
from tkinter import filedialog
from PIL import Image, ImageTk

root = ctk.CTk()

# Window dimensions and centering
window_width = 1000
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.title("MRI Segmentation Tool")

pen_color = ""
pen_size = 15
file_path = ""


def add_image():
    global file_path, pen_color
    file_path = filedialog.askopenfilename(filetypes=[("NIfTI files", "*.nii")])
    if file_path:
        try:
            # reading file
            nii_file = nib.load(file_path).get_fdata()
            nii_file.shape
            
            # getting data
            nii_data = nii_file[:,:,100]
            
            # plotting data
            plt.imshow(nii_data)
            plt.axis('off')
            plt.imsave("output/plot.png", nii_data
                       , cmap='gray'
                       )
            
            # placing plot in the canvas
            plot_image = Image.open("output/plot.png")
            width, height = int(plot_image.width * 3), int(plot_image.height * 3) # upscaling the plot_image
            plot_image = plot_image.resize((width, height))
            
            # adjusting the canvas to be the same size
            drawing_canvas.config(width=plot_image.width, height=plot_image.height)
            
            image = ImageTk.PhotoImage(plot_image)
            drawing_canvas.image = image
            drawing_canvas.create_image(0, 0, image=image, anchor="nw")
            mode_switch.configure(state="normal")
            pen_size_scale.configure(state="normal")
            clear_button.configure(state="normal")
            process_segmentation_button.configure(state="normal")
            pen_color="green3"
        except Exception as e:
            print("Error loading image:", e)
    else:
        print("No file selected")
        
def change_pen_size(val):
    global pen_size
    pen_size = int(val)
    
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

def process_segmentation():
    print("Work in progress jeje")
    
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

# Process image button
process_segmentation_button = ctk.CTkButton(left_frame, text="Process Segmentation", state="disabled", command=process_segmentation)
process_segmentation_button.pack(pady=10, padx=20)

drawing_canvas.bind("<Button-1>", start_draw)
drawing_canvas.bind("<B1-Motion>", draw)
drawing_canvas.bind("<ButtonRelease-1>", end_draw)

root.mainloop()
