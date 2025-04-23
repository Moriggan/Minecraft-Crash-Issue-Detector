# 🛠️ Minecraft Crash Issue Detector

A fully automated tool to diagnose, scan, and suggest fixes for Minecraft mod crashes.
Built with Python + PyQt5, powered by GitHub AI, CurseForge APIs, and smart mod detection.

---

## ✨ Features

- 🔍 Scan `latest.log` and crash report files for crash errors automatically
- 🧠 AI-based crash issue suggestions from GitHub repositories
- ⚙️ Detects suspected mods causing crashes
- 🔄 Fetches known mod conflicts from a live database
- 🧵 Multi-threaded scanning (no freezing UI)
- 📦 Mod Compatibility Checker (with conflict suggestions)
- 🧬 Auto-detects missing classes inside `.jar` mod files
- 🛰️ (Coming soon) Auto-resolve mod names via CurseForge API

---

## 🛡 Requirements

- Python 3.8+
- PyQt5
- requests

### 📦 Install Requirements
```bash
pip install PyQt5 requests
```

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate    # On Windows
```

---

## 📦 How to Convert into .exe (Windows)

Want to share with others who don't have Python installed? Create a standalone `.exe`!

### Steps:

1. Install PyInstaller:
```bash
pip install pyinstaller
```
2. Inside your project folder, run the command saved inside `cmd.txt`, or manually:
```bash
pyinstaller --onefile --noconsole --icon=mod_analyzer.ico crash_analyzer.py
```

- `--onefile`: Bundles everything into a single `.exe`
- `--noconsole`: Hides the console window (for GUI apps)
- `--icon=mod_analyzer.ico`: Adds your custom icon.

3. After building, your `.exe` will be inside the `dist/` folder.

---

## 💬 Credits

- Data fetched from [GitHub](https://github.com/) and [CurseForge](https://curseforge.com/)
- Minecraft is a trademark of Mojang AB. This project is not affiliated with Mojang or Microsoft.

---

## 📜 License

MIT License. Feel free to fork, improve, and contribute!
