import os
import platform
import webbrowser

def open_file_in_browser(path: str):
    abs_path = os.path.abspath(path)
    if platform.system() == "Darwin":  # macOS
        os.system(f"open '{abs_path}'")
    elif platform.system() == "Windows":
        os.startfile(abs_path)
    else:  # Linux
        webbrowser.open("file://" + abs_path, new=2)

    print("已打开:", abs_path)
