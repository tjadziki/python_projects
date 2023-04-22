import os
from moviepy.editor import *
import tkinter as tk
import numpy as np
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

# Coding technique learned from MoviePy Tutorials by AI Sciences on Youtube


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

    def create_handle(self, x, y):
        return self.canvas.create_rectangle(x - 3, y - 3, x + 3, y + 3, fill="white", tags=self.tag)

    def __init__(self, canvas, x1, y1, x2, y2, tag, text):
        self.canvas = canvas
        self.tag = tag
        self.text = text

        self.canvas.create_rectangle(
            x1, y1, x2, y2, outline="white", tags=self.tag)
        self.text_id = self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2, text=self.text, tags=self.tag, fill="white")

        self.handles = [
            self.create_handle(x1, y1),
            self.create_handle(x1, y2),
            self.create_handle(x2, y1),
            self.create_handle(x2, y2),
        ]

        self.canvas.tag_bind(self.tag, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.tag, "<ButtonRelease-1>", self.on_release)
        self.canvas.tag_bind(self.tag, "<B1-Motion>", self.on_move)

    def on_press(self, event):
        self.x, self.y = event.x, event.y
        self.resizing = self.is_resizing(event.x, event.y)

    def is_resizing(self, x, y):
        x1, y1, x2, y2 = self.canvas.coords(self.tag)
        corners = [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]
        self.resizing_corner = None

        for corner_x, corner_y in corners:
            if abs(x - corner_x) <= 5 and abs(y - corner_y) <= 5:
                self.resizing_corner = (corner_x, corner_y)
                break

        return self.resizing_corner is not None

    def on_move(self, event):
        dx, dy = event.x - self.x, event.y - self.y

        x1, y1, x2, y2 = self.canvas.coords(self.tag)
        frame_width = self.canvas.winfo_width()
        frame_height = self.canvas.winfo_height()

        if self.resizing:
            new_x2 = min(max(x2 + dx, x1 + 10), frame_width)
            new_y2 = min(max(y2 + dy, y1 + 10), frame_height)
            self.canvas.coords(self.tag, x1, y1, new_x2, new_y2)
        else:
            new_x1 = min(max(x1 + dx, 0), frame_width - (x2 - x1))
            new_y1 = min(max(y1 + dy, 0), frame_height - (y2 - y1))
            new_x2 = new_x1 + (x2 - x1)
            new_y2 = new_y1 + (y2 - y1)
            self.canvas.coords(self.tag, new_x1, new_y1, new_x2, new_y2)

        self.x, self.y = event.x, event.y

        x1, y1, x2, y2 = self.canvas.coords(self.tag)
        self.canvas.coords(self.text_id, (x1 + x2) / 2, (y1 + y2) / 2)

        # Update handle positions
        self.canvas.coords(self.handles[0], x1 - 3, y1 - 3, x1 + 3, y1 + 3)
        self.canvas.coords(self.handles[1], x1 - 3, y2 - 3, x1 + 3, y2 + 3)
        self.canvas.coords(self.handles[2], x2 - 3, y1 - 3, x2 + 3, y1 + 3)
        self.canvas.coords(self.handles[3], x2 - 3, y2 - 3, x2 + 3, y2 + 3)

    def on_release(self, event):
        self.resizing = False


class VideoEditorGUI(tk.Frame):

    def __init__(self, master):
        self.master = master
        self.master.title("Edge Cutter")
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, bg="black", width=640, height=360)
        self.canvas.pack(pady=(0, 30))
        # Hide the canvas initially
        self.canvas.pack_forget()

        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(side=tk.BOTTOM, pady=(0, 0))

        self.import_button = tk.Button(
            self.button_frame, text="Import Video", command=self.import_video, bg="#0cc0df", fg="white")
        self.import_button.grid(
            row=0, column=0, sticky="nsew", pady=(0, 10), padx=10)

        self.process_button = tk.Button(
            self.button_frame, text="Process Video", command=self.process_data, bg="#0cc0df", fg="white")
        self.process_button.grid(
            row=0, column=1, sticky="nsew", pady=(0, 10), padx=10)
        # Hide the process button initially
        self.process_button.grid_remove()

        self.video_clip = None

        # Move the import button to the center of the frame
        self.import_button.pack(expand=True, ipadx=30,
                                ipady=10, pady=100, padx=100)

        # Configure rows and columns for resizing
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=0)

    def import_video(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            # If no file was selected, move the import button back to the center
            self.import_button.grid_forget()
            self.import_button.pack(expand=True)
            # Hide the canvas
            self.canvas.pack_forget()
            # Hide the process button
            self.process_button.grid_remove()
            return

        # Check if the file extension is supported
        file_extension = os.path.splitext(filepath)[-1].lower()
        supported_extensions = [".mp4", ".mkv", ".avi",
                                ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"]

        if file_extension not in supported_extensions:
            messagebox.showerror(
                "Error", "Import video files only (e.g.  files that end with .mp4, .mkv).")
            return
        # Restore the original button layout
        self.import_button.pack_forget()
        self.import_button.grid(
            row=0, column=0, sticky="nsew", pady=(0, 10), padx=10, ipadx=0, ipady=0)
        # Show the canvas
        self.canvas.pack()
        # Show the process button
        self.process_button.grid()

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

        # Remove previous video and rectangles if they exist
        self.canvas.delete("video")
        if hasattr(self, 'facecam'):
            self.canvas.delete(self.facecam.tag)
        if hasattr(self, 'gameplay'):
            self.canvas.delete(self.gameplay.tag)

        # Add the new video frame
        self.canvas.create_image(
            0, 0, anchor=tk.NW, image=self.video_frame, tags="video")

        # Create the new rectangles
        self.facecam = ResizableRectangle(
            self.canvas, 10, 10, 160, 90, "facecam", "Facecam")
        self.gameplay = ResizableRectangle(
            self.canvas, 170, 10, 470, 270, "gameplay", "Gameplay")

    def process_data(self):
        if not hasattr(self, 'filepath') or not self.filepath:
            messagebox.showerror("Error", "No video file has been imported.")
            return

        clip = VideoFileClip(self.filepath)

        # Calculate scaling factor
        scale_x = clip.size[0] / 640
        scale_y = clip.size[1] / 360

        facecam_coords = self.canvas.coords(self.facecam.tag)
        gameplay_coords = self.canvas.coords(self.gameplay.tag)

        # Scale the coordinates to match the original video dimensions
        facecam_coords = [c * scale_x if i % 2 == 0 else c *
                          scale_y for i, c in enumerate(facecam_coords)]
        gameplay_coords = [c * scale_x if i % 2 == 0 else c *
                           scale_y for i, c in enumerate(gameplay_coords)]

        facecam_clip = clip.crop(
            x1=facecam_coords[0], y1=facecam_coords[1], x2=facecam_coords[2], y2=facecam_coords[3])
        gameplay_clip = clip.crop(
            x1=gameplay_coords[0], y1=gameplay_coords[1], x2=gameplay_coords[2], y2=gameplay_coords[3])

        output_width = 720
        facecam_height = int(1080 / 3)
        gameplay_height = int(1080 * 2 / 3)

        facecam_resized = facecam_clip.resize((output_width, facecam_height))
        gameplay_resized = gameplay_clip.resize(
            (output_width, gameplay_height))

        facecam_position = (0, 0)
        gameplay_position = (0, facecam_height)

        final_clip = CompositeVideoClip([gameplay_resized.set_position(gameplay_position),
                                        facecam_resized.set_position(facecam_position)], size=(output_width, 1080))

        self.cut_video(final_clip)

    def cut_video(self, final_clip):
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4")
        if not output_path:
            return

        final_clip.write_videofile(
            output_path, codec='libx264', audio_codec='aac')

        messagebox.showinfo("Success", "Video has been processed and saved.")
        output_folder = os.path.dirname(output_path)
        # Remove the existing Open Output Folder button if it exists
        if hasattr(self, 'open_folder_button'):
            self.open_folder_button.destroy()
        # Create a new Output Folder button
        open_folder_button = tk.Button(
            self.master, text="Open Output Folder", command=lambda: os.startfile(output_folder), bg="#FFD700")
        open_folder_button.pack(side=tk.BOTTOM, pady=10, padx=10)

    def close_video(self):
        if self.video_clip is not None:
            self.video_clip.close()


def on_close(root, app):
    app.close_video()
    root.destroy()


def main():
    root = tk.Tk()
    root.geometry("800x600")
    root.minsize(800, 600)
    global app
    app = VideoEditorGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root, app))
    root.mainloop()


if __name__ == "__main__":
    main()
