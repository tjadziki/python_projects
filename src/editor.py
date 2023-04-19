import os
from moviepy.editor import *
from moviepy.config import change_settings
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import mimetypes
import random
import string
import cv2


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
        self.configure_gui()
        self.create_widgets()
        self.importedObjects = []
        self.crop_coords = (0, 0, 0, 0)
        self.canvas = None
        self.active_rect = None

    def configure_gui(self):
        self.master.geometry('1280x760')

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
            self.show_video_frame()
        else:
            openFileLabel = tk.Label(self.master, anchor="e", justify=tk.LEFT, text="Location: " +
                                     self.master.filename + " Type: " + "Audio", font=("Helvatica", 13))
            openFileLabel.grid(sticky="W", column=0, row=len(
                self.importedObjects) + 4, padx=10, pady=2)
            file = FileObject(self.master.filename, openFileLabel, "audio")
            self.importedObjects.append(file)

    def show_video_frame(self):
        clip = VideoFileClip(self.importedObjects[-1].path)
        frame = clip.get_frame(0)
        frame_image = Image.fromarray(frame)
        frame_image.thumbnail((800, 600))
        frame_image_tk = ImageTk.PhotoImage(frame_image)

        self.canvas = tk.Canvas(self.master, width=800, height=600)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        self.canvas.create_image(0, 0, image=frame_image_tk, anchor=tk.NW)
        self.canvas.image = frame_image_tk

        self.rects = {
            "facecam": {"coords": (0, 0, 0, 0), "tag": "facecam_rect", "color": "red"},
            "gameplay": {"coords": (0, 0, 0, 0), "tag": "gameplay_rect", "color": "blue"}
        }
        self.current_rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        print("Buttton press event")
        if not self.current_rect:
            return

        self.rects[self.current_rect]["coords"] = (
            event.x, event.y, event.x, event.y)
        self.canvas.create_rectangle(
            *self.rects[self.current_rect]["coords"], outline=self.rects[self.current_rect]["color"], tag=self.rects[self.current_rect]["tag"])

        if self.active_rect == "facecam":
            self.aspect_ratio = 16 / 9
        elif self.active_rect == "gameplay":
            self.aspect_ratio = 9 / 16

        self.start_x = event.x
        self.start_y = event.y

    def on_move_press(self, event):
        if self.active_rect:
            dx = event.x - self.start_x
            dy = event.y - self.start_y

            self.canvas.move(self.rects[self.active_rect]["tag"], dx, dy)

            self.start_x = event.x
            self.start_y = event.y

            self.update_crop_coords()

    def update_crop_coords(self):
        if not self.current_rect:
            return

        x1, y1, x2, y2 = self.rects[self.current_rect]["coords"]
        self.crop_coords = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        print("Crop coords:", self.crop_coords)

    def on_button_release(self, event):
        self.update_crop_coords()

        if self.active_rect:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            new_width = self.rects[self.active_rect]["coords"][2] + dx
            new_height = new_width / self.aspect_ratio

            if self.active_rect == "facecam":
                # Ensure the facecam height does not exceed one-third of the canvas height
                if new_height > self.canvas_height / 3:
                    new_height = self.canvas_height / 3
                    new_width = new_height * self.aspect_ratio

            elif self.active_rect == "gameplay":
                # Ensure the gameplay height does not exceed two-thirds of the canvas height
                if new_height > (self.canvas_height * 2) / 3:
                    new_height = (self.canvas_height * 2) / 3
                    new_width = new_height * self.aspect_ratio

            self.canvas.coords(
                self.rects[self.active_rect]["tag"],
                (
                    self.rects[self.active_rect]["coords"][0],
                    self.rects[self.active_rect]["coords"][1],
                    self.rects[self.active_rect]["coords"][0] + new_width,
                    self.rects[self.active_rect]["coords"][1] + new_height,
                ),
            )

        self.start_x = None
        self.start_y = None
        self.active_rect = None

    def create_widgets(self):
        # Import video and audio
        importButton = tk.Button(self.master, text="Import", font=(
            "Helvetica", 18), padx=10, pady=5, fg="#FFF", bg="#3582e8", command=self.open_dialog)
        importButton.grid(sticky="W", column=0, row=0, padx=10, pady=10)

        # Facecam and Gameplay selection buttons
        facecamButton = tk.Button(self.master, text="Facecam", font=("Helvetica", 18), padx=10,
                                  pady=5, fg="#FFF", bg="#E85151", command=lambda: self.set_current_rect("facecam"))
        facecamButton.grid(sticky="W", column=1, row=0, padx=10, pady=10)

        gameplayButton = tk.Button(self.master, text="Gameplay", font=("Helvetica", 18), padx=10,
                                   pady=5, fg="#FFF", bg="#5284E8", command=lambda: self.set_current_rect("gameplay"))
        gameplayButton.grid(sticky="W", column=2, row=0, padx=10, pady=10)

        # Process video
        processButton = tk.Button(self.master, text="Process", font=(
            "Helvetica", 18), padx=10, pady=5, fg="#FFF", bg="#3582e8", command=self.processData)
        processButton.grid(sticky="W", column=3, row=0, padx=10, pady=10)

        # Add an Entry widget for overlay text
        self.overlay_text_label = tk.Label(self, text="Overlay Text:")
        self.overlay_text_label.grid(row=6, column=0, sticky='w')
        self.overlay_text_entry = tk.Entry(self)
        self.overlay_text_entry.grid(row=6, column=1, sticky='w')

        return [importButton, facecamButton, gameplayButton, processButton]

    def set_current_rect(self, rect_name):
        self.current_rect = rect_name

    def processData(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4")
        video_clips = [
            obj.path for obj in self.importedObjects if obj.data_type == "video"]
        audio_clips = [
            obj.path for obj in self.importedObjects if obj.data_type == "audio"]

        if len(video_clips) > 0:
            video = concatenate_videoclips(
                [VideoFileClip(clip) for clip in video_clips])
            if len(audio_clips) > 0:
                audio = concatenate_audioclips(
                    [AudioFileClip(clip) for clip in audio_clips])
                video = video.set_audio(audio)

            # Calculate facecam and gameplay positions in the final video
            facecam_coords = [
                int((coord / self.canvas_width) * new_width)
                if index % 2 == 0
                else int((coord / self.canvas_height) * new_height)
                for index, coord in enumerate(self.crop_coords["facecam"])
            ]
            gameplay_coords = [
                int((coord / self.canvas_width) * new_width)
                if index % 2 == 0
                else int((coord / self.canvas_height) * new_height)
                for index, coord in enumerate(self.crop_coords["gameplay"])
            ]

            # Set facecam height to one-third of the final video height
            facecam_height = int(new_height / 3)
            facecam_width = int(facecam_height * self.aspect_ratio)

            # Set gameplay height to two-thirds of the final video height
            gameplay_height = int((new_height * 2) / 3)
            gameplay_width = int(gameplay_height * self.aspect_ratio)

            # Position facecam video in the top third of the final video
            facecam = facecam.set_position((0, 0), relative=False).resize(
                (facecam_width, facecam_height))

            # Position gameplay video in the bottom two-thirds of the final video
            gameplay = gameplay.set_position((0, facecam_height), relative=False).resize(
                (gameplay_width, gameplay_height))

            # Overlay the facecam video on the gameplay video
            final_video = gameplay.overlay(facecam)

            # Check if new dimensions are valid
            new_width = 1280
            new_height = int(new_width / self.aspect_ratio)

            if new_width > 0 and new_height > 0:
                resized_video = final_video.resize(
                    newsize=(new_width, new_height))
            else:
                print(
                    "Invalid dimensions. Ensure both width and height are greater than zero.")
                return
            width = self.crop_coords[2] - self.crop_coords[0]
            height = self.crop_coords[3] - self.crop_coords[1]

            if width > 0 and height > 0:
                resized_video = video.resize(newsize=(width, height))
            else:
                resized_video = video

            overlay_text = self.overlay_text_entry.get()
            if overlay_text:
                txt_clip = (TextClip(overlay_text, fontsize=70, color='white', font="Amiri-Bold")
                            .set_position(('center', 'bottom'), relative=True)
                            .set_duration(video.duration))

            aspect_ratio = float(width) / float(height)
            new_width = 1280
            new_height = int(new_width / aspect_ratio)

            if new_width > 0 and new_height > 0:
                resized_video = video.resize(newsize=(new_width, new_height))
            else:
                print(
                    "Invalid dimensions. Ensure both width and height are greater than zero.")
                return

            resized_video.write_videofile(
                output_path, codec="libx264", audio_codec="aac")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEditorGUI(root)
    app.mainloop()
