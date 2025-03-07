import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import sys
import re
import subprocess
from urllib.parse import urlparse

class CoverageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Coverage Cleaner")
        self.root.geometry("400x250")

        # Get the directory of the EXE (when running from an installer)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "cleaner.ico")  # Absolute path to the icon

        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)  # Set the icon
        else:
            messagebox.showwarning("Warning", "Icon file not found!")

        # Label
        self.label = tk.Label(root, text="Select your coverage json file:")
        self.label.pack(pady=5)

        # Entry box to display file path
        self.file_entry = tk.Entry(root, width=50)
        self.file_entry.pack(pady=5)

        # Browse Button
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Process Button
        self.process_button = tk.Button(root, text="Run", command=self.run_it_down)
        self.process_button.pack(pady=5)

        # Set output folder location to user's Documents folder
        user_documents = os.path.expanduser("~\\Documents")
        self.output_folder = os.path.join(user_documents, "Coverage_Output")  # You can change the folder name

        # Open Output Folder Button
        self.open_folder_button = tk.Button(root, text="Open Output Folder", command=self.open_output_folder)
        self.open_folder_button.pack(pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        self.file_entry.delete(0, tk.END)  # Clear existing text
        self.file_entry.insert(0, file_path)  # Insert selected file path

    def extract_filename_from_url(self, url):
        """Extracts a valid filename from a URL (rightmost part after last /)."""
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip("/").split("/")  # Split by "/"
        
        filename = path_parts[-1] if path_parts else "default_name"  # Take last part
        if not filename:  
            filename = path_parts[-2] if len(path_parts) > 1 else "default_name"  # Backup

        # Remove invalid filename characters
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return safe_filename

    def run_it_down(self):
        file_path = self.file_entry.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file!")
            return
        
        try:
            # Check and create output folder if it doesn't exist
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            with open(file_path, 'r', encoding='utf-8') as file:
                coverage_data = json.load(file)

            for entry in coverage_data:
                url = entry.get("url")
                ranges = entry.get("ranges")
                text = entry.get("text")

                if not url:
                    continue  # Skip entries with no URL

                filename = self.extract_filename_from_url(url)
                output_file_path = os.path.join(self.output_folder, filename)

                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    for range_item in ranges:
                        start = range_item.get('start')
                        end = range_item.get('end')
                        substring = text[start:end]
                        output_file.write(substring)

            messagebox.showinfo("Success", f"Processing complete! Files saved in '{self.output_folder}'")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{str(e)}")

    def open_output_folder(self):
        """Opens the output folder in the file explorer."""
        # If the folder doesn't exist, create it
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        if os.path.exists(self.output_folder):
            subprocess.run(["explorer", os.path.abspath(self.output_folder)], shell=True)
        else:
            messagebox.showerror("Error", "Output folder not found!")

# Run Tkinter app
root = tk.Tk()
app = CoverageProcessor(root)
root.mainloop()
