import os
import sys
import subprocess
from pathlib import Path

def make_desktop_shortcut():
    desktop_dir = os.path.expanduser("~/Desktop")
    if not os.path.exists(desktop_dir):
        desktop_dir = os.path.join(os.environ['USERPROFILE'], 'Desktop')

    shortcut_path = os.path.join(desktop_dir, "Dev Mode Workflow.lnk")
    
    target_dir = str(Path(__file__).parent.resolve())
    main_app_script = os.path.join(target_dir, "main_app.py")
    
    pythonw_exe = os.path.join(sys.prefix, "pythonw.exe")
    if not os.path.exists(pythonw_exe):
        pythonw_exe = "pythonw.exe"
    
    ps_script = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
    $Shortcut.TargetPath = "{pythonw_exe}"
    $Shortcut.Arguments = '"{main_app_script}"'
    $Shortcut.WorkingDirectory = "{target_dir}"
    $Shortcut.Description = "Launch Dev Mode AI links and shortcuts in Brave"
    $Shortcut.Save()
    """
    
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
    subprocess.run(cmd, check=True)
    return shortcut_path

if __name__ == "__main__":
    path = make_desktop_shortcut()
    print(f"Created desktop shortcut using pythonw at: {path}")
