# Process Manager Elite 🛡️

A modern, high-performance Process Management tool for Windows, built with Python and CustomTkinter. Designed to be a safer, clearer alternative to the native Task Manager.

## 🚀 Features

*   **🛡️ Smart Categorization**: Automatically distinguishes between **User Apps** and **System Services** to prevent accidental system crashes.
*   **🔍 Deep Search**: Finds processes by Name, PID, or **Command Line Arguments** (e.g., finds `java -jar app.jar` by searching "app").
*   **⚡ High Performance**: Threaded scanning engine ensures the UI never freezes, even on heavy load.
*   **🎨 Modern Dark UI**: Sleek, professional interface using CustomTkinter.
*   **⚠️ Safety First**: Distinct warnings ("CRITICAL WARNING") when attempting to terminate system-critical services.

## 🛠️ Installation & Build

This application is built as a standalone `.exe`.

### Prerequisites
- Python 3.10+
- `pip install -r requirements.txt`

### Build from Source
To compile the executable yourself:

```bash
run build_gui.bat
```

The output file will be in the `dist/` folder.

## 🎮 Usage

1.  **Run the App**: Open `ProcessKiller_GUI.exe`.
2.  **Filter**: Use the Sidebar to show only **User Apps** or **Services**.
3.  **Search**: Type in the top bar to filter instantly (supports partial matching, accent-insensitive).
4.  **Terminate**: Click "End Task". A confirmation popup will appear.

## 📝 Requirements

*   `customtkinter`
*   `psutil`
*   `pillow`
*   `packaging`
