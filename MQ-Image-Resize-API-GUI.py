from PIL import Image, ImageOps
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import subprocess
import requests
import io
import shutil
import xml.etree.ElementTree as ET


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
        tk.Label(self.root, text="Enter SKU Value:").pack()
        self.sku_entry = tk.Entry(self.root)
        self.sku_entry.pack()
        tk.Button(
            self.root,
            text="Download and Process Images",
            command=self.download_and_process_images,
        ).pack()
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

    def download_images(self, sku):
        api_url = f"https://wholesale.williams-trading.com/rest/product-images/{sku}?format=xml"
        response = requests.get(api_url)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            image_urls = []

            # Find all image_large_url elements and extract the URLs
            for image_elem in root.findall(".//image_large_url"):
                image_url = image_elem.text
                image_urls.append(image_url)
                print("Image URL:", image_url)

            output_folder = self.output_folder.get()
            sku_folder = os.path.join(output_folder, sku)
            os.makedirs(sku_folder, exist_ok=True)

            original_images_folder = os.path.join(sku_folder, "original_images")
            os.makedirs(original_images_folder, exist_ok=True)

            for index, image_url in enumerate(image_urls):
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    image_data = image_response.content
                    image = Image.open(io.BytesIO(image_data))

                    # Convert the image to RGB mode if it's in RGBA mode
                    if image.mode == "RGBA":
                        image = image.convert("RGB")

                    image_filename = f"{sku}_{index+1}.jpg"
                    image_path = os.path.join(original_images_folder, image_filename)
                    image.save(image_path, "JPEG")

            print("Original images downloaded and saved.")

    def download_and_process_images(self):
        sku = self.sku_entry.get()
        output_name = self.output_name.get()

        if not output_name:
            name_api_url = (
                f"https://wholesale.williams-trading.com/rest/products/{sku}?format=xml"
            )
            name_response = requests.get(name_api_url)

            if name_response.status_code == 200:
                name_root = ET.fromstring(name_response.content)
                output_name = name_root.find(".//name").text

        if sku and output_name:
            self.download_images(sku)

            output_folder = os.path.join(self.output_folder.get(), output_name)
            os.makedirs(output_folder, exist_ok=True)

            sku_folder = os.path.join(self.output_folder.get(), sku)
            image_files = [
                file
                for file in os.listdir(os.path.join(sku_folder, "original_images"))
                if file.endswith(".jpg")
            ]

            self.input_images.extend(
                os.path.join(sku_folder, "original_images", image_file)
                for image_file in image_files
            )
            self.update_selected_images_listbox()

            # Automatically run the resize_and_pad_images function for the downloaded images
            self.resize_and_pad_images(output_folder)
        else:
            print("Please enter a valid SKU value and Output Name.")

    def browse_output_folder(self):
        default_output_folder = self.output_folder.get()
        folder = filedialog.askdirectory(initialdir=default_output_folder)
        self.output_folder.set(folder)

    def resize_and_pad_images(self, output_folder):
        output_name = self.output_name.get()

        if not output_name:  # If output_name is blank, use the SKU as the output_name
            output_name = self.sku_entry.get()

        current_date = datetime.now().strftime("%Y-%m-%d")
        output_folder = os.path.join(output_folder, current_date)

        os.makedirs(output_folder, exist_ok=True)

        for i, image_path in enumerate(self.input_images):
            img = Image.open(image_path)

            img.thumbnail(self.target_size, Image.LANCZOS)

            background = Image.new("RGB", self.target_size, (255, 255, 255))

            paste_x = (self.target_size[0] - img.width) // 2
            paste_y = (self.target_size[1] - img.height) // 2

            background.paste(img, (paste_x, paste_y))

            output_filename = f"{output_name}_{i+1}.jpg"
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
