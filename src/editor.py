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
    {"IMAGEMAGICK_BINARY":  r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})


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
        # Types of files to be output
        if mimetypes.guess_type(self.master.filename)[0].startswith('video'):
            openFileLabel = tk.Label(self.master, anchor="e", justify=tk.LEFT, text="Location: " +
                                     self.master.filename + " Type: " + "Video", font=("Helvatica", 13))
            openFileLabel.grid(sticky="W", column=0, row=len(
                self.importedObjects) + 4, padx=10, pady=2)
            file = FileObject(self.master.filename, openFileLabel, "video")
            self.importedObjects.append(file)
        else:
            openFileLabel = tk.Label(self.master, anchor="e", justify=tk.LEFT, text="Location: " +
                                     self.master.filename + " Type: " + "Audio", font=("Helvatica", 13))
            openFileLabel.grid(sticky="W", column=0, row=len(
                self.importedObjects) + 4, padx=10, pady=2)
            file = FileObject(self.master.filename, openFileLabel, "audio")
            self.importedObjects.append(file)

    def get_random_string(self, length):
        letters = string.ascii_lowercase
        result_str = ''. join(random.choice(letters) for i in range(length))
        return result_str

    def processData(self):
        dir_name = filedialog.askdirectory()

        file_name_extension = "/" + self.get_random_string(8)
        video_name = dir_name + file_name_extension + "_video" + ".mp4"
        gif_name = dir_name + file_name_extension + "_gif" + ".gif"
        thumbnail_name = dir_name + file_name_extension + "_thumbnail" + ".jpeg"

        video_clip_found = None
        audio_clip_found = None
        for file in self.importedObjects:
            if (file.data_type == "video"):
                video_clip_found = file
            elif (file.data_type == "audio"):
                audio_clip_found = file

        if (video_clip_found and audio_clip_found):
            clip = VideoFileClip(video_clip_found.path)

            overlayEntry = self.widgets
            # Text you will put on video (Adjust to set duration)
            clip_overlay = TextClip(overlayEntry.get(), color="blue", font="Roboto",
                                    kerning=5, fontsize=150).set_position("center").set_duration(15)

        frame = clip.get_frame(int(10))
        thumb_image = Image.fromarray(frame)
        thumb_image.save(thumbnail_name)

        # Background music.
        background_audio_clip = AudioFileClip(audio_clip_found.path)
        # Note here that the music plays to the clip duration
        bg_music = background_audio_clip.subclip(0, clip.duration)

        # Compression
        resized_clip = clip.resize(0.5)
        resized_clip.write_gif(gif_name)
        # Alternative: ffmpeg -i input.mp4 -vcodec h264 -acodac aad output.mp4

        clip_with_audio = clip.set_audio(bg_music)
        final_clip = CompositeVideoClip([clip_with_audio, clip_overlay])
        final_clip.write_videofile(
            video_name, codec='libx264', audio_codec='aac')


# Root frame
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Edge Cutter")

    main_app = VideoEditorGUI(root)
    root.mainloop()
