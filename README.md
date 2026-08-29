# Dev Mode Workflow Launcher

A custom high-performance workflow launcher for Windows that opens all your essential AI web tools in **Brave Browser** and launches your local desktop app shortcuts with **one single click**.

---

## 🎯 Configured Launcher Items

### 🌐 Web Applications (Opened in Brave Browser)
1. **Gemini AI**: `https://gemini.google.com/app?hl=en-IN`
2. **ChatGPT**: `https://chatgpt.com`
3. **Claude AI**: `https://claude.com`
4. **Perplexity AI**: `https://www.perplexity.ai/`

### 🖥️ Desktop Applications & Shortcuts
1. **YouTube App**: `C:\Users\Tanis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Chrome Apps\YouTube.lnk`
2. **Antigravity IDE**: `C:\Users\Tanis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Antigravity IDE.exe.lnk`
3. **Habit Tracker**: `C:\Users\Tanis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Habit Tracker.lnk`

---

## 🚀 How to Run

### Option 1: Desktop Shortcut (Instant 1-Click Launch)
Double-click the **Dev Mode Workflow** shortcut on your Desktop:
`C:\Users\Tanis\Desktop\Dev Mode Workflow.lnk`

### Option 2: Modern Dark-Mode GUI App
Run the graphical interface to toggle individual items or add new links/apps:
```powershell
python app.py
```
Or launch the standalone executable:
`d:\dev mode workflow\dist\DevModeWorkflow\DevModeWorkflow.exe`

### Option 3: Silent Background Script
Double-click `launch_all.vbs` or `launch_all.bat` in `d:\dev mode workflow\`.

---

## 🛠️ Configuration & Customization

All configurations are saved in `d:\dev mode workflow\config.json`. You can edit this file manually or use the `+ Add URL` and `+ Add App` buttons inside the GUI application.
