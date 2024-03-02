import customtkinter as ctk
import tkinter as tk
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
pen_size = 25
file_path = ""


def add_image():
    global file_path, pen_color
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            image = Image.open(file_path)
            width, height = int(image.width / 2), int(image.height / 2)
            image = image.resize((width, height))
            canvas.config(width=image.width, height=image.height)
            image = ImageTk.PhotoImage(image)
            canvas.image = image
            canvas.create_image(0, 0, image=image, anchor="nw")
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
    canvas.create_line(last_x, last_y, x, y, fill=pen_color, width=pen_size*2, capstyle="round", smooth=True)
    last_x, last_y = x, y

def start_draw(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def end_draw(event):
    pass
 
def clear_canvas():
    global pen_size, pen_color
    canvas.delete("all")
    canvas.create_image(0, 0, image=canvas.image, anchor="nw")
    pen_size = 25
    pen_size_scale.set(25)
    #pen_color = ""
    mode_switch.select()

def process_segmentation():
    print("Work in progress jeje")
    
# left Frame which contains the tools and options
left_frame = ctk.CTkFrame(root, height=600)
left_frame.pack(padx= 15, side='left', fill='y')

# Canvas Area on the rest of the window
canvas = ctk.CTkCanvas(root, width=750, height=600)
canvas.pack()

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
def switch_event():
    if(switch_var.get() == "on"):
        include()
    else:
        exclude()
    print("switch toggled, current value:", switch_var.get())

mode_switch = ctk.CTkSwitch(master=left_frame, text="Include", state="disabled", command=switch_event,
                                   variable=switch_var, onvalue="on", offvalue="off")
mode_switch.pack(padx=20, pady=10)


# Size slider
margin = ctk.CTkFrame(master=left_frame, height=20)

# Label for the slider
label = ctk.CTkLabel(master=left_frame, text="Pen Size:")
label.pack(pady=5)

# slider
pen_size_scale = ctk.CTkSlider(master=left_frame, from_=5, to=45,state="disabled", command=change_pen_size, width=120)
pen_size_scale.set(pen_size)
pen_size_scale.pack()

# Clear canva button
clear_button = ctk.CTkButton(left_frame, text="Clear Selection", state="disabled", command=clear_canvas)
clear_button.pack(pady=10)

# Process image button
process_segmentation_button = ctk.CTkButton(left_frame, text="Process Segmentation", state="disabled", command=process_segmentation)
process_segmentation_button.pack(pady=10, padx=20)

canvas.bind("<Button-1>", start_draw)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonRelease-1>", end_draw)

root.mainloop()
