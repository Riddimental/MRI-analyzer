import tkinter as tk
import customtkinter
import actions

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

# define main window
root_tk = tk.Tk()
root_tk.title("MRI Analyzer beta")

# Window dimensions and centering
window_width = 900
window_height = 600
screen_width = root_tk.winfo_screenwidth()
screen_height = root_tk.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root_tk.geometry(f"{window_width}x{window_height}+{x}+{y}")

# main frame canva
main_frame = customtkinter.CTkFrame(master=root_tk)
main_frame.pack(fill=tk.BOTH, expand=True)

# Left frame of the canva, holds the logo and the buttons
left_frame = customtkinter.CTkFrame(master=main_frame)
left_frame.grid(row=0, column=0, sticky="nsew")
left_frame.columnconfigure(0, weight=1)

# Logo
logo_frame = customtkinter.CTkFrame(master=left_frame)
logo_frame.grid(row=0, pady=10, padx=30)

# Canvas for logo
canvas = tk.Canvas(master=logo_frame, width=100, height=100)
canvas.grid(row=0)
logo_image = tk.PhotoImage(file="images/logo.png").subsample(4, 4)
canvas.create_image(50, 50, image=logo_image)

# Title "MRI Analyzer" under the logo
title_label = tk.Label(logo_frame, text="MRI Analyzer beta")
title_label.grid(row=1)

# Left frame buttons
buttons_frame = customtkinter.CTkFrame(master=left_frame)
buttons_frame.grid(row=1, column=0, sticky="nsew")

button_upload_image = customtkinter.CTkButton(master=buttons_frame, corner_radius=10, text="Upload Image", command=actions.upload_image)
button_upload_image.grid(row=0, pady=10, padx=30)

empty_space = tk.Frame(master=buttons_frame, height=40)
empty_space.grid(row=1)

button_include = customtkinter.CTkButton(master=buttons_frame, corner_radius=10, text="Include Tool", command=actions.button_function)
button_include.grid(row=2, pady=10, padx=30)

button_avoid = customtkinter.CTkButton(master=buttons_frame, corner_radius=10, text="Avoid Tool", command=actions.button_function)
button_avoid.grid(row=3, pady=10, padx=30)

empty_space2 = tk.Frame(master=buttons_frame, height=60)
empty_space2.grid(row=4)

button_preview = customtkinter.CTkButton(master=buttons_frame, corner_radius=10, text="Preview Segmentation", command=actions.button_function)
button_preview.grid(row=5, pady=10, padx=30)

# Right Frame holds the main image and the space for the user to higlight selected zones
right_frame = customtkinter.CTkFrame(master=main_frame)
right_frame.grid(row=0, column=1, sticky="nsew")
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

image_frame = tk.Frame(master=right_frame, bg="white")
image_frame.pack(fill=tk.BOTH, expand=True)

root_tk.mainloop()
