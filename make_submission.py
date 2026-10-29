"""
Make a clean .zip of this project to submit or share.

Usage (from the project folder):
    python make_submission.py

It leaves out things that should never be shared:
  - .env            your secret API key
  - db.sqlite3      your database (your account, password hash, and events)
  - virtual environments (venv/, .venv/, or any folder with pyvenv.cfg)
  - __pycache__/    files Python generates automatically
  - .git/, old .zip files, and editor clutter

The zip is saved next to manage.py as syllabus-calendar-submission.zip.
"""

import zipfile
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parent
ZIP_NAME = "syllabus-calendar-submission.zip"

# Folders that are skipped wherever they appear.
SKIP_FOLDERS = {"venv", ".venv", "env", "__pycache__", ".git", ".idea", ".vscode", "staticfiles"}

# Individual files that are skipped.
SKIP_FILES = {".env", "db.sqlite3", ".DS_Store", "Thumbs.db"}

# File endings that are skipped.
SKIP_ENDINGS = (".pyc", ".zip", ".log")


def is_virtual_environment(folder):
    """Every virtual environment contains a pyvenv.cfg file, whatever it's named."""
    return (folder / "pyvenv.cfg").exists()


def should_skip_folder(folder):
    return folder.name in SKIP_FOLDERS or is_virtual_environment(folder)


def should_skip_file(file):
    return file.name in SKIP_FILES or file.name.endswith(SKIP_ENDINGS)


def collect_files(folder):
    """Return every file in folder (and its subfolders) that should be included."""
    included = []
    for item in sorted(folder.iterdir()):
        if item.is_dir():
            if not should_skip_folder(item):
                included.extend(collect_files(item))  # look inside this folder too
        elif not should_skip_file(item):
            included.append(item)
    return included


def main():
    zip_path = PROJECT_FOLDER / ZIP_NAME
    files = collect_files(PROJECT_FOLDER)

    # Everything goes inside one top-level folder in the zip, so unzipping
    # it creates "syllabus-calendar/" instead of scattering files around.
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            name_in_zip = Path("syllabus-calendar") / file.relative_to(PROJECT_FOLDER)
            archive.write(file, name_in_zip)

    # Double-check that no secret file slipped in.
    with zipfile.ZipFile(zip_path) as archive:
        names = [Path(name).name for name in archive.namelist()]
    for secret in (".env", "db.sqlite3"):
        if secret in names:
            zip_path.unlink()
            raise SystemExit(f"Stopped: {secret} ended up in the zip, so it was deleted.")

    size_kb = zip_path.stat().st_size / 1024
    print(f"Created {ZIP_NAME} ({len(files)} files, {size_kb:.0f} KB).")
    print("Left out: .env (your API key), db.sqlite3 (your data), virtual environments, caches.")


if __name__ == "__main__":
    main()
