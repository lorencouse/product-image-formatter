from PIL import Image, ImageOps
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import subprocess


class ImageResizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer")

        self.input_images = []
        self.output_folder = tk.StringVar(
            value="/Users/lorencouse/My Drive/Websites/Male Q/Graphics/Store/Products/Resized"
        )
        self.target_size = (650, 650)
        self.output_name = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        tk.Button(
            self.root, text="Select Input Images", command=self.select_input_images
        ).pack()
        tk.Label(self.root, text="Selected Images:").pack()
        self.selected_images_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.selected_images_listbox.pack()
        tk.Label(self.root, text="Output Folder:").pack()
        tk.Entry(self.root, textvariable=self.output_folder).pack()
        tk.Button(self.root, text="Browse", command=self.browse_output_folder).pack()
        tk.Label(self.root, text="Output Name:").pack()
        tk.Entry(self.root, textvariable=self.output_name).pack()
        tk.Button(
            self.root, text="Resize and Pad Images", command=self.resize_and_pad_images
        ).pack()

    def select_input_images(self):
        downloads_folder = str(Path.home() / "Downloads")
        self.input_images = filedialog.askopenfilenames(
            initialdir=downloads_folder,
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")],
        )
        if not isinstance(self.input_images, str):
            self.input_images = list(self.input_images)
            self.update_selected_images_listbox()

    def update_selected_images_listbox(self):
        self.selected_images_listbox.delete(0, tk.END)
        for image_path in self.input_images:
            _, image_filename = os.path.split(image_path)
            self.selected_images_listbox.insert(tk.END, image_filename)

    def browse_output_folder(self):
        default_output_folder = self.output_folder.get()
        folder = filedialog.askdirectory(initialdir=default_output_folder)
        self.output_folder.set(folder)

    def resize_and_pad_images(self):
        output_name = self.output_name.get()

        current_date = datetime.now().strftime("%Y-%m-%d")
        output_folder = os.path.join(self.output_folder.get(), current_date)

        os.makedirs(output_folder, exist_ok=True)

        for i, image_path in enumerate(self.input_images):
            img = Image.open(image_path)

            img.thumbnail(self.target_size, Image.LANCZOS)

            background = Image.new("RGB", self.target_size, (255, 255, 255))

            paste_x = (self.target_size[0] - img.width) // 2
            paste_y = (self.target_size[1] - img.height) // 2

            background.paste(img, (paste_x, paste_y))

            output_filename = f"{output_name}_{i+1}.jpg"  # Output name followed by a number and ".jpg"
            output_path = os.path.join(output_folder, output_filename)
            background.save(output_path, "JPEG")

        print("Batch resizing and padding complete.")

        # Open the output directory when completed
        try:
            subprocess.Popen(["open", output_folder])  # macOS
        except FileNotFoundError:
            try:
                subprocess.Popen(["xdg-open", output_folder])  # Linux
            except FileNotFoundError:
                try:
                    subprocess.Popen(["explorer", output_folder])  # Windows
                except FileNotFoundError:
                    print("Couldn't automatically open the output directory.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageResizerGUI(root)
    root.mainloop()
