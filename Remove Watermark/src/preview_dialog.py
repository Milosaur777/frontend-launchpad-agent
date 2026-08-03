"""Preview dialog — before/after comparison for a single image."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
import threading
import tempfile

from config import (
    ACCENT, ACCENT_DIM, BG, BORDER, BORDER_LIGHT, FONT_FAMILY, FONT_SIZE, FONT_SIZE_LG,
    SURFACE, SURFACE_HOVER, TEXT, TEXT_DIM, TEXT_MID,
)

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class PreviewDialog(tk.Toplevel):
    """Popup window showing a single image with optional before/after comparison."""

    def __init__(self, master, filepath: Path, process_fn=None, **kw):
        super().__init__(master, **kw)
        self._filepath = filepath
        self._process_fn = process_fn
        self._original_img = None
        self._processed_img = None
        self._showing_after = False

        self.title(f"Preview — {filepath.name}")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.transient(master)

        w, h = 900, 700
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(600, 500)

        self._build_ui()
        self._load_original()

    def _build_ui(self):
        # ── Header ─────────────────────────────────────
        header = tk.Frame(self, bg=SURFACE)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text=f"  ◉  {self._filepath.name}",
            bg=SURFACE,
            fg=TEXT,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            anchor=tk.W,
            pady=12,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)

        close_btn = tk.Button(
            header,
            text="✕",
            bg=SURFACE,
            fg=TEXT_DIM,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT,
            font=(FONT_FAMILY, FONT_SIZE_LG),
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.destroy,
        )
        close_btn.pack(side=tk.RIGHT, padx=12)

        # ── Image canvas ───────────────────────────────
        canvas_frame = tk.Frame(self, bg=BG)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self._canvas = tk.Canvas(canvas_frame, bg="#080808", highlightthickness=0)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        # ── Controls ───────────────────────────────────
        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(fill=tk.X, padx=12, pady=(0, 12))

        self._status_label = tk.Label(
            ctrl,
            text="Original",
            bg=BG,
            fg=TEXT_DIM,
            font=(FONT_FAMILY, FONT_SIZE),
            anchor=tk.W,
        )
        self._status_label.pack(side=tk.LEFT)

        self._process_btn = tk.Button(
            ctrl,
            text="▶  Process Preview",
            bg=ACCENT_DIM,
            fg=ACCENT,
            activebackground=ACCENT,
            activeforeground="#000000",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=14,
            pady=8,
            command=self._process_image,
        )
        self._process_btn.pack(side=tk.RIGHT)

        self._toggle_btn = tk.Button(
            ctrl,
            text="Show After →",
            bg=SURFACE,
            fg=TEXT_DIM,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT,
            font=(FONT_FAMILY, FONT_SIZE),
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=14,
            pady=8,
            command=self._toggle_view,
            state=tk.DISABLED,
        )
        self._toggle_btn.pack(side=tk.RIGHT, padx=(0, 10))

        self._canvas.bind("<Configure>", self._on_resize)

    def _load_original(self):
        if Image is None:
            self._canvas.create_text(
                250, 200,
                text="Pillow not installed.\nInstall with: pip install Pillow",
                fill=TEXT_DIM,
                font=(FONT_FAMILY, FONT_SIZE),
                justify=tk.CENTER,
            )
            return

        try:
            self._original_img = Image.open(self._filepath)
            self._display_image(self._original_img)
        except Exception as e:
            self._canvas.create_text(
                250, 200,
                text=f"Cannot load image:\n{e}",
                fill="#ef4444",
                font=(FONT_FAMILY, FONT_SIZE),
                justify=tk.CENTER,
            )

    def _display_image(self, img):
        if img is None:
            return

        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        if cw < 10 or ch < 10:
            cw, ch = 860, 560

        img_copy = img.copy()
        img_copy.thumbnail((cw - 24, ch - 24), Image.LANCZOS)

        self._photo = ImageTk.PhotoImage(img_copy)
        self._canvas.delete("all")
        self._canvas.create_image(
            cw // 2, ch // 2,
            image=self._photo,
            anchor=tk.CENTER,
        )

    def _on_resize(self, event):
        if self._showing_after and self._processed_img:
            self._display_image(self._processed_img)
        elif self._original_img:
            self._display_image(self._original_img)

    def _toggle_view(self):
        if self._showing_after:
            self._showing_after = False
            self._status_label.config(text="Original", fg=TEXT_DIM)
            self._toggle_btn.config(text="Show After →")
            if self._original_img:
                self._display_image(self._original_img)
        else:
            self._showing_after = True
            self._status_label.config(text="Processed", fg=ACCENT)
            self._toggle_btn.config(text="← Show Before")
            if self._processed_img:
                self._display_image(self._processed_img)

    def _process_image(self):
        if self._process_fn is None:
            return

        self._process_btn.config(text="Processing...", state=tk.DISABLED)
        self._status_label.config(text="Processing...", fg="#f59e0b")

        def _run():
            tmp_dir = Path(tempfile.mkdtemp(prefix="aiwc_preview_"))
            result = self._process_fn(self._filepath, tmp_dir)
            self.after(0, lambda: self._on_processed(result, tmp_dir))

        threading.Thread(target=_run, daemon=True).start()

    def _on_processed(self, result_path, tmp_dir):
        self._process_btn.config(text="▶  Process Preview", state=tk.NORMAL)

        if result_path is None or not result_path.exists():
            self._status_label.config(text="Processing failed", fg="#ef4444")
            return

        try:
            self._processed_img = Image.open(result_path)
            self._toggle_btn.config(state=tk.NORMAL)
            self._showing_after = True
            self._status_label.config(text="Processed", fg=ACCENT)
            self._toggle_btn.config(text="← Show Before")
            self._display_image(self._processed_img)
        except Exception:
            self._status_label.config(text="Failed to load result", fg="#ef4444")
