"""Samsung Galaxy: a lock and home screen wallpaper sized for the Galaxy S24 Ultra.

One UI has no theme file to ship outside the Galaxy Themes store, so samsung/README.md walks through building
the theme in Theme Park (Good Lock) from the wallpaper and the hex values below.
"""
import os

import windows

NAME = 'ThatDataPurple'
# Galaxy S24 Ultra at its highest (WQHD+) resolution. One UI scales it for the other screen resolutions.
WIDTH, HEIGHT = 1440, 3120


def build(p, out_root):
    """Writes samsung/ThatDataPurple.S24Ultra.jpg under out_root. Returns paths written."""
    os.makedirs(out_root, exist_ok=True)
    path = os.path.join(out_root, f'{NAME}.S24Ultra.jpg')
    windows.wallpaper(p, path, WIDTH, HEIGHT)
    return [path]
