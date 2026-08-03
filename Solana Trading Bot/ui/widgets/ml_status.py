"""ML status view showing model performance."""

import tkinter as tk

from ui.config import (
    SURFACE_CARD, SURFACE, TEXT, TEXT_DIM, TEXT_MID, TEXT_BRIGHT,
    ACCENT, ACCENT_DIM, SUCCESS, ERROR, WARNING,
    FONT_FAMILY, FONT_SIZE, FONT_SIZE_SM, FONT_SIZE_XL,
    PAD_X, PAD_Y, CARD_PAD,
)
from ui.components import styled_frame, styled_label, section_header, status_badge


class MLStatusView(tk.Frame):
    """ML model status panel."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE_CARD)
        self.app = app
        self._build_ui()
    
    def _build_ui(self):
        header = section_header(self, "ML Status", "Model performance and training")
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y, PAD_Y // 2))
        
        # Status card
        status_card = styled_frame(self)
        status_card.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        self.status_badge = status_badge(status_card, "NOT LOADED", status="warning")
        self.status_badge.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, 0))
        
        self.model_info = styled_label(status_card, "No model currently loaded", size=FONT_SIZE, color=TEXT_DIM, bg=SURFACE_CARD)
        self.model_info.pack(anchor="w", padx=CARD_PAD, pady=(PAD_Y, CARD_PAD))
        
        # Metrics
        metrics_card = styled_frame(self)
        metrics_card.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        metrics_header = styled_label(metrics_card, "PERFORMANCE METRICS", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        metrics_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))
        
        metrics_grid = tk.Frame(metrics_card, bg=SURFACE_CARD)
        metrics_grid.pack(fill=tk.X, padx=CARD_PAD, pady=(0, CARD_PAD))
        
        self.metric_labels = {}
        metrics = [
            ("accuracy", "Accuracy", "—"),
            ("precision", "Precision", "—"),
            ("recall", "Recall", "—"),
            ("f1", "F1 Score", "—"),
            ("trades", "Trades Analyzed", "0"),
            ("last_train", "Last Training", "—"),
        ]
        
        for i, (key, label, default) in enumerate(metrics):
            frame = tk.Frame(metrics_grid, bg=SURFACE_CARD)
            frame.grid(row=i // 3, column=i % 3, sticky="w", padx=(0, 40), pady=8)
            
            lbl = styled_label(frame, label, size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
            lbl.pack(anchor="w")
            
            val = styled_label(frame, default, size=FONT_SIZE_XL, color=ACCENT, bold=True, bg=SURFACE_CARD)
            val.pack(anchor="w")
            
            self.metric_labels[key] = val
        
        # Feature importance
        features_card = styled_frame(self)
        features_card.pack(fill=tk.BOTH, expand=True, padx=PAD_X, pady=PAD_Y)
        
        features_header = styled_label(features_card, "FEATURE IMPORTANCE", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        features_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))
        
        self.features_text = tk.Text(
            features_card,
            font=(FONT_FAMILY, FONT_SIZE),
            fg=TEXT,
            bg=SURFACE,
            insertbackground=TEXT,
            highlightthickness=0,
            bd=0,
            wrap=tk.WORD,
            padx=CARD_PAD,
            pady=CARD_PAD,
        )
        self.features_text.pack(fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=(0, CARD_PAD))
        self.features_text.insert(tk.END, "Train the model to see feature importance.")
        self.features_text.config(state=tk.DISABLED)
    
    def update_status(self, loaded, info=""):
        """Update model status."""
        self.status_badge.destroy()
        if loaded:
            self.status_badge = status_badge(self.status_badge.master, "LOADED", status="success")
            self.model_info.config(text=info or "Model ready for inference")
        else:
            self.status_badge = status_badge(self.status_badge.master, "NOT LOADED", status="warning")
            self.model_info.config(text=info or "No model currently loaded")
        self.status_badge.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, 0))
    
    def update_metrics(self, metrics):
        """Update performance metrics."""
        for key, val in metrics.items():
            if key in self.metric_labels:
                self.metric_labels[key].config(text=str(val))
    
    def update_features(self, features_text):
        """Update feature importance text."""
        self.features_text.config(state=tk.NORMAL)
        self.features_text.delete(1.0, tk.END)
        self.features_text.insert(tk.END, features_text)
        self.features_text.config(state=tk.DISABLED)
