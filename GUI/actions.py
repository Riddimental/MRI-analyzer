import tkinter as tk
from tkinter import filedialog

def button_function():
    print("Upload funciono yeeeeey")
    
def upload_image():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    
    if file_path:
        print("Imagen seleccionada:", file_path)
        # Aquí puedes realizar la acción que desees con el archivo seleccionado
    else:
        print("No se seleccionó ninguna imagen.")