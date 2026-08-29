import os
import sys
import subprocess
import webbrowser
import time
import data_manager

def find_brave_browser():
    possible_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def safe_log(log_callback, message):
    """Safely invokes log_callback without crashing on Windows console encoding errors"""
    try:
        if log_callback:
            log_callback(message)
    except Exception:
        try:
            # Fallback to ASCII encoding
            safe_msg = message.encode('ascii', errors='replace').decode('ascii')
            print(safe_msg)
        except Exception:
            pass

def launch_workflow(config=None, log_callback=print):
    if config is None:
        config = data_manager.load_config()
    
    items = config.get("items", [])
    
    # 1. Launch Brave URLs
    enabled_urls = [item["url"] for item in items if item.get("type") == "urls" and item.get("enabled", True) and item.get("url")]
    if enabled_urls:
        brave_path = config.get("brave_path") or find_brave_browser()
        if brave_path and os.path.exists(brave_path):
            safe_log(log_callback, f"Opening {len(enabled_urls)} URLs in Brave Browser...")
            try:
                subprocess.Popen([brave_path] + enabled_urls)
                safe_log(log_callback, "[OK] Brave Browser launched with all tabs successfully!")
            except Exception as e:
                safe_log(log_callback, f"[ERROR] Failed to launch Brave executable: {e}. Opening in default browser...")
                for url in enabled_urls:
                    try:
                        webbrowser.open(url)
                    except Exception:
                        pass
        else:
            safe_log(log_callback, "[WARN] Brave Browser not found. Opening with default browser...")
            for url in enabled_urls:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass

    # 2. Launch Desktop App / Shortcut Files
    enabled_apps = [item for item in items if item.get("type") == "apps" and item.get("enabled", True) and item.get("path")]
    delay = config.get("delay_between_apps", 0.5)
    
    safe_log(log_callback, f"Launching {len(enabled_apps)} desktop apps...")

    for app in enabled_apps:
        app_name = app.get("name", "App")
        app_path = app.get("path", "")
        
        if not app_path or not os.path.exists(app_path):
            safe_log(log_callback, f"[WARN] Shortcut path not found: {app_path}")
            continue
            
        safe_log(log_callback, f"Launching {app_name} -> {app_path}...")
        try:
            os.startfile(app_path)
            safe_log(log_callback, f"[OK] {app_name} launched successfully!")
        except Exception as e:
            try:
                subprocess.Popen(['cmd', '/c', 'start', '', app_path], shell=True)
                safe_log(log_callback, f"[OK] {app_name} launched via cmd!")
            except Exception as ex:
                safe_log(log_callback, f"[ERROR] Could not launch {app_name}: {ex}")
                
        time.sleep(delay)

    safe_log(log_callback, "[OK] All requested items launched successfully!")

if __name__ == "__main__":
    print("Executing Dev Mode Workflow Launcher...")
    config = data_manager.load_config()
    launch_workflow(config)
