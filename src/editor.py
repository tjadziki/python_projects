import os
from moviepy.editor import *
from moviepy.config import change_settings
import tkinter as tk
import numpy as np
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

# Creating the interface


class FileObject:
    def __init__(self, path, label, data_type):
        self.path = path
        self.label = label
        self.data_type = data_type


class ResizableRectangle:
    @property
    def x1(self):
        return self.canvas.coords(self.tag)[0]

    @property
    def y1(self):
        return self.canvas.coords(self.tag)[1]

    @property
    def x2(self):
        return self.canvas.coords(self.tag)[2]

    @property
    def y2(self):
        return self.canvas.coords(self.tag)[3]

    def __init__(self, canvas, x1, y1, x2, y2, tag, text):
        self.canvas = canvas
        self.tag = tag
        self.text = text

        self.canvas.create_rectangle(
            x1, y1, x2, y2, outline="white", tags=self.tag)
        self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2, text=self.text, tags=self.tag, fill="white")
        self.corners = []
        for i in range(4):
            self.corners.append(self.canvas.create_rectangle(
                0, 0, 10, 10, fill="white", tags=self.tag))

        self._update_corners()

        self.canvas.tag_bind(self.tag, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.tag, "<ButtonRelease-1>", self.on_release)
        self.canvas.tag_bind(self.tag, "<B1-Motion>", self.on_move)

    def on_press(self, event):
        self.x, self.y = event.x, event.y
        self._current_corner = None

        for i, corner in enumerate(self.corners):
            coords = self.canvas.coords(corner)
            if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                self._current_corner = i
                break

    def on_release(self, event):
        self.x, self.y = None, None

    def on_move(self, event):
        dx, dy = event.x - self.x, event.y - self.y

        if self._current_corner is not None:
            coords = self.canvas.coords(self.tag)
            if self._current_corner in (0, 1):
                coords[1] += dy
            if self._current_corner in (2, 3):
                coords[3] += dy
            if self._current_corner in (0, 2):
                coords[0] += dx
            if self._current_corner in (1, 3):
                coords[2] += dx
            self.canvas.coords(self.tag, *coords)
        else:
            self.canvas.move(self.tag, dx, dy)

        self._update_corners()
        self.x, self.y = event.x, event.y

    def _update_corners(self):
        coords = self.canvas.coords(self.tag)
        x1, y1, x2, y2 = coords

        corner_coords = [
            (x1 - 5, y1 - 5, x1 + 5, y1 + 5),
            (x2 - 5, y1 - 5, x2 + 5, y1 + 5),
            (x1 - 5, y2 - 5, x1 + 5, y2 + 5),
            (x2 - 5, y2 - 5, x2 + 5, y2 + 5),
        ]

        for corner, new_coords in zip(self.corners, corner_coords):
            self.canvas.coords(corner, *new_coords)

# ResizableRectangle class remains the same


class VideoEditorGUI(tk.Frame):

    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, bg="black", width=640, height=360)
        self.canvas.pack()

        self.import_button = tk.Button(
            self.frame, text="Import Video", command=self.import_video)
        self.import_button.pack(side=tk.LEFT)

        self.process_button = tk.Button(
            self.frame, text="Process Video", command=self.process_data)
        self.process_button.pack(side=tk.RIGHT)

    def import_video(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            return

        # Save the video filepath
        self.filepath = filepath

        # Read the video file
        video = VideoFileClip(filepath)

        # Get a frame from the video (e.g., at 1 second)
        frame = video.get_frame(1)

        # Convert the frame to a PIL image
        self.video_frame = Image.fromarray(
            np.uint8(frame)).resize((640, 360), Image.ANTIALIAS)
        self.video_frame = ImageTk.PhotoImage(self.video_frame)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.video_frame)

        self.facecam = ResizableRectangle(
            self.canvas, 10, 10, 160, 90, "facecam", "Facecam")
        self.gameplay = ResizableRectangle(
            self.canvas, 170, 10, 470, 270, "gameplay", "Gameplay")

    def process_data(self):
        if not hasattr(self, 'filepath') or not self.filepath:
            messagebox.showerror("Error", "No video file has been imported.")
            return

        clip = VideoFileClip(self.filepath)

        facecam_coords = self.canvas.coords(self.facecam.tag)
        gameplay_coords = self.canvas.coords(self.gameplay.tag)

        facecam_clip = clip.crop(
            x1=facecam_coords[0], y1=facecam_coords[1], x2=facecam_coords[2], y2=facecam_coords[3])
        facecam_resized = facecam_clip.resize(height=360)

        gameplay_clip = clip.crop(
            x1=gameplay_coords[0], y1=gameplay_coords[1], x2=gameplay_coords[2], y2=gameplay_coords[3])
        gameplay_resized = gameplay_clip.resize(height=720)

        final_clip = concatenate_videoclips(
            [facecam_resized, gameplay_resized], method="compose")
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4")
        if not output_path:
            return

        final_clip.write_videofile(
            output_path, codec='libx264', audio_codec='aac')


def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = VideoEditorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
