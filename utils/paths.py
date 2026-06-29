import os, sys
from pathlib import Path

def get_resource_path(relative_path):
    # Resolve assets from the bundled app or from the source tree during development.
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).resolve().parent

        if not (base_path / "assets").exists():
            if (base_path.parent / "assets").exists():
                base_path = base_path.parent

    full_path = base_path / relative_path
    return str(full_path)


def get_app_data_path(filename):
    # Store mutable user data outside the install directory.
    app_name = "System Breach Protocol"

    if sys.platform == "win32":
        base_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    else:
        base_dir = os.path.expanduser("~")

    dest_dir = Path(base_dir) / app_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    return str(dest_dir / filename)
