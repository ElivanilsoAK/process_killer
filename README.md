# 🛡️ Process Manager Elite

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

> **A sophisticated, high-performance Process Management tool for Windows.**  
> Built with `CustomTkinter` for a modern GUI and `Rich` for a powerful CLI. Designed to be a safer, clearer, and more beautiful alternative to the native Task Manager.

---

## ✨ Features

*   **🛡️ Smart Protection**: Automatically distinguishes between **User Apps** and **System Services** to prevent accidental system crashes.
*   **🔍 Deep Search Engine**: Finds processes by Name, PID, or **Command Line Arguments** (e.g., searches `java -jar app.jar` by scanning the arguments).
*   **⚡ Threaded Performance**: Non-blocking scanning engine ensures the UI never freezes, even under heavy load.
*   **🎨 Modern Design**: 
    *   **GUI**: Sleek dark mode interface using CustomTkinter.
    *   **CLI**: Beautiful terminal output using Rich tables and panels.
*   **⚠️ Safety First**: Distinct warnings ("CRITICAL WARNING") when attempting to terminate system-critical services.

---

## 📸 Screenshots

| Modern Dark GUI | Powerful CLI |
|:---:|:---:|
| *(Add your screenshot here)* | *(Add your screenshot here)* |

---

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- Windows 10/11 (Recommended)

### Setup
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/process-killer.git
    cd process-killer
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🎮 Usage

### GUI Mode (Default)
Run the application with a modern graphical interface:
```bash
python main.py
```
1.  **Filter**: Use the Sidebar to show only **User Apps** or **Services**.
2.  **Search**: Type in the top bar to filter instantly (supports partial matching).
3.  **Terminate**: Click "End Task". A confirmation popup will appear.

### CLI Mode (Terminal)
Run the application in the command line for text-based management:
```bash
python main.py --cli
```
1.  **Search**: Enter a search term/PID.
2.  **Select**: Choose to kill all matching processes or a specific PID.

---

## 📦 Building form Source

To compile the application into a standalone `.exe`:

```bash
build_gui.bat
```
The executable will be found in the `dist/` folder.

---

## 📂 Project Structure

```text
/
├── assets/             # Icons and images
├── src/                # Source code
│   ├── core/           # Core logic (Scanning, Killing)
│   ├── gui/            # Graphical User Interface (CustomTkinter)
│   └── cli/            # Command Line Interface (Rich)
├── main.py             # Entry point
├── requirements.txt    # Dependencies
└── build_gui.bat       # Build script
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
