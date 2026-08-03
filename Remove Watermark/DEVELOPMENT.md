# AI Watermark Cleaner — Codebase Guide

## What is this?
Desktop app (Python/Tkinter) that removes AI watermarks, strips metadata, and converts images to AVIF. Bundled as standalone `.exe` via PyInstaller — no Python needed on target machine.

## Tech stack
- Python 3.10+ / Tkinter (GUI)
- OpenCV + Pillow (image processing)
- PyInstaller (EXE packaging)
- [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) (core engine)

## Architecture

```
main.py          → Entry point, PyInstaller-compatible path handling
app.py           → Main window, grid layout, event loop, polling
config.py        → All colors, fonts, paths, settings persistence
core.py          → Batch engine (threading), watermark removal, AVIF conversion
gpu_detector.py  → CUDA/MPS/nvidia-smi detection
preview_dialog.py→ Before/after popup for single images
```

### Widgets
```
widgets/sidebar.py        → Scrollable sidebar: folder pickers, options, GPU status
widgets/file_list.py      → Scrollable file list with thumbnails + checkboxes
widgets/log_panel.py      → Log console (Canvas-wrapped Text for no scrollbar arrows)
widgets/progress_bar.py   → Segmented progress indicator
widgets/overwrite_dialog.py → Modal: Overwrite / Add Number / Cancel
widgets/rounded_frame.py  → Canvas-based rounded corners (rarely used now)
```

### Assets
```
src/assets/icon.avif      → App icon (AVIF)
src/assets/icon.ico       → Windows icon
src/assets/clean_button.avif → CLEAN IMAGES button image
```

## How it works

1. User selects input/output folders
2. Options: visible watermarks, metadata, invisible watermarks, AVIF conversion
3. Click CLEAN IMAGES → `core.py` spawns background thread
4. Thread processes each image through the pipeline
5. Progress + logs pushed to UI via `queue.Queue`
6. Overwrite conflicts show modal dialog, thread blocks until user responds

## Key patterns

### Threading
```python
# core.py runs in background, communicates via queues
self.log_queue.put(f"[{ts()}] Processing {filename}...")
self.progress_queue.put((current, total))
```

### Grid layout (app.py)
```python
right.rowconfigure(0, weight=4)  # file list: 80%
right.rowconfigure(1, weight=1)  # log: 20%
```

### Sidebar scrolling
```python
# Hide scrollbar when content fits
if inner_h <= canvas_h:
    scrollbar.pack_forget()
```

## Tkinter gotchas (learned the hard way)

| Problem | Fix |
|---------|-----|
| 8-digit hex colors (`#33CC9950`) crash | Use 6-digit only (`#33CC99`) |
| `pack()` + `grid()` in same parent | Use one layout method per parent |
| Canvas expands to fill parent | Manually set canvas size via `<Configure>` |
| Text scrollbars show arrows on Windows | Wrap Text in Canvas widget |
| `overrideredirect(True)` kills resize | Use `overrideredirect(False)`, native resize works |

## Build

```bash
# Clean build
taskkill /F /IM "AI Image Cleaner.exe"
Remove-Item dist, build, src/__pycache__, src/widgets/__pycache__ -Recurse -Force

# Build
python -m PyInstaller "AI Image Cleaner.spec" --noconfirm --clean
```

Output: `dist/AI Image Cleaner.exe` (~30MB, standalone)

## Running locally

```bash
cd src && python main.py
```

## Dependencies

```
pip install -r requirements.txt
pip install "remove-ai-watermarks[gpu]"  # optional, for invisible watermarks
```

## Future ideas
- AI copy protection (frequency-domain watermarking)
- Drag & drop support
- Side-by-side before/after preview
- Multi-language support
