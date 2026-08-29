import os
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import launcher

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DevModeApp(ctk.CTk):
    def __init__(self, autorun=False):
        super().__init__()

        self.title("Dev Mode Workflow Launcher")
        self.geometry("820x720")
        self.minsize(750, 650)
        
        # Load configuration
        self.config_data = launcher.load_config()
        
        # UI Header
        self.create_header()
        
        # Main scrollable content
        self.create_body()
        
        # Footer / Log console
        self.create_footer()
        
        # Handle autorun flag if passed
        if autorun or "--autorun" in sys.argv:
            self.after(500, self.on_launch_all)

    def create_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="#13141f", corner_radius=12)
        header_frame.pack(fill="x", padx=16, pady=(16, 8))
        
        # Title section
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=16, pady=12)
        
        title_label = ctk.CTkLabel(
            title_box, 
            text="🚀 Dev Mode Workflow Launcher", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w")
        
        sub_label = ctk.CTkLabel(
            title_box, 
            text="Launch your workspace apps & AI tabs in Brave with a single click", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#a0a5c0"
        )
        sub_label.pack(anchor="w")

        # Brave Status Badge
        brave_path = self.config_data.get("brave_path") or launcher.find_brave_browser()
        brave_status = "✓ Brave Browser Connected" if (brave_path and os.path.exists(brave_path)) else "⚠️ Brave Not Found"
        badge_color = "#2ef09b" if "✓" in brave_status else "#ff9f43"

        badge = ctk.CTkLabel(
            header_frame,
            text=brave_status,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=badge_color,
            fg_color="#1a1d2e",
            corner_radius=8,
            padx=12,
            pady=6
        )
        badge.pack(side="right", padx=16, pady=12)

    def create_body(self):
        # Action Bar with Big Launch Button
        action_frame = ctk.CTkFrame(self, fg_color="#181a29", corner_radius=12)
        action_frame.pack(fill="x", padx=16, pady=8)

        self.launch_btn = ctk.CTkButton(
            action_frame,
            text="🚀 LAUNCH ALL WORKFLOW ITEMS NOW",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color="#6c5ce7",
            hover_color="#5b4bc4",
            height=50,
            corner_radius=10,
            command=self.on_launch_all
        )
        self.launch_btn.pack(fill="x", padx=16, pady=12)

        # Tab view or split cards for URLs and Apps
        content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=16, pady=8)

        # --- Section 1: Web URLs ---
        url_header = ctk.CTkLabel(
            content_frame, 
            text="🌐 Web Applications (Opens in Brave Browser)", 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#64ffda"
        )
        url_header.pack(anchor="w", pady=(8, 4))

        self.url_switches = []
        for index, item in enumerate(self.config_data.get("urls", [])):
            card = ctk.CTkFrame(content_frame, fg_color="#181a29", corner_radius=8)
            card.pack(fill="x", pady=4)

            switch_var = ctk.BooleanVar(value=item.get("enabled", True))
            switch = ctk.CTkSwitch(
                card, 
                text=f"{item['name']} ({item['url']})", 
                variable=switch_var,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                command=lambda i=index, v=switch_var: self.toggle_url(i, v)
            )
            switch.pack(side="left", padx=12, pady=10)
            self.url_switches.append((switch_var, item))

        # --- Section 2: Desktop Apps / Shortcuts ---
        app_header = ctk.CTkLabel(
            content_frame, 
            text="🖥️ Desktop Apps & Shortcuts", 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#00b4d8"
        )
        app_header.pack(anchor="w", pady=(16, 4))

        self.app_switches = []
        for index, item in enumerate(self.config_data.get("apps", [])):
            card = ctk.CTkFrame(content_frame, fg_color="#181a29", corner_radius=8)
            card.pack(fill="x", pady=4)

            switch_var = ctk.BooleanVar(value=item.get("enabled", True))
            path_display = item['path']
            if len(path_display) > 55:
                path_display = "..." + path_display[-52:]
                
            switch = ctk.CTkSwitch(
                card, 
                text=f"{item['name']}  ➜  {path_display}", 
                variable=switch_var,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                command=lambda i=index, v=switch_var: self.toggle_app(i, v)
            )
            switch.pack(side="left", padx=12, pady=10)
            self.app_switches.append((switch_var, item))

        # --- Quick Utility Buttons ---
        utils_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        utils_frame.pack(fill="x", pady=(16, 8))

        add_url_btn = ctk.CTkButton(
            utils_frame,
            text="+ Add URL",
            width=120,
            fg_color="#2b2d42",
            hover_color="#3d3f58",
            command=self.add_url_dialog
        )
        add_url_btn.pack(side="left", padx=(0, 8))

        add_app_btn = ctk.CTkButton(
            utils_frame,
            text="+ Add App / .lnk",
            width=140,
            fg_color="#2b2d42",
            hover_color="#3d3f58",
            command=self.add_app_dialog
        )
        add_app_btn.pack(side="left", padx=8)

        shortcut_btn = ctk.CTkButton(
            utils_frame,
            text="📌 Create Desktop Shortcut",
            width=180,
            fg_color="#00b4d8",
            hover_color="#0077b6",
            command=self.create_desktop_shortcut
        )
        shortcut_btn.pack(side="right", padx=0)

    def create_footer(self):
        footer_frame = ctk.CTkFrame(self, fg_color="#13141f", corner_radius=12)
        footer_frame.pack(fill="x", padx=16, pady=(4, 16))

        log_title = ctk.CTkLabel(
            footer_frame, 
            text="System Activity Log", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#8d99ae"
        )
        log_title.pack(anchor="w", padx=12, pady=(8, 2))

        self.log_textbox = ctk.CTkTextbox(
            footer_frame, 
            height=100, 
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0b0c10", 
            text_color="#64ffda"
        )
        self.log_textbox.pack(fill="x", padx=12, pady=(0, 8))
        self.log("System initialized. Ready to launch Dev Mode Workflow!")

    def log(self, message):
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")

    def toggle_url(self, index, var):
        self.config_data["urls"][index]["enabled"] = var.get()
        launcher.save_config(self.config_data)

    def toggle_app(self, index, var):
        self.config_data["apps"][index]["enabled"] = var.get()
        launcher.save_config(self.config_data)

    def on_launch_all(self):
        self.launch_btn.configure(state="disabled", text="⏳ LAUNCHING WORKFLOW...")
        self.log("\n--- Starting Launch Sequence ---")
        
        def run_in_thread():
            launcher.launch_workflow(self.config_data, log_callback=self.log_from_thread)
            self.after(0, lambda: self.launch_btn.configure(state="normal", text="🚀 LAUNCH ALL WORKFLOW ITEMS NOW"))

        threading.Thread(target=run_in_thread, daemon=True).start()

    def log_from_thread(self, message):
        self.after(0, lambda: self.log(message))

    def add_url_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter full URL (e.g. https://example.com):", title="Add New URL")
        url = dialog.get_input()
        if url:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            name = url.replace("https://", "").replace("http://", "").split("/")[0]
            self.config_data["urls"].append({"name": name, "url": url, "enabled": True})
            launcher.save_config(self.config_data)
            messagebox.showinfo("Success", f"Added {name}! Restart the app to see it in your checklist.")

    def add_app_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Select App Executable or Shortcut",
            filetypes=[("Shortcuts & Executables", "*.lnk;*.exe;*.bat;*.cmd"), ("All Files", "*.*")]
        )
        if file_path:
            name = Path(file_path).stem
            self.config_data["apps"].append({"name": name, "path": file_path, "enabled": True})
            launcher.save_config(self.config_data)
            messagebox.showinfo("Success", f"Added {name}! Restart the app to see it in your checklist.")

    def create_desktop_shortcut(self):
        try:
            import create_shortcut
            path = create_shortcut.make_desktop_shortcut()
            messagebox.showinfo("Shortcut Created", f"Desktop shortcut created successfully at:\n{path}")
            self.log(f"✓ Created Desktop Shortcut: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create shortcut: {e}")

if __name__ == "__main__":
    autorun = "--autorun" in sys.argv
    app = DevModeApp(autorun=autorun)
    app.mainloop()
