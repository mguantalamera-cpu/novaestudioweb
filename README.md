# SecurePatch Desktop

Desktop SAST + auto-fix tool for local projects. Offline-first by default.

## Features
- Static analysis for Python and JS/TS
- Safe auto-fix for a small, high-confidence set of rules
- Unified diff preview and reversible apply with backups
- Reports in Markdown, HTML, JSON
- Plugin system for additional rules and fixers

## Install
- Python 3.12+
- `pip install -r requirements.txt`

## Run (development)
- `python -m app.main`

## Tests
- `pytest`

## Build (Windows)
- Install PyInstaller: `pip install pyinstaller`
- Build: `pyinstaller --noconfirm --clean --name SecurePatch app/main.py`

## Optional installer (Inno Setup)
- Create an Inno Setup script pointing to `dist/SecurePatch/SecurePatch.exe`.

## Notes
- The app never sends code off the machine by default.
- External tools are optional and only used if installed locally.
