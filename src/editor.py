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

# # Changing directory
# os.chdir('../data/input')
# cur_path = os.path.dirname(os.path.abspath(__file__))
# print(cur_path)

# # Walk function
# for root, dirs, files in os.walk(cur_path, topdown=False):
#     for name in files:
#         print(os.path.join(root, name))
#     for name in dirs:
#         print(os.path.join(root, name))

clip = VideoFileClip(
    r"C:\Users\joedz\OneDrive\Documents\GitHub\python_projects\data\input\pexels-annie-spratt-10698379-1920x1080-24fps.mp4")

w, h = clip.size

duration = clip.duration

fps = clip.fps

print("Width x Height", w, " x ", h)
print("Duration: ", duration)
print("FPS: ", fps)
