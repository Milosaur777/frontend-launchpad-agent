"""File list widget — scrollable list with visible, working checkboxes."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path

from config import (
    ACCENT, ACCENT_DIM, BG, BORDER_LIGHT, FONT_FAMILY,
    FONT_SIZE, FONT_SIZE_SM, SURFACE, SURFACE_HOVER, SURFACE_LIGHT,
    SURFACE_CARD, TEXT, TEXT_DIM, TEXT_MID,
)

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class FileList(tk.Frame):
    """Scrollable list showing image files with visible checkboxes."""

    THUMB_SIZE = (48, 48)

    def __init__(self, master, on_double_click=None, **kw):
        super().__init__(master, bg=SURFACE_CARD, **kw)
        self._on_double_click = on_double_click
        self._files: list[Path] = []
        self._rows: list[dict] = []

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=SURFACE_CARD)
        container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._canvas = tk.Canvas(container, bg=SURFACE_CARD, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=self._canvas.yview,
                                  bg=SURFACE, troughcolor=SURFACE_CARD,
                                  activebackground=ACCENT_DIM, width=10)
        self._inner = tk.Frame(self._canvas, bg=SURFACE_CARD)

        self._inner.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas_window = self._canvas.create_window((0, 0), window=self._inner, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=scrollbar.set)

        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._canvas_window, width=e.width))
        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def set_files(self, files: list[Path]):
        """Replace the file list with thumbnails and checkboxes."""
        for w in self._inner.winfo_children():
            w.destroy()
        self._files = files
        self._rows.clear()

        if not files:
            f = tk.Frame(self._inner, bg=SURFACE_CARD)
            f.pack(pady=40)
            tk.Label(f, text="📂", bg=SURFACE_CARD, fg=TEXT_DIM,
                     font=(FONT_FAMILY, 32)).pack()
            tk.Label(f, text="No images found", bg=SURFACE_CARD, fg=TEXT_DIM,
                     font=(FONT_FAMILY, FONT_SIZE)).pack(pady=(8, 0))
            tk.Label(f, text="Select a folder with images", bg=SURFACE_CARD, fg=TEXT_DIM,
                     font=(FONT_FAMILY, FONT_SIZE_SM)).pack(pady=(4, 0))
            return

        # Header row
        header = tk.Frame(self._inner, bg=SURFACE_CARD)
        header.pack(fill=tk.X, padx=8, pady=(4, 8))

        self._count_label = tk.Label(header, text=f"{len(files)} file(s) found",
                                     bg=SURFACE_CARD, fg=TEXT_DIM,
                                     font=(FONT_FAMILY, FONT_SIZE_SM), anchor=tk.W)
        self._count_label.pack(side=tk.LEFT)

        btn_frame = tk.Frame(header, bg=SURFACE_CARD)
        btn_frame.pack(side=tk.RIGHT)

        tk.Button(btn_frame, text="☑ Select All", bg=SURFACE, fg=ACCENT,
                  activebackground=SURFACE_HOVER, activeforeground=ACCENT,
                  font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
                  relief=tk.FLAT, bd=0, cursor="hand2",
                  command=lambda: self._select_all(True),
                  padx=10, pady=4).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="☐ None", bg=SURFACE, fg=TEXT_DIM,
                  activebackground=SURFACE_HOVER, activeforeground=TEXT,
                  font=(FONT_FAMILY, FONT_SIZE_SM),
                  relief=tk.FLAT, bd=0, cursor="hand2",
                  command=lambda: self._select_all(False),
                  padx=10, pady=4).pack(side=tk.LEFT, padx=2)

        for i, fp in enumerate(files):
            self._add_row(i, fp)

    def _add_row(self, index: int, filepath: Path):
        var = tk.BooleanVar(value=True)
        bg = SURFACE if index % 2 == 0 else SURFACE_CARD

        row = tk.Frame(self._inner, bg=bg, cursor="hand2")
        row.pack(fill=tk.X, padx=4, pady=1)

        # BIG visible checkbox
        cb = tk.Checkbutton(
            row, variable=var,
            bg=bg,
            fg=ACCENT,
            selectcolor=SURFACE,
            selectimage="",
            activebackground=bg,
            activeforeground=ACCENT,
            relief=tk.FLAT,
            bd=0,
            width=3,
            height=1,
            font=(FONT_FAMILY, 16),
            anchor=tk.W,
        )
        cb.pack(side=tk.LEFT, padx=(8, 4), pady=4)

        # Thumbnail
        thumb_label = tk.Label(row, bg=bg, width=48, height=48)
        thumb_label.pack(side=tk.LEFT, padx=(0, 12), pady=4)

        if HAS_PIL:
            try:
                img = Image.open(filepath)
                img.thumbnail(self.THUMB_SIZE, Image.LANCZOS)
                bg_img = Image.new("RGB", self.THUMB_SIZE, (22, 22, 26))
                x = (self.THUMB_SIZE[0] - img.width) // 2
                y = (self.THUMB_SIZE[1] - img.height) // 2
                if img.mode in ("RGBA", "P"):
                    bg_img.paste(img.convert("RGB"), (x, y))
                else:
                    bg_img.paste(img, (x, y))
                photo = ImageTk.PhotoImage(bg_img)
                thumb_label._photo = photo
                thumb_label.config(image=photo)
            except Exception:
                pass

        # File name
        name_label = tk.Label(row, text=filepath.name, bg=bg, fg=TEXT,
                              font=(FONT_FAMILY, FONT_SIZE), anchor=tk.W)
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=4)

        # File size
        size = self._format_size(filepath.stat().st_size)
        size_label = tk.Label(row, text=size, bg=bg, fg=TEXT_DIM,
                              font=(FONT_FAMILY, FONT_SIZE_SM), anchor=tk.E)
        size_label.pack(side=tk.RIGHT, padx=(0, 16), pady=4)

        # Hover
        def on_enter(e):
            for w in (row, name_label, size_label, thumb_label):
                try: w.config(bg=SURFACE_HOVER)
                except: pass
            try: cb.config(bg=SURFACE_HOVER)
            except: pass

        def on_leave(e):
            for w in (row, name_label, size_label, thumb_label):
                try: w.config(bg=bg)
                except: pass
            try: cb.config(bg=bg)
            except: pass

        for w in (row, name_label, size_label, thumb_label, cb):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        # Click row → toggle checkbox
        def on_row_click(e, c=cb):
            if c.cget("state") != "disabled":
                c.toggle()

        row.bind("<Button-1>", on_row_click)
        name_label.bind("<Button-1>", on_row_click)
        thumb_label.bind("<Button-1>", on_row_click)

        # Double-click → preview
        def on_dbl(e, fp=filepath):
            if self._on_double_click:
                self._on_double_click(fp)

        for w in (name_label, thumb_label):
            w.bind("<Double-Button-1>", on_dbl)

        self._rows.append({"path": filepath, "var": var})

    def _select_all(self, selected: bool):
        for row in self._rows:
            row["var"].set(selected)

    def get_selected_files(self) -> list[Path]:
        return [row["path"] for row in self._rows if row["var"].get()]

    @staticmethod
    def _format_size(n: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"
