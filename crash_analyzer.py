# --- Minecraft Crash Detector FULL SCRIPT (ALL FEATURES) ---
import sys, os, re, json, zipfile, traceback, threading, requests, time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QFileDialog, QLineEdit, QHBoxLayout, QTabWidget
)
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal

# --- Configuration ---
GITHUB_TOKEN = "YOUR TOKEN HERE"
GITHUB_API_URL = "https://api.github.com/search/issues?q="
LIVE_CONFLICTS_URL = "https://raw.githubusercontent.com/yourusername/mc-mod-conflicts/main/conflicts.json"
CACHE_FOLDER = ".cache"
CACHE_EXPIRE_HOURS = {
    "conflicts": 48,
    "github_issues": 168,
    "mod_versions": 24
}

CRASH_FIX_PATTERNS = {
    "NullPointerException": "Mod tried to access a null value. Reset configs or remove broken mod.",
    "ClassNotFoundException": "Missing dependency. Make sure all required mods are installed.",
    "Mixin apply failed": "A mod Mixin failed. Check for outdated Fabric API or mod conflicts.",
    "VerifyError": "Bytecode error. Likely coremod patch conflict.",
}

# --- Cache Manager ---
def ensure_cache_folder():
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)

def cache_path(name):
    return os.path.join(CACHE_FOLDER, f"{name}.json")

def load_cache(name):
    try:
        with open(cache_path(name), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_cache(name, data):
    ensure_cache_folder()
    with open(cache_path(name), "w", encoding="utf-8") as f:
        json.dump({"data": data, "timestamp": time.time()}, f)

def is_cache_expired(name, hours):
    try:
        with open(cache_path(name), "r", encoding="utf-8") as f:
            obj = json.load(f)
            return time.time() - obj.get("timestamp", 0) > hours * 3600
    except Exception:
        return True

def get_cached_data(name):
    obj = load_cache(name)
    return obj.get("data", {}) if isinstance(obj, dict) else {}

# --- Conflict Engine ---
class ConflictEngine:
    def __init__(self):
        self.conflict_data = {}

    def load_or_fetch_conflicts(self):
        if is_cache_expired("conflicts", CACHE_EXPIRE_HOURS["conflicts"]):
            try:
                r = requests.get(LIVE_CONFLICTS_URL, timeout=5)
                if r.status_code == 200:
                    self.conflict_data = r.json()
                    save_cache("conflicts", self.conflict_data)
            except:
                self.conflict_data = get_cached_data("conflicts")
        else:
            self.conflict_data = get_cached_data("conflicts")

    def get_fix(self, modname):
        return self.conflict_data.get(modname.lower(), {}).get("fix")

conflict_engine = ConflictEngine()
conflict_engine.load_or_fetch_conflicts()

# --- GitHub AI Engine ---
class GitHubAIScanner:
    def __init__(self, token):
        self.token = token
        self.cached = get_cached_data("github_issues")

    def search_crash_issue(self, error_line):
        if error_line in self.cached and not is_cache_expired("github_issues", CACHE_EXPIRE_HOURS["github_issues"]):
            return self.cached[error_line]
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        query = f'{GITHUB_API_URL}"{error_line}" in:title,body repo:minecraft mod crash'
        try:
            r = requests.get(query, headers=headers, timeout=8)
            if r.status_code == 200:
                data = r.json()
                if data.get("items"):
                    top = data["items"][0]
                    suggestion = f"{top['title']} → {top['html_url']}"
                    self.cached[error_line] = suggestion
                    save_cache("github_issues", self.cached)
                    return suggestion
        except Exception:
            return None
        return None

ai_engine = GitHubAIScanner(GITHUB_TOKEN)

# --- GUI Application ---
class CrashDetector(QWidget):
    mod_scan_result = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minecraft Crash Detector")
        self.setGeometry(100, 100, 950, 700)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.log_tab = QWidget()
        self.mods_tab = QWidget()
        self.tabs.addTab(self.log_tab, "Crash Log Scanner")
        self.tabs.addTab(self.mods_tab, "Mod Compatibility Checker")

        self.setup_log_tab()
        self.setup_mods_tab()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.mod_scan_result.connect(self.update_mod_output)

    def setup_log_tab(self):
        layout = QVBoxLayout()
        path_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        browse_btn = QPushButton("Browse Folder")
        browse_btn.clicked.connect(self.browse_folder)
        path_layout.addWidget(QLabel("Minecraft Folder:"))
        path_layout.addWidget(self.folder_input)
        path_layout.addWidget(browse_btn)

        scan_btn = QPushButton("Scan latest.log")
        scan_btn.clicked.connect(self.scan_log)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: #111; color: #0f0; font-family: Consolas;")

        layout.addLayout(path_layout)
        layout.addWidget(scan_btn)
        layout.addWidget(self.output)
        self.log_tab.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Minecraft Folder")
        if folder:
            self.folder_input.setText(folder)

    def scan_log(self):
        try:
            path = os.path.join(self.folder_input.text(), "logs", "latest.log")
            if not os.path.exists(path):
                self.output.setText("❌ latest.log not found!")
                return
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                log = f.read()
            result = self.analyze_log(log)
            self.output.setText(result)
            self.output.moveCursor(QTextCursor.Start)
        except Exception as e:
            self.output.setText(f"❌ Error analyzing log:\n{e}\n{traceback.format_exc()}")

    def analyze_log(self, log):
        report = []
        suggestions = []
        suspected_mods = set()

        mods_dir = os.path.join(self.folder_input.text(), "mods")
        actual_mods = set()
        mod_jar_map = {}

        if os.path.exists(mods_dir):
            for f in os.listdir(mods_dir):
                if f.endswith(".jar"):
                    modname = f.lower().split("-")[0].replace(".jar", "")
                    actual_mods.add(modname)
                    mod_jar_map[modname] = os.path.join(mods_dir, f)

        lines = log.splitlines()

        for pattern, fix in CRASH_FIX_PATTERNS.items():
            if pattern in log:
                mod_hits = []
                if pattern == "ClassNotFoundException":
                    missing_classes = re.findall(r'ClassNotFoundException: ([\\w\\.]+)', log)
                    for cls in missing_classes:
                        class_path = cls.replace('.', '/')
                        for modname, jar_path in mod_jar_map.items():
                            try:
                                with zipfile.ZipFile(jar_path, 'r') as z:
                                    if any(class_path in entry for entry in z.namelist()):
                                        mod_hits.append(modname)
                                        break
                            except:
                                continue
                if not mod_hits:
                    for i, line in enumerate(lines):
                        if pattern in line:
                            context = "\n".join(lines[max(0, i - 10):i + 10])
                            matches = re.findall(r'at ((?:[a-zA-Z0-9_]+\\.)+[A-Za-z0-9_]+)', context)
                            for match in matches:
                                for part in match.split('.'):
                                    if part.lower() in actual_mods:
                                        mod_hits.append(part.lower())

                suspects = sorted(set(mod_hits))
                mods_str = ", ".join(suspects) if suspects else "unknown"
                report.append(f"❌ {pattern} caused by: {mods_str}\n→ {fix}")
                suggestions.append(fix)
                suspected_mods.update(suspects)

        fail_matches = re.findall(r'Failed to load mod: (\\w+)', log)
        for mod in fail_matches:
            if mod.lower() in actual_mods:
                suspected_mods.add(mod.lower())
                fix = conflict_engine.get_fix(mod.lower())
                if fix:
                    suggestions.append(f"→ {fix}")

        crash_lines = re.findall(r'java\\.[^\\n]+', log)
        ai_suggestions = []
        for line in crash_lines[:2]:
            suggestion = ai_engine.search_crash_issue(line.strip())
            if suggestion:
                ai_suggestions.append(f"🤖 AI Suggestion: {suggestion}")

        report.append("\n🔍 Suspected Mods:")
        if suspected_mods:
            for mod in sorted(suspected_mods):
                report.append(f"- {mod}")
        else:
            report.append("✓ No direct suspects found.")

        if suggestions:
            report.append("\n💡 Suggested Fixes:")
            for fix in set(suggestions):
                report.append(f"→ {fix}")

        if ai_suggestions:
            report.append("\n🧠 AI-Powered Suggestions:")
            report.extend(ai_suggestions)

        return "\n".join(report)

    def setup_mods_tab(self):
        layout = QVBoxLayout()
        scan_mods_btn = QPushButton("Check Mod Info")
        scan_mods_btn.clicked.connect(self.scan_mods)
        self.mod_output = QTextEdit()
        self.mod_output.setReadOnly(True)
        self.mod_output.setStyleSheet("background-color: #111; color: #0f0; font-family: Consolas;")
        layout.addWidget(scan_mods_btn)
        layout.addWidget(self.mod_output)
        self.mods_tab.setLayout(layout)

    def update_mod_output(self, text):
        self.mod_output.setText(text)

    def scan_mods(self):
        self.mod_output.setText("⏳ Scanning mods...")
        thread = threading.Thread(target=self._scan_mods_thread)
        thread.start()

    def _scan_mods_thread(self):
        try:
            mods_path = os.path.join(self.folder_input.text(), "mods")
            if not os.path.exists(mods_path):
                self.mod_scan_result.emit("❌ mods folder not found!")
                return

            results = []
            for modfile in os.listdir(mods_path):
                if not modfile.endswith(".jar"):
                    continue
                mod_name = modfile.lower().split("-")[0].replace(".jar", "")
                fix = conflict_engine.get_fix(mod_name)
                if fix:
                    results.append(f"{mod_name} ⚠️ {fix}")
                else:
                    results.append(f"{mod_name} ✅ No conflict found")

            self.mod_scan_result.emit("📦 Mod Compatibility Check:\n" + "\n".join(results))
        except Exception as e:
            self.mod_scan_result.emit(f"❌ Error scanning mods:\n{str(e)}\n{traceback.format_exc()}")

# --- App Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CrashDetector()
    window.show()
    sys.exit(app.exec_())
