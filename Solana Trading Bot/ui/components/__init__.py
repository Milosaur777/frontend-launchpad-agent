"""Reusable styled components for the trading bot UI."""

import tkinter as tk
from tkinter import ttk

from ui.config import (
    BG,
    SURFACE,
    SURFACE_CARD,
    SURFACE_HOVER,
    SURFACE_ACTIVE,
    BORDER,
    BORDER_LIGHT,
    BORDER_ACCENT,
    ACCENT,
    ACCENT_DIM,
    ACCENT_BRIGHT,
    TEXT,
    TEXT_DIM,
    TEXT_MID,
    TEXT_BRIGHT,
    WARNING,
    ERROR,
    SUCCESS,
    INFO,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_SM,
    FONT_SIZE_LG,
    FONT_SIZE_XL,
    FONT_SIZE_HERO,
    CORNER_RADIUS,
    CARD_RADIUS,
    PAD_X,
    PAD_Y,
    CARD_PAD,
)


def styled_frame(parent, bg=None, highlight=False):
    """Create a styled card frame."""
    bg = bg or SURFACE_CARD
    border_color = BORDER_ACCENT if highlight else BORDER_LIGHT
    
    frame = tk.Frame(
        parent,
        bg=bg,
        highlightbackground=border_color,
        highlightthickness=1,
        bd=0,
    )
    return frame


def styled_label(parent, text, size=FONT_SIZE, color=TEXT, bold=False, bg=None):
    """Create a styled label."""
    bg = bg or SURFACE_CARD
    font = (FONT_FAMILY, size, "bold" if bold else "normal")
    return tk.Label(parent, text=text, font=font, fg=color, bg=bg)


def styled_button(parent, text, command=None, variant="primary", width=None):
    """
    Create a styled button.
    
    Variants: primary, secondary, danger, success, ghost
    """
    variants = {
        "primary": {
            "bg": ACCENT_DIM,
            "fg": ACCENT,
            "hover_bg": ACCENT,
            "hover_fg": BG,
            "active_bg": ACCENT_BRIGHT,
            "border": ACCENT,
        },
        "secondary": {
            "bg": SURFACE,
            "fg": TEXT,
            "hover_bg": SURFACE_HOVER,
            "hover_fg": TEXT_BRIGHT,
            "active_bg": SURFACE_ACTIVE,
            "border": BORDER_LIGHT,
        },
        "danger": {
            "bg": "#3d1f1f",
            "fg": ERROR,
            "hover_bg": ERROR,
            "hover_fg": TEXT_BRIGHT,
            "active_bg": "#ff5555",
            "border": ERROR,
        },
        "success": {
            "bg": ACCENT_DIM,
            "fg": ACCENT,
            "hover_bg": ACCENT,
            "hover_fg": BG,
            "active_bg": ACCENT_BRIGHT,
            "border": ACCENT,
        },
        "warning": {
            "bg": "#3d2f1f",
            "fg": "#CC9933",
            "hover_bg": "#CC9933",
            "hover_fg": BG,
            "active_bg": "#FFAA44",
            "border": "#CC9933",
        },
        "ghost": {
            "bg": SURFACE_CARD,
            "fg": TEXT_MID,
            "hover_bg": SURFACE_HOVER,
            "hover_fg": TEXT,
            "active_bg": SURFACE_ACTIVE,
            "border": BORDER,
        },
    }
    
    v = variants[variant]
    
    btn = tk.Button(
        parent,
        text=text,
        font=(FONT_FAMILY, FONT_SIZE, "bold"),
        bg=v["bg"],
        fg=v["fg"],
        activebackground=v["active_bg"],
        activeforeground=v["hover_fg"],
        highlightbackground=v["border"],
        highlightthickness=1,
        bd=0,
        cursor="hand2",
        relief=tk.FLAT,
        command=command,
        width=width,
    )
    
    def on_enter(e):
        btn.config(bg=v["hover_bg"], fg=v["hover_fg"])
    
    def on_leave(e):
        btn.config(bg=v["bg"], fg=v["fg"])
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


def metric_card(parent, title, value, subtitle=None, color=None, width=None):
    """Create a metric card with title, large value, optional subtitle."""
    color = color or ACCENT
    card = styled_frame(parent)
    
    title_lbl = styled_label(card, title, size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
    title_lbl.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, 2))
    
    value_lbl = styled_label(card, value, size=FONT_SIZE_HERO, color=color, bold=True, bg=SURFACE_CARD)
    value_lbl.pack(anchor="w", padx=CARD_PAD, pady=(0, 2))
    
    if subtitle:
        sub_lbl = styled_label(card, subtitle, size=FONT_SIZE_SM, color=TEXT_DIM, bg=SURFACE_CARD)
        sub_lbl.pack(anchor="w", padx=CARD_PAD, pady=(0, CARD_PAD))
    else:
        value_lbl.pack_configure(pady=(0, CARD_PAD))
    
    if width:
        card.config(width=width)
        value_lbl.config(width=width - CARD_PAD * 2)
    
    return card, value_lbl


def section_header(parent, title, subtitle=None):
    """Create a section header."""
    container = tk.Frame(parent, bg=SURFACE_CARD)
    
    title_lbl = tk.Label(
        container,
        text=title,
        font=(FONT_FAMILY, FONT_SIZE_XL, "bold"),
        fg=TEXT_BRIGHT,
        bg=SURFACE_CARD,
    )
    title_lbl.pack(anchor="w")
    
    if subtitle:
        sub_lbl = tk.Label(
            container,
            text=subtitle,
            font=(FONT_FAMILY, FONT_SIZE_SM, "normal"),
            fg=TEXT_MID,
            bg=SURFACE_CARD,
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))
    
    return container


def status_badge(parent, text, status="success"):
    """Create a status badge (success, warning, error, info)."""
    colors = {
        "success": (ACCENT, ACCENT_DIM),
        "warning": (WARNING, "#3d2a10"),
        "error": (ERROR, "#3d1f1f"),
        "info": (INFO, "#1a2d4d"),
        "neutral": (TEXT_MID, SURFACE),
    }
    
    fg, bg = colors.get(status, colors["neutral"])
    
    badge = tk.Frame(parent, bg=bg, highlightbackground=fg, highlightthickness=1)
    
    lbl = tk.Label(
        badge,
        text=text,
        font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
        fg=fg,
        bg=bg,
    )
    lbl.pack(padx=8, pady=3)
    
    return badge


def scrollbar_style():
    """Apply custom scrollbar style to a ttk widget."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Vertical.TScrollbar",
        gripcount=0,
        background=ACCENT_DIM,
        darkcolor=SURFACE,
        lightcolor=SURFACE,
        troughcolor=SURFACE,
        bordercolor=SURFACE,
        arrowcolor=TEXT_MID,
    )
    style.configure(
        "Horizontal.TScrollbar",
        gripcount=0,
        background=ACCENT_DIM,
        darkcolor=SURFACE,
        lightcolor=SURFACE,
        troughcolor=SURFACE,
        bordercolor=SURFACE,
        arrowcolor=TEXT_MID,
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", ACCENT)],
        arrowcolor=[("active", TEXT)],
    )
    style.map(
        "Horizontal.TScrollbar",
        background=[("active", ACCENT)],
        arrowcolor=[("active", TEXT)],
    )
    return style


def style_treeview(tv, columns):
    """Style a ttk.Treeview to match the dark theme."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Custom.Treeview",
        background=SURFACE_CARD,
        foreground=TEXT,
        fieldbackground=SURFACE_CARD,
        bordercolor=BORDER_LIGHT,
        relief=tk.FLAT,
        rowheight=28,
        font=(FONT_FAMILY, FONT_SIZE),
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=SURFACE,
        foreground=TEXT_MID,
        font=(FONT_FAMILY, FONT_SIZE, "bold"),
        bordercolor=BORDER_LIGHT,
        relief=tk.FLAT,
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", ACCENT_DIM)],
        foreground=[("selected", ACCENT)],
    )
    tv.configure(style="Custom.Treeview")
    
    for col, heading in columns:
        tv.heading(col, text=heading)
        tv.column(col, anchor="w")
    
    return tv
