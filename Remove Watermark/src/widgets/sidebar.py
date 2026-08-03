"""Sidebar widget — clean, reliable layout without Canvas hacks."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog

from config import (
    ACCENT, ACCENT_DIM, BG, BORDER, BORDER_LIGHT,
    BORDER_VISIBLE, FONT_FAMILY, FONT_SIZE, FONT_SIZE_SM, FONT_SIZE_LG,
    SURFACE, SURFACE_LIGHT, SURFACE_CARD, SURFACE_HOVER, TEXT, TEXT_DIM, TEXT_MID,
    WARNING, SIDEBAR_BG, SIDEBAR_WIDTH,
    get_last_input, get_last_output, set_last_input, set_last_output,
)


def _card(parent, **kw) -> tk.Frame:
    """Simple card with visible border."""
    return tk.Frame(parent, bg=SURFACE_CARD, highlightbackground=BORDER_LIGHT,
                    highlightthickness=1, bd=0, **kw)


def _mint_button(parent, text, command) -> tk.Button:
    """Mint-colored button."""
    return tk.Button(
        parent, text=text, bg=ACCENT_DIM, fg=ACCENT,
        activebackground=ACCENT, activeforeground="#000000",
        font=(FONT_FAMILY, FONT_SIZE, "bold"), relief=tk.FLAT,
        bd=0, cursor="hand2", command=command,
        padx=12, pady=6,
    )


class Sidebar(tk.Frame):
    """Scrollable sidebar with folder selectors, options, GPU status."""

    def __init__(self, master, gpu_info: dict, on_input_change=None, on_output_change=None, **kw):
        super().__init__(master, bg=SURFACE_CARD, **kw)
        self._on_input_change = on_input_change
        self._on_output_change = on_output_change
        self._gpu_info = gpu_info

        self.input_var = tk.StringVar(value=str(get_last_input()))
        self.output_var = tk.StringVar(value=str(get_last_output()))
        self.visible_var = tk.BooleanVar(value=True)
        self.metadata_var = tk.BooleanVar(value=True)
        self.invisible_var = tk.BooleanVar(value=gpu_info.get("available", False))
        self.avif_var = tk.BooleanVar(value=False)
        self.avif_quality = tk.IntVar(value=75)

        self._build_ui()
        self._update_avif_estimate()

    def _build_ui(self):
        # Scrollable canvas
        self._canvas = tk.Canvas(self, bg=SURFACE_CARD, highlightthickness=0)
        self._scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview,
                                        bg=SURFACE, troughcolor=SURFACE_CARD,
                                        activebackground=ACCENT_DIM, width=10)
        self._inner = tk.Frame(self._canvas, bg=SURFACE_CARD)

        self._inner.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas_window = self._canvas.create_window((0, 0), window=self._inner, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Resize inner frame to match canvas width
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

        self._build_content()

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)
        # Hide scrollbar if content fits
        self._canvas.update_idletasks()
        canvas_h = self._canvas.winfo_height()
        inner_h = self._inner.winfo_reqheight()
        if inner_h <= canvas_h:
            self._scrollbar.pack_forget()
        else:
            self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_mousewheel(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_content(self):
        p = self._inner
        px = 14  # horizontal padding

        # ── Title ──────────────────────────────────────
        tk.Label(p, text="AI IMAGE CLEANER", bg=SURFACE_CARD, fg=ACCENT,
                 font=(FONT_FAMILY, FONT_SIZE_LG, "bold")).pack(fill=tk.X, pady=(6, 2), padx=px)
        tk.Frame(p, bg=BORDER_LIGHT, height=1).pack(fill=tk.X, padx=px, pady=(0, 4))

        # ── Input folder ─────────────────────────────
        tk.Label(p, text="INPUT FOLDER", bg=SURFACE_CARD, fg=TEXT_MID,
                 font=(FONT_FAMILY, FONT_SIZE_SM, "bold")).pack(anchor=tk.W, padx=px, pady=(0, 3))

        card_in = _card(p)
        card_in.pack(fill=tk.X, padx=px, pady=(0, 4))

        _mint_button(card_in, "📁  Browse", self._pick_input).pack(fill=tk.X, padx=8, pady=(6, 2))

        self._input_label = tk.Label(
            card_in, text=self._short_path(self.input_var.get()),
            bg=SURFACE_CARD, fg=TEXT_DIM, font=(FONT_FAMILY, FONT_SIZE_SM),
            anchor=tk.W, wraplength=SIDEBAR_WIDTH - 56,
        )
        self._input_label.pack(fill=tk.X, padx=8, pady=(0, 6))

        # ── Output folder ──────────────────────────────
        tk.Label(p, text="OUTPUT FOLDER", bg=SURFACE_CARD, fg=TEXT_MID,
                 font=(FONT_FAMILY, FONT_SIZE_SM, "bold")).pack(anchor=tk.W, padx=px, pady=(0, 3))

        card_out = _card(p)
        card_out.pack(fill=tk.X, padx=px, pady=(0, 4))

        _mint_button(card_out, "📁  Browse", self._pick_output).pack(fill=tk.X, padx=8, pady=(6, 2))

        self._output_label = tk.Label(
            card_out, text=self._short_path(self.output_var.get()),
            bg=SURFACE_CARD, fg=TEXT_DIM, font=(FONT_FAMILY, FONT_SIZE_SM),
            anchor=tk.W, wraplength=SIDEBAR_WIDTH - 56,
        )
        self._output_label.pack(fill=tk.X, padx=8, pady=(0, 6))

        # ── Options ────────────────────────────────────
        tk.Label(p, text="CLEANING OPTIONS", bg=SURFACE_CARD, fg=TEXT_MID,
                 font=(FONT_FAMILY, FONT_SIZE_SM, "bold")).pack(anchor=tk.W, padx=px, pady=(0, 3))

        card_opts = _card(p)
        card_opts.pack(fill=tk.X, padx=px, pady=(0, 4))

        opts_inner = tk.Frame(card_opts, bg=SURFACE_CARD)
        opts_inner.pack(fill=tk.X, padx=8, pady=(6, 6))

        for label, var, desc in [
            ("✨ Visible watermarks", self.visible_var, "Gemini sparkle, Doubao, etc."),
            ("📝 AI metadata", self.metadata_var, "C2PA, EXIF, provenance data"),
        ]:
            f = tk.Frame(opts_inner, bg=SURFACE_CARD)
            f.pack(fill=tk.X, pady=1)
            tk.Checkbutton(f, text=label, variable=var, bg=SURFACE_CARD, fg=TEXT,
                           selectcolor=SURFACE, activebackground=SURFACE_CARD,
                           font=(FONT_FAMILY, FONT_SIZE), relief=tk.FLAT, bd=0).pack(anchor=tk.W)
            tk.Label(f, text=f"    {desc}", bg=SURFACE_CARD, fg=TEXT_DIM,
                     font=(FONT_FAMILY, FONT_SIZE_SM)).pack(anchor=tk.W)

        inv_state = tk.NORMAL if self._gpu_info["available"] else tk.DISABLED
        gpu_desc = f"GPU: {self._gpu_info['name']}" if self._gpu_info["available"] else "Requires GPU"
        f2 = tk.Frame(opts_inner, bg=SURFACE_CARD)
        f2.pack(fill=tk.X, pady=1)
        tk.Checkbutton(f2, text="🔒 Invisible watermarks", variable=self.invisible_var,
                       bg=SURFACE_CARD, fg=TEXT, selectcolor=SURFACE,
                       activebackground=SURFACE_CARD, font=(FONT_FAMILY, FONT_SIZE),
                       relief=tk.FLAT, bd=0, state=inv_state).pack(anchor=tk.W)
        tk.Label(f2, text=f"    {gpu_desc}", bg=SURFACE_CARD, fg=TEXT_DIM,
                 font=(FONT_FAMILY, FONT_SIZE_SM)).pack(anchor=tk.W)

        # ── AVIF ───────────────────────────────────────
        tk.Label(p, text="OUTPUT FORMAT", bg=SURFACE_CARD, fg=TEXT_MID,
                 font=(FONT_FAMILY, FONT_SIZE_SM, "bold")).pack(anchor=tk.W, padx=px, pady=(0, 3))

        card_avif = _card(p)
        card_avif.pack(fill=tk.X, padx=px, pady=(0, 4))

        avif_inner = tk.Frame(card_avif, bg=SURFACE_CARD)
        avif_inner.pack(fill=tk.X, padx=8, pady=(6, 6))

        tk.Checkbutton(avif_inner, text="🔄 Convert to AVIF", variable=self.avif_var,
                       bg=SURFACE_CARD, fg=TEXT, selectcolor=SURFACE,
                       activebackground=SURFACE_CARD, font=(FONT_FAMILY, FONT_SIZE),
                       relief=tk.FLAT, bd=0, command=self._update_avif_estimate).pack(anchor=tk.W)

        # Quality label row
        q_row = tk.Frame(avif_inner, bg=SURFACE_CARD)
        q_row.pack(fill=tk.X, pady=(6, 2))

        tk.Label(q_row, text="Quality:", bg=SURFACE_CARD, fg=TEXT_MID,
                 font=(FONT_FAMILY, FONT_SIZE_SM)).pack(side=tk.LEFT)

        self._quality_label = tk.Label(q_row, text="75", bg=SURFACE_CARD, fg=ACCENT,
                                       font=(FONT_FAMILY, FONT_SIZE, "bold"), width=3)
        self._quality_label.pack(side=tk.LEFT, padx=(4, 0))

        # Slider with 1px border
        slider_outer = tk.Frame(avif_inner, bg=SURFACE_CARD, highlightbackground=BORDER_LIGHT, highlightthickness=1)
        slider_outer.pack(fill=tk.X, pady=(0, 0))

        self._slider = tk.Scale(
            slider_outer, from_=30, to=100, orient=tk.HORIZONTAL,
            variable=self.avif_quality, bg=SURFACE_CARD, fg=ACCENT,
            troughcolor=SURFACE, highlightthickness=0, bd=0,
            length=200, showvalue=False, command=self._on_quality_change,
        )
        self._slider.pack(fill=tk.X, padx=2, pady=2)

        self._size_estimate = tk.Label(
            avif_inner, text="~85 KB per image (estimated)",
            bg=SURFACE_CARD, fg=TEXT_DIM, font=(FONT_FAMILY, FONT_SIZE_SM, "italic"), anchor=tk.W,
        )
        self._size_estimate.pack(fill=tk.X, pady=(4, 0))

        # ── GPU Status ─────────────────────────────────
        tk.Label(p, text="GPU STATUS", bg=SURFACE_CARD, fg=TEXT_MID,
                 font=(FONT_FAMILY, FONT_SIZE_SM, "bold")).pack(anchor=tk.W, padx=px, pady=(0, 3))

        card_gpu = _card(p)
        card_gpu.pack(fill=tk.X, padx=px, pady=(0, 8))

        gpu_inner = tk.Frame(card_gpu, bg=SURFACE_CARD)
        gpu_inner.pack(fill=tk.X, padx=8, pady=(6, 6))

        gpu_color = ACCENT if self._gpu_info["available"] else WARNING
        gpu_icon = "✓" if self._gpu_info["available"] else "✗"
        gpu_name = self._gpu_info['name'] if self._gpu_info["available"] else "No GPU detected"

        tk.Label(gpu_inner, text=f"{gpu_icon}  {gpu_name}", bg=SURFACE_CARD, fg=gpu_color,
                 font=(FONT_FAMILY, FONT_SIZE, "bold"), anchor=tk.W).pack(fill=tk.X)

        if not self._gpu_info["available"]:
            tk.Label(gpu_inner, text="Invisible removal disabled", bg=SURFACE_CARD, fg=TEXT_DIM,
                     font=(FONT_FAMILY, FONT_SIZE_SM), anchor=tk.W).pack(fill=tk.X, pady=(2, 0))

    def _short_path(self, path: str, max_len: int = 30) -> str:
        p = path.replace("\\", "/")
        return ("..." + p[-(max_len - 3):]) if len(p) > max_len else p

    def _on_quality_change(self, val):
        self._quality_label.config(text=val)
        self._update_avif_estimate()

    def _update_avif_estimate(self):
        if not self.avif_var.get():
            self._size_estimate.config(text="AVIF conversion disabled", fg=TEXT_DIM)
            return
        q = self.avif_quality.get()
        est = "~120-150 KB" if q >= 90 else "~70-90 KB" if q >= 75 else "~45-60 KB" if q >= 60 else "~30-40 KB"
        self._size_estimate.config(text=f"{est} per image (estimated)", fg=ACCENT)

    def _pick_input(self):
        from pathlib import Path
        d = filedialog.askdirectory(title="Select Input Folder", initialdir=self.input_var.get())
        if d:
            self.input_var.set(d)
            self._input_label.config(text=self._short_path(d))
            set_last_input(Path(d))
            if self._on_input_change:
                self._on_input_change(d)

    def _pick_output(self):
        from pathlib import Path
        d = filedialog.askdirectory(title="Select Output Folder", initialdir=self.output_var.get())
        if d:
            self.output_var.set(d)
            self._output_label.config(text=self._short_path(d))
            set_last_output(Path(d))
            if self._on_output_change:
                self._on_output_change(d)
