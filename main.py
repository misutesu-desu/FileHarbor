import os
import shutil
import json
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext

CONFIG_FILE = "config.json"

DEFAULT_MAPPINGS = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".heic", ".webp"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"],
    "Music": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
    "Executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".cs", ".php", ".json", ".xml", ".yml", ".yaml"],
    "Torrents": [".torrent"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
    "Others": [] # Catch-all for unmapped extensions
}

class ConfigManager:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file_path, 'r') as f:
                config_data = json.load(f)
                # Ensure all necessary keys exist
                if "download_folder" not in config_data:
                    config_data["download_folder"] = ""
                if "target_folder" not in config_data:
                    config_data["target_folder"] = ""
                if "file_type_mappings" not in config_data:
                    config_data["file_type_mappings"] = DEFAULT_MAPPINGS.copy()
                # Ensure 'Others' category exists for safety
                if "Others" not in config_data["file_type_mappings"]:
                     config_data["file_type_mappings"]["Others"] = []
                return config_data
        except FileNotFoundError:
            self.log_message(f"Config file not found. Creating '{self.config_file_path}' with defaults.")
            return {
                "download_folder": "",
                "target_folder": "",
                "file_type_mappings": DEFAULT_MAPPINGS.copy()
            }
        except json.JSONDecodeError:
            self.log_message(f"Error decoding JSON from '{self.config_file_path}'. Using defaults.", "error")
            return {
                "download_folder": "",
                "target_folder": "",
                "file_type_mappings": DEFAULT_MAPPINGS.copy()
            }

    def save_config(self):
        try:
            with open(self.config_file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.log_message("Configuration saved.", "info")
        except IOError:
            self.log_message(f"Error saving configuration to '{self.config_file_path}'.", "error")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

    # Placeholder for log_message, will be set by App
    def log_message(self, message, level="info"):
        print(f"[{level.upper()}] {message}")


class FileOrganizer:
    def __init__(self, target_base_folder, mappings, log_callback):
        self.target_base_folder = target_base_folder
        self.mappings = mappings
        self.log = log_callback

    def get_category_for_extension(self, extension):
        ext_lower = extension.lower()
        for category, extensions in self.mappings.items():
            if ext_lower in extensions:
                return category
        return "Others" # Default category if no match

    def organize_file(self, file_path):
        if not os.path.isfile(file_path):
            # self.log(f"Skipping '{os.path.basename(file_path)}' as it's a directory or no longer exists.")
            return

        # Avoid processing temporary download files or already processed files in target
        if os.path.dirname(file_path) == self.target_base_folder or \
           any(file_path.endswith(temp_ext) for temp_ext in ['.tmp', '.crdownload', '.part']):
            return

        filename = os.path.basename(file_path)
        _, extension = os.path.splitext(filename)

        if not extension:
            category_folder_name = "NoExtension" # Or handle as 'Others'
        else:
            category_folder_name = self.get_category_for_extension(extension)

        target_category_path = os.path.join(self.target_base_folder, category_folder_name)

        try:
            if not os.path.exists(target_category_path):
                os.makedirs(target_category_path)
                self.log(f"Created folder: '{target_category_path}'")

            destination_path = os.path.join(target_category_path, filename)

            # Handle file name conflicts
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(destination_path):
                destination_path = os.path.join(target_category_path, f"{base_name}_{counter}{ext}")
                counter += 1
            
            shutil.move(file_path, destination_path)
            self.log(f"Moved: '{filename}' to '{category_folder_name}'")

        except Exception as e:
            self.log(f"Error moving '{filename}': {e}", "error")


class WatcherHandler(FileSystemEventHandler):
    def __init__(self, organizer, log_callback, app_instance):
        self.organizer = organizer
        self.log = log_callback
        self.app = app_instance # To schedule GUI updates on the main thread

    def on_created(self, event):
        if not event.is_directory:
            # Give a small delay for the file to be fully written
            time.sleep(1) # Adjust if files are large or write slowly
            self.log(f"New file detected: {event.src_path}")
            # Schedule the organization task on the main GUI thread
            self.app.after(100, lambda: self.organizer.organize_file(event.src_path))

    def on_modified(self, event):
        # This can be noisy. Often on_created is enough for downloads.
        # Only process if it's a file and it has finished downloading (heuristics)
        # This is tricky because "modified" fires many times during download.
        # Consider checking if the file size has stabilized.
        # For now, we primarily rely on on_created.
        pass


class App(ctk.CTk):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        config_manager.log_message = self.log_message # Link config manager's logger

        self.title("FileHarbor - Automatic File Sorter")
        self.geometry("700x550")
        ctk.set_appearance_mode("System") # "Dark", "Light"
        ctk.set_default_color_theme("blue") # "blue", "green", "dark-blue"

        self.observer = None
        self.organizer = None
        self.is_monitoring = False
        self.monitoring_thread = None

        # --- Main frame ---
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # --- Configuration Frame ---
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(pady=10, padx=10, fill="x")

        # Download Folder
        ctk.CTkLabel(config_frame, text="Downloads Folder (to watch):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.download_folder_var = ctk.StringVar(value=self.config_manager.get("download_folder", ""))
        self.download_folder_entry = ctk.CTkEntry(config_frame, textvariable=self.download_folder_var, width=300)
        self.download_folder_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="Browse", command=self.browse_download_folder).grid(row=0, column=2, padx=5, pady=5)

        # Target Organization Folder
        ctk.CTkLabel(config_frame, text="Target Organization Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.target_folder_var = ctk.StringVar(value=self.config_manager.get("target_folder", ""))
        self.target_folder_entry = ctk.CTkEntry(config_frame, textvariable=self.target_folder_var, width=300)
        self.target_folder_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(config_frame, text="Browse", command=self.browse_target_folder).grid(row=1, column=2, padx=5, pady=5)
        
        config_frame.columnconfigure(1, weight=1) # Make entry expand

        # --- Controls Frame ---
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(pady=10, padx=10, fill="x")

        self.start_button = ctk.CTkButton(controls_frame, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(side="left", padx=10, pady=10)

        self.stop_button = ctk.CTkButton(controls_frame, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(side="left", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(controls_frame, text="Status: Idle", text_color="gray")
        self.status_label.pack(side="right", padx=10, pady=10)


        # --- Log Display ---
        log_label = ctk.CTkLabel(main_frame, text="Activity Log:")
        log_label.pack(pady=(10,0), padx=10, anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=70, relief="sunken", borderwidth=1,
                                                  bg=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"]),
                                                  fg=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"]),
                                                  insertbackground=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkEntry"]["text_color"]),
                                                  selectbackground=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkEntry"]["select_background_color"]),
                                                  selectforeground=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkEntry"]["select_foreground_color"])
                                                  )
        self.log_text.pack(pady=10, padx=10, fill="both", expand=True)
        self.log_text.configure(state='disabled') # Make it read-only initially

        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close

        # Initial log messages
        self.log_message("FileHarbor initialized. Please configure folders and start monitoring.", "info")
        if not self.config_manager.get("download_folder") or not self.config_manager.get("target_folder"):
            self.log_message("Warning: Download or Target folder not set. Please configure.", "warning")


    def log_message(self, message, level="info"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level.upper()}] {message}\n"
        
        self.log_text.configure(state='normal') # Enable writing
        if level == "error":
            self.log_text.insert(ctk.END, formatted_message, "error_tag")
        elif level == "warning":
            self.log_text.insert(ctk.END, formatted_message, "warning_tag")
        else: # info or debug
            self.log_text.insert(ctk.END, formatted_message, "info_tag")
        
        self.log_text.configure(state='disabled') # Disable writing
        self.log_text.see(ctk.END) # Scroll to the end

        # Define tags for coloring if not already defined
        # These colors are examples, might need adjustment for light/dark themes
        if not self.log_text.tag_cget("error_tag", "foreground"):
            self.log_text.tag_configure("error_tag", foreground="red")
        if not self.log_text.tag_cget("warning_tag", "foreground"):
            self.log_text.tag_configure("warning_tag", foreground="orange")
        if not self.log_text.tag_cget("info_tag", "foreground"):
            self.log_text.tag_configure("info_tag", foreground=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"]))


    def browse_download_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.download_folder_var.set(folder_selected)
            self.config_manager.set("download_folder", folder_selected)
            self.config_manager.save_config()
            self.log_message(f"Download folder set to: {folder_selected}")

    def browse_target_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.target_folder_var.set(folder_selected)
            self.config_manager.set("target_folder", folder_selected)
            self.config_manager.save_config()
            self.log_message(f"Target organization folder set to: {folder_selected}")

    def _validate_paths(self):
        download_folder = self.download_folder_var.get()
        target_folder = self.target_folder_var.get()

        if not download_folder or not os.path.isdir(download_folder):
            messagebox.showerror("Error", "Invalid Downloads Folder path. Please select a valid directory.")
            self.log_message("Invalid Downloads Folder path.", "error")
            return False
        if not target_folder or not os.path.isdir(target_folder): # Check if target exists, or can be created
            try:
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder) # Try to create if not exists
                    self.log_message(f"Target folder '{target_folder}' did not exist. Created successfully.", "info")
                elif not os.path.isdir(target_folder): # Exists but is not a directory
                    messagebox.showerror("Error", f"Target Organization Folder path '{target_folder}' exists but is not a directory.")
                    self.log_message(f"Target path '{target_folder}' is not a directory.", "error")
                    return False
            except OSError as e:
                 messagebox.showerror("Error", f"Cannot create or access Target Organization Folder: {target_folder}\n{e}")
                 self.log_message(f"Cannot create/access Target folder '{target_folder}': {e}", "error")
                 return False
        
        if download_folder == target_folder:
            messagebox.showerror("Error", "Downloads Folder and Target Organization Folder cannot be the same.")
            self.log_message("Downloads and Target folders cannot be the same.", "error")
            return False
        
        # Check if target folder is a subfolder of download_folder (potential loop)
        # Or vice versa, though less likely to cause a direct loop
        if os.path.abspath(target_folder).startswith(os.path.abspath(download_folder) + os.sep):
            warn = messagebox.askyesno("Warning", "The Target Organization Folder is inside the Downloads Folder. "
                                       "This might lead to unexpected behavior or re-processing of files.\n"
                                       "Are you sure you want to continue?")
            if not warn:
                self.log_message("User cancelled due to Target folder being inside Download folder.", "warning")
                return False
        return True

    def start_monitoring(self):
        if not self._validate_paths():
            return

        download_folder = self.download_folder_var.get()
        target_folder = self.target_folder_var.get()
        
        # Ensure mappings are up-to-date from config if it was edited externally
        self.config_manager.config = self.config_manager.load_config()
        file_mappings = self.config_manager.get("file_type_mappings", DEFAULT_MAPPINGS.copy())

        self.organizer = FileOrganizer(target_folder, file_mappings, self.log_message)
        event_handler = WatcherHandler(self.organizer, self.log_message, self)
        
        self.observer = Observer()
        try:
            self.observer.schedule(event_handler, download_folder, recursive=False) # Watch only top-level
            self.observer.start()
            self.is_monitoring = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_label.configure(text="Status: Monitoring...", text_color="green")
            self.log_message(f"Started monitoring folder: {download_folder}", "info")

            # Check for existing files once on start
            self.log_message("Checking for existing files in download folder...", "info")
            for item in os.listdir(download_folder):
                item_path = os.path.join(download_folder, item)
                if os.path.isfile(item_path):
                    self.organizer.organize_file(item_path)
            self.log_message("Initial scan complete.", "info")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {e}")
            self.log_message(f"Failed to start monitoring: {e}", "error")
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
            self.observer = None
            self.is_monitoring = False

    def stop_monitoring(self):
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            # self.observer.join() # This can block the GUI, consider if needed or timeout
            self.log_message("File monitoring stopped by user.", "info")
        
        # Wait for thread to finish (optional, but good for clean shutdown)
        # if self.monitoring_thread and self.monitoring_thread.is_alive():
        #     self.monitoring_thread.join(timeout=2) # Give it 2 seconds to finish

        self.observer = None
        self.is_monitoring = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Status: Idle", text_color="gray")


    def on_closing(self):
        if self.is_monitoring:
            if messagebox.askyesno("Confirm Exit", "Monitoring is active. Do you want to stop monitoring and exit?"):
                self.stop_monitoring()
            else:
                return # Don't close
        
        # Save current paths even if not changed via browse, but via typing
        self.config_manager.set("download_folder", self.download_folder_var.get())
        self.config_manager.set("target_folder", self.target_folder_var.get())
        self.config_manager.save_config()
        
        self.destroy()


if __name__ == "__main__":
    config_mgr = ConfigManager(CONFIG_FILE)
    app = App(config_mgr)
    app.mainloop()
