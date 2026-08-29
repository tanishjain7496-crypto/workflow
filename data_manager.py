import os
import sys
import json
import urllib.parse
import urllib.request
import subprocess
import hashlib
from pathlib import Path

# Dedicated data folder
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
ICONS_DIR = DATA_DIR / "icons"
CONFIG_FILE = DATA_DIR / "config.json"

# Default items required by user
DEFAULT_ITEMS = [
    {
        "id": "gemini",
        "name": "Gemini AI",
        "type": "urls",
        "url": "https://gemini.google.com/app?hl=en-IN",
        "sub": "gemini.google.com",
        "icon_type": "google",
        "icon_file": "gemini.png",
        "tag": "Brave Tab",
        "enabled": True
    },
    {
        "id": "chatgpt",
        "name": "ChatGPT",
        "type": "urls",
        "url": "https://chatgpt.com",
        "sub": "chatgpt.com",
        "icon_type": "chatgpt",
        "icon_file": "chatgpt.png",
        "tag": "Brave Tab",
        "enabled": True
    },
    {
        "id": "claude",
        "name": "Claude AI",
        "type": "urls",
        "url": "https://claude.com",
        "sub": "claude.com",
        "icon_type": "claude",
        "icon_file": "claude.png",
        "tag": "Brave Tab",
        "enabled": True
    },
    {
        "id": "perplexity",
        "name": "Perplexity AI",
        "type": "urls",
        "url": "https://www.perplexity.ai/",
        "sub": "perplexity.ai",
        "icon_type": "perplexity",
        "icon_file": "perplexity.png",
        "tag": "Brave Tab",
        "enabled": True
    },
    {
        "id": "youtube",
        "name": "YouTube App",
        "type": "apps",
        "path": r"C:\Users\Tanis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Chrome Apps\YouTube.lnk",
        "sub": "Chrome Apps / YouTube.lnk",
        "icon_file": "youtube.png",
        "tag": "Desktop App",
        "enabled": True
    },
    {
        "id": "antigravity_ide",
        "name": "Antigravity IDE",
        "type": "apps",
        "path": r"C:\Users\Tanis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Antigravity IDE.exe.lnk",
        "sub": "Antigravity IDE.exe.lnk",
        "icon_file": "antigravity_ide.png",
        "tag": "Desktop App",
        "enabled": True
    },
    {
        "id": "habit_tracker",
        "name": "Habit Tracker",
        "type": "apps",
        "path": r"C:\Users\Tanis\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Habit Tracker.lnk",
        "sub": "Habit Tracker.lnk",
        "icon_file": "habit_tracker.png",
        "tag": "Desktop App",
        "enabled": True
    }
]

def init_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        save_config({"brave_path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", "items": DEFAULT_ITEMS})

def load_config():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        init_data_dir()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return {"brave_path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", "items": DEFAULT_ITEMS}

def save_config(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def fetch_favicon(url, target_filename):
    """Downloads favicon for a URL and saves to data/icons directory"""
    init_data_dir()
    target_path = ICONS_DIR / target_filename
    if target_path.exists():
        return f"data/icons/{target_filename}"

    domain = urllib.parse.urlparse(url).netloc or url.replace("https://", "").replace("http://", "").split("/")[0]
    
    sources = [
        f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
        f"https://icon.horse/icon/{domain}"
    ]

    for favicon_url in sources:
        try:
            req = urllib.request.Request(
                favicon_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=5) as response, open(target_path, "wb") as f:
                f.write(response.read())
            print(f"✓ Downloaded favicon for {domain} -> {target_filename}")
            return f"data/icons/{target_filename}"
        except Exception as e:
            print(f"Favicon fetch failed from {favicon_url}: {e}")

    return None

def extract_windows_icon(file_path, target_filename):
    """Extracts Windows executable or shortcut icon using PowerShell script"""
    init_data_dir()
    target_path = ICONS_DIR / target_filename
    if target_path.exists():
        return f"data/icons/{target_filename}"

    if not os.path.exists(file_path):
        return None

    # PowerShell inline script to extract icon using System.Drawing
    ps_cmd = f"""
    Add-Type -AssemblyName System.Drawing
    $filePath = '{file_path}'
    $outPath = '{str(target_path).replace('\\', '/')}'
    try {{
        if ($filePath.EndsWith('.lnk')) {{
            $sh = New-Object -ComObject WScript.Shell
            $target = $sh.CreateShortcut($filePath).TargetPath
            if ([string]::IsNullOrEmpty($target) -or -not (Test-Path $target)) {{ $target = $filePath }}
            $filePath = $target
        }}
        $icon = [System.Drawing.Icon]::ExtractAssociatedIcon($filePath)
        if ($icon) {{
            $bmp = $icon.ToBitmap()
            $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
            $bmp.Dispose()
            $icon.Dispose()
            Write-Output 'OK'
        }}
    }} catch {{
        Write-Output $_.Exception.Message
    }}
    """
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True, timeout=8)
        if "OK" in res.stdout and target_path.exists():
            print(f"✓ Extracted native icon for {file_path} -> {target_filename}")
            return f"data/icons/{target_filename}"
    except Exception as e:
        print(f"Error extracting icon for {file_path}: {e}")

    return None

def ensure_favicon(url, icon_file):
    if not (ICONS_DIR / icon_file).exists():
        fetch_favicon(url, icon_file)

def ensure_app_icon(file_path, icon_file):
    if not (ICONS_DIR / icon_file).exists():
        extract_windows_icon(file_path, icon_file)

def add_new_website(name, url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    domain = urllib.parse.urlparse(url).netloc or url
    item_id = "site_" + hashlib.md5(url.encode()).hexdigest()[:8]
    icon_filename = f"{item_id}.png"

    # Fetch favicon
    fetch_favicon(url, icon_filename)

    new_item = {
        "id": item_id,
        "name": name if name else domain,
        "type": "urls",
        "url": url,
        "sub": domain,
        "icon_file": icon_filename,
        "tag": "Brave Tab",
        "enabled": True
    }

    config = load_config()
    config["items"].append(new_item)
    save_config(config)
    return new_item

def add_new_app(name, file_path):
    item_id = "app_" + hashlib.md5(file_path.encode()).hexdigest()[:8]
    icon_filename = f"{item_id}.png"

    # Extract icon
    extract_windows_icon(file_path, icon_filename)

    sub_display = Path(file_path).name
    new_item = {
        "id": item_id,
        "name": name if name else Path(file_path).stem,
        "type": "apps",
        "path": file_path,
        "sub": sub_display,
        "icon_file": icon_filename,
        "tag": "Desktop App",
        "enabled": True
    }

    config = load_config()
    config["items"].append(new_item)
    save_config(config)
    return new_item

def delete_item(item_id):
    config = load_config()
    config["items"] = [item for item in config.get("items", []) if item.get("id") != item_id]
    save_config(config)
    return True
