import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar
import threading
import os
import sys

# Ensure src can be imported even when running from subfolders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import process_all_images


class ImageBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Photoshop Image Builder Automation")
        self.root.geometry("650x200")
        self.create_widgets()

        # Static paths for development
        self.excel_path = r"C:\Users\chota\Desktop\NEW AUTOMATION\PBImageBuilderBU - 1200 x 1800 pxl (1) 2.xlsx" #r"C:\Users\rahul\Desktop\NEW AUTOMATION\PBImageBuilderBU - 1200 x 1800 pxl (1).xlsx"
        
        self.logo_path = r"C:\Users\chota\Desktop\NEW AUTOMATION\LOGO-20250805T171308Z-1-001\LOGO"
        self.image_path = r"C:\Users\chota\Desktop\NEW AUTOMATION\Images-20250805T171308Z-1-001\Images"

    def create_widgets(self):
        tk.Label(self.root, text="Static Development Mode: Using predefined paths", fg="blue").pack(pady=10)

        tk.Button(self.root, text="Start Processing", command=self.start_processing).pack(pady=10)
        self.progress = Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

    def start_processing(self):
        if not all([self.excel_path, self.logo_path, self.image_path]):
            messagebox.showerror("Missing Input", "One or more static paths are missing.")
            return

        self.progress["value"] = 0
        threading.Thread(target=self.run_process).start()

    def run_process(self):
        try:
            process_all_images(
                excel_file=self.excel_path,
                image_folder=self.image_path,
                logo_folder=self.logo_path,
                progress_callback=self.update_progress
            )
            messagebox.showinfo("Done", "All images processed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_progress(self, value):
        self.progress["value"] = value
        self.root.update_idletasks()


if __name__ == '__main__':
    root = tk.Tk()
    app = ImageBuilderGUI(root)
    root.mainloop()


# import tkinter as tk
# from tkinter import filedialog, messagebox
# from tkinter.ttk import Progressbar
# import threading
# import os
# import sys

# # Ensure src can be imported even when running from subfolders
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from src.main import process_all_images


# class ImageBuilderGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Photoshop Image Builder Automation")
#         self.root.geometry("650x420")
#         self.create_widgets()

#     def create_widgets(self):
#         tk.Label(self.root, text="Select Excel File:").pack(pady=5)
#         self.excel_path = tk.StringVar()
#         tk.Entry(self.root, textvariable=self.excel_path, width=60).pack()
#         tk.Button(self.root, text="Browse", command=self.browse_excel).pack(pady=5)

#         tk.Label(self.root, text="Select Logo Folder:").pack(pady=5)
#         self.logo_path = tk.StringVar()
#         tk.Entry(self.root, textvariable=self.logo_path, width=60).pack()
#         tk.Button(self.root, text="Browse", command=self.browse_logo).pack(pady=5)

#         tk.Label(self.root, text="Select Input Images Folder:").pack(pady=5)
#         self.image_path = tk.StringVar()
#         tk.Entry(self.root, textvariable=self.image_path, width=60).pack()
#         tk.Button(self.root, text="Browse", command=self.browse_images).pack(pady=5)

#         tk.Button(self.root, text="Start Processing", command=self.start_processing).pack(pady=10)
#         self.progress = Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
#         self.progress.pack(pady=10)

#     def browse_excel(self):
#         path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
#         if path:
#             self.excel_path.set(path)

#     def browse_logo(self):
#         path = filedialog.askdirectory()
#         if path:
#             self.logo_path.set(path)

#     def browse_images(self):
#         path = filedialog.askdirectory()
#         if path:
#             self.image_path.set(path)

#     def start_processing(self):
#         if not all([self.excel_path.get(), self.logo_path.get(), self.image_path.get()]):
#             messagebox.showerror("Missing Input", "Please select all required paths.")
#             return

#         self.progress["value"] = 0
#         threading.Thread(target=self.run_process).start()

#     def run_process(self):
#         try:
#             process_all_images(
#                 excel_file=self.excel_path.get(),
#                 image_folder=self.image_path.get(),
#                 logo_folder=self.logo_path.get(),
#                 progress_callback=self.update_progress
#             )
#             messagebox.showinfo("Done", "All images processed successfully!")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))

#     def update_progress(self, value):
#         self.progress["value"] = value
#         self.root.update_idletasks()


# if __name__ == '__main__':
#     root = tk.Tk()
#     app = ImageBuilderGUI(root)
#     root.mainloop()
