"""Rounded corners widget — Canvas-based with 5px radius."""

from __future__ import annotations

import tkinter as tk

from config import BG, BORDER_LIGHT, SURFACE_CARD


class RoundedFrame(tk.Frame):
    """Frame with canvas-drawn rounded corners (5px radius)."""

    def __init__(self, parent, bg=SURFACE_CARD, border_color=BORDER_LIGHT, radius=5, **kw):
        super().__init__(parent, bg=parent.cget("bg") if hasattr(parent, 'cget') else BG, **kw)
        self._bg = bg
        self._border = border_color
        self._radius = radius

        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._inner = tk.Frame(self._canvas, bg=bg)
        self._canvas.create_window(0, 0, window=self._inner, anchor=tk.NW, tags="inner")

        # When inner frame changes size, update canvas and draw border
        self._inner.bind("<Configure>", self._on_inner_configure)
        self.bind("<Configure>", self._on_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_inner_configure(self, event):
        """Resize canvas to match inner frame content."""
        self._canvas.configure(width=event.width, height=event.height)
        self.configure(width=event.width, height=event.height)
        self._draw_border()

    def _on_configure(self, event):
        self._draw_border()

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig("inner", width=event.width, height=event.height)
        self._draw_border()

    def _on_configure(self, event):
        self._draw_border()

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig("inner", width=event.width, height=event.height)
        self._draw_border()

    def _draw_border(self):
        self._canvas.delete("border")
        w = self._canvas.winfo_width()
        h = self._canvas.winfo_height()
        if w < 2 or h < 2:
            return
        r = min(self._radius, w // 4, h // 4)
        self._rounded_rect(1, 1, w - 1, h - 1, r)

    def _rounded_rect(self, x1, y1, x2, y2, r):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        self._canvas.create_polygon(points, smooth=True, fill=self._bg,
                                     outline=self._border, width=1, tags="border")
        self._canvas.tag_lower("border")

    def inner_frame(self):
        return self._inner


class RoundedButton(tk.Canvas):
    """Clickable rounded button using Canvas."""

    def __init__(self, parent, text="", bg="#1a6650", fg="#33CC99",
                 command=None, radius=10, font=("Segoe UI", 11, "bold"), **kw):
        super().__init__(parent, bg=parent.cget("bg") if hasattr(parent, 'cget') else BG,
                         highlightthickness=0, bd=0, cursor="hand2", **kw)
        self._bg = bg
        self._fg = fg
        self._command = command
        self._radius = radius
        self._font = font
        self._text = text
        self._hovered = False

        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2 or h < 2:
            return
        r = min(self._radius, w // 4, h // 4)
        self._rounded_rect(1, 1, w - 1, h - 1, r, fill=self._bg, outline=self._bg)
        self.create_text(w // 2, h // 2, text=self._text, fill=self._fg,
                         font=self._font, tags="text")

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        self.create_polygon(points, smooth=True, **kw)

    def _on_click(self, event):
        if self._command:
            self._command()

    def _on_enter(self, event):
        self._hovered = True
        self._draw_hover()

    def _on_leave(self, event):
        self._hovered = False
        self._draw()

    def _draw_hover(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2 or h < 2:
            return
        r = min(self._radius, w // 4, h // 4)
        self._rounded_rect(1, 1, w - 1, h - 1, r, fill=self._bg, outline=self._fg, width=1)
        self.create_text(w // 2, h // 2, text=self._text, fill=self._fg,
                         font=self._font, tags="text")
