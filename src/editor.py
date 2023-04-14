import os
from moviepy.editor import *
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import mimetypes
import random
import string

from moviepy.config import change_settings
change_settings(
    {"IMAGEMAGIC_BINARY":  r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})


# Creating the interface
class FileObject:
    def __init__(self, path, label, data_type):
        self.path = path
        self.label = label
        self.data_type = data_type


class VideoEditorGUI(tk.Frame):
    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.gui = self.configure_gui()
        self.widgets = self.create_widgets()
        self.importedObjects = []

    def configure_gui(self):
        self.master.geometry('1280x760')

    def create_widgets(self):
        # Import Button
        importBtn = tk.Button(self.master, text="Import", font=(
            "Helvatica", 18), padx=10, pady=5, fg="#FFF", bg="#3582e8", command=self.open_dialog)
        importBtn.grid(stick="W", column=0, row=0, padx=10, pady=10)
        # Process Button
        processBtn = tk.Button(self.master, text="Process", font=(
            "Helvatica", 18), padx=10, pady=5, fg="#FFF", bg="#3582e8", command=self.processData)
        processBtn.grid(sticky="W", column=0, row=1, padx=10, pady=10)

        # Cropping area
        # TODO

        # Branding text
        overlayEntry = tk.Entry(self.master, width=15,
                                text="Title", font=("Helvatica", 18))
        overlayEntry.grid(sticky="W", column=0, row=2, padx=10, pady=10)

        return overlayEntry

    # Function to import video and audio
    def open_dialog(self):
        self.master.filename = filedialog.askopenfilename(
            initialdir="/", title="Select your files", filetypes=[('All files', '*.*')])
        print(self.master.filename)

    def processData(self):
        print("Processing")


# Root frame
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Edge Cutter")

    main_app = VideoEditorGUI(root)
    root.mainloop()
