# 🛠️ Minecraft Crash Issue Detector

![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/github/license/Moriggan/Minecraft-Crash-Issue-Detector) 
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey)
<!-- You can update these badge URLs to match your actual GitHub repo -->

A fully automated tool to diagnose, scan, and suggest fixes for Minecraft mod crashes.  
Built with Python + PyQt5, powered by GitHub AI, CurseForge APIs, and smart mod detection.

---

## ✨ Features

- 🔍 Scan latest.log and crash report files for crash errors automatically
- 🧠 AI-based crash issue suggestions from GitHub repositories
- ⚙️ Detects suspected mods causing crashes
- 🔄 Fetches known mod conflicts from a live database
- 🧵 Multi-threaded scanning (no freezing UI)
- 📦 Mod Compatibility Checker (with conflict suggestions)
- 🧬 Auto-detects missing classes inside .jar mod files
- 🛰️ (Coming soon) Auto-resolve mod names via CurseForge API

---

## 🛡 Requirements

- Python 3.8 or higher
- Required modules:
  - PyQt5
  - requests

---

## 📦 Install Dependencies

Using pip:

```bash
pip install PyQt5 requests
```

Optional: Create and activate a virtual environment:

```bash
python -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

---

## 🖥️ Convert to .exe (for Windows)

Want to share your app with non-Python users? You can bundle it as a standalone Windows executable.

1. Install PyInstaller:

```bash
pip install pyinstaller
```

2. Run the build command (also saved in cmd.txt):

```bash
pyinstaller --onefile --noconsole --icon=mod_analyzer.ico crash_analyzer.py
```

- --onefile: Bundles everything into a single .exe  
- --noconsole: Suppresses console (for GUI apps)  
- --icon: Uses your custom icon  

3. Your compiled app will be located in the dist/ folder.

---

## 💬 Credits

- Data fetched using [GitHub](https://github.com/) APIs and [CurseForge](https://curseforge.com/)
- Minecraft is a trademark of Mojang AB. This tool is not affiliated with Mojang or Microsoft.

---

## 📜 License

MIT License  
Feel free to fork, improve, and contribute!
