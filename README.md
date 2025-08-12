# Photoshop_Automation_Project
Automate logo placement on apparel images using AI (MediaPipe + OpenCV) with optional Photoshop export.

## Auto Decorate (OpenCV + MediaPipe)

Batch place logos from PDFs onto product images based on rows in an Excel file. Images are matched by supplier folder and filename template; logos are taken from the first page of PDF files. Placement is computed using MediaPipe pose landmarks for common decoration locations (left/right chest, center front, sleeves), with simple heuristics. Falls back to coordinates provided as text.

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r auto_decorate/requirements.txt
```

### Expected Excel Columns
- Supplier Part ID
- Supplier Color
- Decoration Code
- Decoration Location
- Location As per Word (optional; can be `x,y,width` or `%x,%y,%w`)
- Supplier Name
- Final Image Name

### Run

```bash
python -m auto_decorate.main \
  --excel-path "/absolute/path/to/input.xlsx" \
  --images-root "/absolute/path/to/images_root" \
  --logos-root "/absolute/path/to/logos_root" \
  --output-dir "/absolute/path/to/output"
```

Optional flags:
- `--image-filename-template` (default: `{Supplier Part ID}_{Supplier Color}`)
- `--logo-filename-template` (default: `{Decoration Code}`)
- `--logo-dpi` (default: `300`)

The script writes processed images to the output directory and a `report.csv` with per-row status.

### Notes
- Supported product image extensions: `.png`, `.jpg`, `.jpeg`.
- Logo must be a `.pdf`; the first page is rasterized with transparency if present.
- Placement heuristics may require tuning depending on your imagery. Update `auto_decorate/coordinates.py` ratios as needed.
- This project avoids automating proprietary software. The output is standard raster images (PNG/JPG). If you need PSDs, consider exporting later using lawful tools.
