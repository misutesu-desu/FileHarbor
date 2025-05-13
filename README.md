```markdown
# FileHarbor ⚓

**FileHarbor: Your smart, automated download companion that elegantly sorts new files into designated folders based on their type. Keep your downloads tidy, effortlessly!**

![FileHarbor Screenshot](https://via.placeholder.com/600x400.png?text=FileHarbor+UI+Screenshot+Here)
*(Replace the placeholder above with an actual screenshot of the application)*

## ✨ Features

*   **Automatic Monitoring:** Watches a specified "Downloads" folder for new files.
*   **Intelligent Sorting:** Moves files to subfolders based on their extension (e.g., `.pdf` to "Documents", `.jpg` to "Images").
*   **Customizable Mappings:** Easily configure which file types go into which folders via a `config.json` file.
*   **Modern GUI:** A clean and user-friendly interface built with CustomTkinter.
*   **Log Display:** See what FileHarbor is doing in real-time.
*   **Start/Stop Control:** Manually start or stop the monitoring process.
*   **Configurable Paths:** Choose your download and target organization folders.
*   **Cross-Platform (Python):** Should work on Windows, macOS, and Linux where Python is installed.

## 🛠️ Prerequisites

*   Python 3.7+
*   `pip` (Python package installer)

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/FileHarbor.git
    cd FileHarbor
    ```

2.  **Install dependencies:**
    It's highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
    Then install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

    The `requirements.txt` file should contain:
    ```
    customtkinter
    watchdog
    ```

## 🚀 Usage

1.  **Run the application:**
    ```bash
    python file_harbor.py
    ```

2.  **Configuration:**
    *   On the first run, or if `config.json` is missing, default paths and mappings will be used.
    *   Use the "Browse" buttons to select your **Downloads Folder** (the folder to monitor) and the **Target Organization Folder** (where sorted subfolders will be created).
    *   The application will save your chosen paths in `config.json` for future sessions.
    *   Click **"Start Monitoring"**. FileHarbor will now watch the Downloads Folder.
    *   When a new file appears in the Downloads Folder, it will be moved to the appropriate subfolder within your Target Organization Folder.
    *   Click **"Stop Monitoring"** to pause the process.

## 📂 File Type Mappings (`config.json`)

You can customize how files are sorted by editing the `file_type_mappings` section in the `config.json` file (created after the first run or manually).

Example `config.json`:
```json
{
    "download_folder": "C:/Users/YourUser/Downloads",
    "target_folder": "D:/OrganizedFiles",
    "file_type_mappings": {
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".ppt", ".pptx", ".xls", ".xlsx"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".heic"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv"],
        "Music": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
        "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
        "Executables": [".exe", ".msi", ".dmg", ".pkg"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".cs", ".php"],
        "Torrents": [".torrent"],
        "Others": []
    }
}
```
*   Files with extensions not listed in any category will be moved to the "Others" folder (if defined) or a folder named after their extension if "Others" is not a key.
*   The `Others: []` entry acts as a catch-all. If an extension isn't found elsewhere, and `Others` exists, it goes there. If `Others` doesn't exist, a folder for that specific extension (e.g., `.xyz_files`) might be created, or you can modify the script to handle it differently.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgements

*   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI.
*   [Watchdog](https://github.com/gorakhargosh/watchdog) for file system monitoring.
```
