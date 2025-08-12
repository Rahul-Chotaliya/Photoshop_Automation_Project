# Photoshop_Automation_Project
Automate logo placement on apparel images using AI (MediaPipe + OpenCV) with optional Photoshop export.

## Quick start
1. Create a virtualenv and install requirements:
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt`
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. Put your Excel and assets in the input folders or use the GUI to browse.
3. Run the GUI:
   - `python -m gui.interface` (or `python3 -m gui.interface`)

## Notes
- Photoshop export is disabled by default (`enable_photoshop_export: false`). On Windows, set it to `true` in `config/settings.json` if Photoshop is installed and in PATH as `Photoshop`.
- PDF logo conversion tries `pdf2image` (Poppler) first; optionally set `poppler_path` in `config/settings.json`. If not available, it falls back to PyMuPDF.
- The tool places logos using human landmarks; if detection is unreliable, it falls back to heuristic positions.
