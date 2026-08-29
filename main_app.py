import os
import sys
import webview
import subprocess
from pathlib import Path
import launcher
import data_manager

class Api:
    def get_config(self):
        print("API Call: get_config")
        config = data_manager.load_config()
        # Resolve icon paths for frontend
        for item in config.get("items", []):
            icon_file = item.get("icon_file")
            if icon_file:
                icon_full_path = data_manager.ICONS_DIR / icon_file
                if icon_full_path.exists():
                    item["icon_src"] = icon_full_path.as_uri()
                else:
                    item["icon_src"] = None
        return config

    def launch_all(self):
        print("API Call: launch_all")
        config = data_manager.load_config()
        launcher.launch_workflow(config)
        return {"status": "success"}

    def launch_url(self, url):
        print(f"API Call: launch_url: {url}")
        brave_path = launcher.find_brave_browser()
        if brave_path and os.path.exists(brave_path):
            subprocess.Popen([brave_path, url])
        else:
            import webbrowser
            webbrowser.open(url)
        return {"status": "success"}

    def launch_app(self, path):
        print(f"API Call: launch_app: {path}")
        if os.path.exists(path):
            try:
                os.startfile(path)
                return {"status": "success"}
            except Exception:
                subprocess.Popen(['cmd', '/c', 'start', '', path], shell=True)
                return {"status": "success"}
        return {"status": "error", "message": "Shortcut path not found"}

    def add_website(self, name, url):
        print(f"API Call: add_website: {name} -> {url}")
        new_item = data_manager.add_new_website(name, url)
        icon_file = new_item.get("icon_file")
        if icon_file:
            icon_full_path = data_manager.ICONS_DIR / icon_file
            if icon_full_path.exists():
                new_item["icon_src"] = icon_full_path.as_uri()
        return new_item

    def add_app(self, name, file_path):
        print(f"API Call: add_app: {name} -> {file_path}")
        new_item = data_manager.add_new_app(name, file_path)
        icon_file = new_item.get("icon_file")
        if icon_file:
            icon_full_path = data_manager.ICONS_DIR / icon_file
            if icon_full_path.exists():
                new_item["icon_src"] = icon_full_path.as_uri()
        return new_item

    def delete_item(self, item_id):
        print(f"API Call: delete_item: {item_id}")
        data_manager.delete_item(item_id)
        return {"status": "success"}

    def toggle_item(self, item_id, enabled):
        config = data_manager.load_config()
        for item in config.get("items", []):
            if item.get("id") == item_id:
                item["enabled"] = enabled
                break
        data_manager.save_config(config)
        return {"status": "success"}

    def pick_app_file(self):
        print("API Call: pick_app_file")
        file_types = ('Shortcuts & Executables (*.lnk;*.exe;*.bat;*.cmd)', 'All files (*.*)')
        try:
            result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
            if result and len(result) > 0:
                return result[0]
        except Exception as e:
            print(f"File dialog error: {e}")
        return None

def main():
    data_manager.init_data_dir()
    landing_dir = Path(__file__).parent.resolve() / "landing"
    html_file = landing_dir / "index.html"

    api = Api()

    # Check for --autorun argument
    if "--autorun" in sys.argv or "-a" in sys.argv:
        api.launch_all()

    window = webview.create_window(
        title="Dev Mode Workflow Launcher",
        url=html_file.as_uri(),
        js_api=api,
        width=1180,
        height=860,
        resizable=True,
        background_color="#000000"
    )
    
    # Enable DevTools debug mode for live right-click -> Inspect Element
    webview.start(debug=True)

if __name__ == "__main__":
    main()
