"""Entry point — launch the AI Image Cleaner GUI."""

from __future__ import annotations

import sys
import os
import tkinter as tk

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

if base_path not in sys.path:
    sys.path.insert(0, base_path)

from app import App


def main():
    root = tk.Tk()
    root.withdraw()

    app = App(root)

    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
