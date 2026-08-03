"""Main application window — big button, grid proportions, rounded cards."""

from __future__ import annotations

import os
import sys
import queue
import tkinter as tk
from pathlib import Path

from config import (
    ACCENT, BG, BORDER_VISIBLE, DEFAULT_HEIGHT, DEFAULT_WIDTH,
    MIN_HEIGHT, MIN_WIDTH, SURFACE, SURFACE_CARD, TEXT, TEXT_DIM,
    FONT_FAMILY, FONT_SIZE, FONT_SIZE_LG, FONT_SIZE_XL, ASSETS_DIR,
)
from gpu_detector import detect_gpu
from core import BatchEngine, BatchOptions, BatchState, scan_images
from widgets.sidebar import Sidebar
from widgets.file_list import FileList
from widgets.log_panel import LogPanel
from widgets.progress_bar import ProgressBar
from widgets.overwrite_dialog import OverwriteDialog
from preview_dialog import PreviewDialog

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._gpu_info = detect_gpu()
        self._engine = BatchEngine()
        self._poll_id: str | None = None

        self._setup_window()
        self._build_layout()
        self._bind_shortcuts()
        self._refresh_file_list()

    def _setup_window(self):
        self.root.title("AI Image Cleaner")
        self.root.configure(bg=BG)
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - DEFAULT_WIDTH) // 2
        y = (sh - DEFAULT_HEIGHT) // 2
        self.root.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}+{x}+{y}")

        try:
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, "assets", "icon.ico")
            else:
                icon_path = str(ASSETS_DIR / "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

    def _build_layout(self):
        # ── TOP BAR: BIG CLEAN IMAGES + PROGRESS ───────
        top_bar = tk.Frame(self.root, bg=SURFACE_CARD)
        top_bar.pack(fill=tk.X, padx=12, pady=12)

        # Left: CLEAN IMAGES — 2x BIGGER
        btn_frame = tk.Frame(top_bar, bg=SURFACE_CARD)
        btn_frame.pack(side=tk.LEFT, padx=(12, 20), pady=12)

        self._btn_photo = None
        if HAS_PIL:
            try:
                btn_path = ASSETS_DIR / "clean_button.avif"
                if btn_path.exists():
                    img = Image.open(btn_path)
                    target_h = 120  # 2x bigger
                    ratio = target_h / img.height
                    target_w = int(img.width * ratio)
                    img = img.resize((target_w, target_h), Image.LANCZOS)
                    self._btn_photo = ImageTk.PhotoImage(img)
            except Exception:
                pass

        if self._btn_photo:
            self._start_btn = tk.Label(
                btn_frame, image=self._btn_photo, bg=SURFACE_CARD, cursor="hand2",
            )
            self._start_btn.pack()
            self._start_btn.bind("<Button-1>", lambda e: self._on_start())
        else:
            self._start_btn = tk.Button(
                btn_frame, text="🧹  CLEAN IMAGES", bg=ACCENT, fg="#000000",
                activebackground="#44e0ab", activeforeground="#000000",
                font=(FONT_FAMILY, 24, "bold"), relief=tk.FLAT, bd=0,
                cursor="hand2", command=self._on_start, height=3, padx=40,
            )
            self._start_btn.pack()

        # Right: Progress bar
        self._progress = ProgressBar(top_bar)
        self._progress.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12)

        # ── MAIN CONTENT with GRID layout ──────────────
        content = tk.Frame(self.root, bg=BG)
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # Configure grid: sidebar=0, right=1
        content.columnconfigure(0, weight=0)  # sidebar fixed width
        content.columnconfigure(1, weight=1)  # right panel expands
        content.rowconfigure(0, weight=1)

        # ── Sidebar ────────────────────────────────────
        sidebar_outer = tk.Frame(
            content, bg=SURFACE_CARD,
            highlightbackground=BORDER_VISIBLE, highlightthickness=2, bd=0,
        )
        sidebar_outer.grid(row=0, column=0, sticky="ns", padx=(0, 12))

        self._sidebar = Sidebar(
            sidebar_outer, gpu_info=self._gpu_info,
            on_input_change=self._on_input_change,
            on_output_change=self._on_output_change,
        )
        self._sidebar.pack(fill=tk.BOTH, expand=True)

        # ── Right panel with GRID ──────────────────────
        right = tk.Frame(content, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=4)  # file list: 4 parts
        right.rowconfigure(1, weight=1)  # log: 1 part

        # File list — TALLER
        file_frame = tk.Frame(
            right, bg=SURFACE_CARD,
            highlightbackground=BORDER_VISIBLE, highlightthickness=2, bd=0,
        )
        file_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        file_header = tk.Frame(file_frame, bg=SURFACE_CARD)
        file_header.pack(fill=tk.X, padx=16, pady=(8, 4))

        tk.Label(
            file_header, text="📁  FILE LIST", bg=SURFACE_CARD, fg=ACCENT,
            font=(FONT_FAMILY, FONT_SIZE, "bold"), anchor=tk.W,
        ).pack(side=tk.LEFT)

        self._file_list = FileList(file_frame, on_double_click=self._on_preview)
        self._file_list.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        # Log — expands vertically to match sidebar bottom
        log_frame = tk.Frame(
            right, bg=SURFACE_CARD,
            highlightbackground=BORDER_VISIBLE, highlightthickness=2, bd=0,
        )
        log_frame.grid(row=1, column=0, sticky="nsew")

        log_header = tk.Frame(log_frame, bg=SURFACE_CARD)
        log_header.pack(fill=tk.X, padx=16, pady=(6, 4))

        tk.Label(
            log_header, text="⌘  LOG CONSOLE", bg=SURFACE_CARD, fg=ACCENT,
            font=(FONT_FAMILY, FONT_SIZE, "bold"), anchor=tk.W,
        ).pack(side=tk.LEFT)

        self._log = LogPanel(log_frame)
        self._log.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

    def _bind_shortcuts(self):
        self.root.bind("<Return>", lambda e: self._on_start())
        self.root.bind("<Escape>", lambda e: self._on_cancel())

    def _on_input_change(self, path: str):
        self._refresh_file_list()

    def _on_output_change(self, path: str):
        pass

    def _refresh_file_list(self):
        input_dir = Path(self._sidebar.input_var.get())
        if input_dir.is_dir():
            files = scan_images(input_dir)
            self._file_list.set_files(files)
        else:
            self._file_list.set_files([])

    def _on_start(self):
        if self._engine.state == BatchState.RUNNING:
            return

        selected = self._file_list.get_selected_files()
        if not selected:
            self._log.append("[!] No files selected")
            return

        input_dir = Path(self._sidebar.input_var.get())
        output_dir = Path(self._sidebar.output_var.get())
        output_dir.mkdir(parents=True, exist_ok=True)

        options = BatchOptions(
            input_dir=input_dir, output_dir=output_dir,
            visible=self._sidebar.visible_var.get(),
            metadata=self._sidebar.metadata_var.get(),
            invisible=self._sidebar.invisible_var.get(),
            gpu_available=self._gpu_info["available"],
            gpu_type=self._gpu_info["type"],
            avif=self._sidebar.avif_var.get(),
            avif_quality=self._sidebar.avif_quality.get(),
            selected_files=selected,
        )

        self._progress.reset()
        self._log.clear()
        self._engine.start(options)
        self._start_polling()

    def _on_cancel(self):
        if self._engine.state == BatchState.RUNNING:
            self._engine.cancel()
            self._log.append("[!] Cancelling...")

    def _on_preview(self, filepath: Path):
        PreviewDialog(self.root, filepath, process_fn=self._engine.process_single_preview)

    def _start_polling(self):
        if self._poll_id is not None:
            return
        self._poll_queue()

    def _poll_queue(self):
        while not self._engine.log_queue.empty():
            try: self._log.append(self._engine.log_queue.get_nowait())
            except queue.Empty: break

        while not self._engine.progress_queue.empty():
            try:
                current, total = self._engine.progress_queue.get_nowait()
                self._progress.set_progress(current, total)
            except queue.Empty: break

        while not self._engine.file_done_queue.empty():
            try: self._engine.file_done_queue.get_nowait()
            except queue.Empty: break

        if self._engine.overwrite_pending:
            filename = self._engine.overwrite_filename
            self._engine.overwrite_pending = False
            self.root.after(10, lambda fn=filename: self._show_overwrite_dialog(fn))
            self._poll_id = self.root.after(200, self._poll_queue)
            return

        if self._engine.state in (BatchState.DONE, BatchState.CANCELLED):
            self._poll_id = None
            self._progress.set_progress(1, 1)
            return

        self._poll_id = self.root.after(100, self._poll_queue)

    def _show_overwrite_dialog(self, filename: str):
        dialog = OverwriteDialog(self.root, filename)
        self._engine.respond_overwrite(dialog.result or "cancel")
