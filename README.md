# FileHarbor ⚓

**FileHarbor: Your smart, automated download companion that elegantly sorts new files into designated folders based on their type. Keep your downloads tidy, effortlessly!**

![FileHarbor Screenshot](https://via.placeholder.com/700x500.png?text=FileHarbor+UI+Screenshot+Here)

## ✨ Features

*   **Automatic Monitoring:** Watches a specified "Downloads" folder for new files.
*   **Intelligent Sorting:** Moves files to subfolders based on their extension (e.g., `.pdf` to "Documents", `.jpg` to "Images").
*   **Customizable Mappings:** Easily configure which file types go into which folders via a `config.json` file.
*   **Modern GUI:** A clean and user-friendly interface built with CustomTkinter.
*   **Real-time Activity Log:** See what FileHarbor is doing, including file movements and any errors.
*   **Start/Stop Control:** Manually start or stop the monitoring process at any time.
*   **Configurable Paths:** Easily select your download folder and the main organization folder through the UI.
*   **Initial Scan:** Option to process existing files in the download folder when monitoring starts.
*   **Cross-Platform (Python):** Designed to work on Windows, macOS, and Linux where Python and its dependencies are installed.
*   **Configuration Persistence:** Saves your selected folder paths and mappings for future sessions.

## 🛠️ Prerequisites

*   Python 3.7+
*   `pip` (Python package installer)

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/misutesu-desu/FileHarbor.git
    cd FileHarbor
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    Make sure you have a `requirements.txt` file in your project root with the following content:
    ```txt
    customtkinter
    watchdog
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

1.  **Run the application:**
    ```bash
    python file_harbor.py
    ```

2.  **Initial Setup:**
    *   When you first run the application, the "Downloads Folder" and "Target Organization Folder" fields might be empty or have default paths (if `config.json` exists from a previous run).
    *   Click the **"Browse"** button next to "Downloads Folder (to watch)" to select the folder you want FileHarbor to monitor (e.g., your system's default Downloads folder).
    *   Click the **"Browse"** button next to "Target Organization Folder" to select the root folder where FileHarbor will create subfolders (e.g., "Documents", "Images") and move the sorted files.
        *   **Important:** The Target Organization Folder should ideally not be the same as, or inside, the Downloads Folder to avoid potential processing loops or confusion. The application will warn you if this is the case.
    *   Your chosen paths will be saved in `config.json` for the next time you run the app.

3.  **Start Monitoring:**
    *   Click the **"Start Monitoring"** button.
    *   The status will change to "Monitoring...", and the button will be disabled. The "Stop Monitoring" button will become active.
    *   FileHarbor will now watch the specified Downloads Folder.
    *   When monitoring starts, it will also perform an initial scan of the Downloads Folder and attempt to organize any existing files according to the rules.
    *   Any new files saved or moved into the Downloads Folder will be automatically processed and moved to the appropriate subfolder within your Target Organization Folder.

4.  **Activity Log:**
    *   The "Activity Log" text area will display messages about files being detected, moved, folders being created, and any errors encountered.

5.  **Stop Monitoring:**
    *   Click the **"Stop Monitoring"** button to pause the file organization process. The status will revert to "Idle".

## 📂 File Type Mappings (`config.json`)

FileHarbor uses a `config.json` file (created in the same directory as the script upon first successful path configuration or run) to determine how to categorize files. You can customize these mappings by editing this file.

Example `config.json`:
```json
{
    "download_folder": "C:/Users/YourUser/Downloads",
    "target_folder": "D:/OrganizedFiles",
    "file_type_mappings": {
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".heic", ".webp"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"],
        "Music": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
        "Archives": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
        "Executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".cs", ".php", ".json", ".xml", ".yml", ".yaml"],
        "Torrents": [".torrent"],
        "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
        "Others": []
    }
}
```

*   **`download_folder`**: The absolute path to the folder FileHarbor monitors.
*   **`target_folder`**: The absolute path to the root folder where sorted subfolders will be created.
*   **`file_type_mappings`**: A dictionary where:
    *   Each **key** (e.g., "Documents", "Images") is the name of the subfolder that will be created in the `target_folder`.
    *   Each **value** is a list of file extensions (including the leading dot, e.g., `.pdf`) that belong to that category.
    *   The **`"Others"`** category is a special catch-all. If a file's extension doesn't match any other defined category, it will be moved into the "Others" subfolder. If `Others` is not present, files with unmapped extensions might be handled differently.

## Troubleshooting

*   **Permissions:** Ensure the script has read permissions for the Downloads folder and read/write/create permissions for the Target Organization Folder and its subdirectories.
*   **File In Use:** If a file is still being written or is locked by another application when FileHarbor tries to move it, an error might occur. The script includes a small delay after detection, but very large files or slow writes might still be problematic.
*   **Incorrect Paths:** Double-check that the paths in the UI and `config.json` are correct and point to existing, accessible directories.

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` file for more information.

## 🙏 Acknowledgements

*   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the beautiful modern GUI toolkit.
*   [Watchdog](https://github.com/gorakhargosh/watchdog) for robust file system event monitoring.
*   Anyone whose code or ideas contributed to this project.
