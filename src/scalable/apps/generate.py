#!/usr/bin/env python3
"""
Nothing OS Icon Generator
Generates black-circle white-glyph icons matching the Nothing OS aesthetic.
Usage: python3 generate.py
Output: ./output/*.png  — drop into ~/.local/share/icons/NothingOS/scalable/apps/
"""

import subprocess
import json
import os
import io
from PIL import Image, ImageDraw
import cairosvg

SIZE = 512
# Glyph occupies this fraction of canvas diameter
GLYPH_SCALE = 0.50

OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# SVG path data for icons not from simple-icons (hand-crafted, 0 0 24 24 viewbox)
# ---------------------------------------------------------------------------

CUSTOM_SVGS = {
    # Terminal
    "utilities-terminal": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M2 5.5C2 4.12 3.12 3 4.5 3h15C20.88 3 22 4.12 22 5.5v13c0 1.38-1.12 2.5-2.5 2.5h-15C3.12 21 2 19.88 2 18.5v-13zm2.5 0v13h15v-13h-15zM6.7 8.3a1 1 0 0 1 1.4 0l3 3a1 1 0 0 1 0 1.4l-3 3a1 1 0 0 1-1.4-1.4L9.08 12 6.7 9.7a1 1 0 0 1 0-1.4zM12 16a1 1 0 0 1 1-1h3a1 1 0 0 1 0 2h-3a1 1 0 0 1-1-1z"/>
    </svg>""",

    # App Store / Software (shopping bag)
    "org.gnome.Software": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M6 2a1 1 0 0 0-.894.553L3.106 6.5A1 1 0 0 0 3 7v13a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7a1 1 0 0 0-.106-.447l-2-4A1 1 0 0 0 18 2H6zm.618 2h10.764l1.5 3H5.118l1.5-3zM5 9h14v11H5V9zm4 2a1 1 0 0 0 0 2h.5v3.5a1 1 0 0 0 2 0V13H12a1 1 0 0 0 0-2H9zm4 0a1 1 0 0 0 0 2v4.5a1 1 0 0 0 2 0V11a1 1 0 0 0-2 0z"/>
    </svg>""",

    # VLC — cone (Material-style)
    "vlc": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2L3 19h18L12 2zm0 3.5L18.5 17h-13L12 5.5zM11 13v-3h2v3h-2zm0 2h2v2h-2v-2z"/>
    </svg>""",

    # LinkedIn
    "linkedin": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/>
    </svg>""",

    # Microsoft Teams
    "teams": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M19.19 8.77a2.5 2.5 0 1 0-2.5-2.5 2.5 2.5 0 0 0 2.5 2.5zm1.31.73h-2.62A1.38 1.38 0 0 0 16.5 10v4a3 3 0 0 0 1.5 2.6V18h2v-1.4A3 3 0 0 0 21.5 14v-4a1.38 1.38 0 0 0-1-1.5zM9 11A3 3 0 1 0 6 8a3 3 0 0 0 3 3zm3.5 1h-7A1.5 1.5 0 0 0 4 13.5v5A1.5 1.5 0 0 0 5.5 20h7a1.5 1.5 0 0 0 1.5-1.5v-5A1.5 1.5 0 0 0 12.5 12z"/>
    </svg>""",

    # Amazon
    "amazon": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M13.23 10.56v-.15c-.93.12-2.08.19-2.08 1.17 0 .51.27.86.74.86.34 0 .64-.21.84-.55.25-.41.5-.99.5-1.33zM21 17.5c-3.18 2.25-7.8 3.44-11.78 3.44C4.2 20.94.5 19.07.5 16c0-1.9 1.6-3.5 4.04-4.71-.38-.44-.6-1-.6-1.58 0-.56.21-1.12.6-1.56C2.54 7.33 1.5 5.77 1.5 4.03c0-2.78 2.54-4.03 5.08-4.03 1.41 0 2.72.35 3.77 1.01A5.06 5.06 0 0 1 13.5 0c2.19 0 3.8 1.09 3.8 3.1 0 .29-.05.55-.12.8H18c.55 0 1 .45 1 1v1h-1v7c0 .28.22.5.5.5H19l2 2v2.1zM8.5 6c0-1.1-.67-1.75-1.5-1.75S5.5 4.9 5.5 6s.67 1.75 1.5 1.75S8.5 7.1 8.5 6zm5.5 5.83c0-2.08-1.12-2.73-3.23-2.73-.93 0-2.04.15-2.77.46v.77c.62-.27 1.49-.42 2.29-.42 1.24 0 1.71.42 1.71 1.34v.54c-.37-.04-.74-.06-1.12-.06-1.8 0-3.38.62-3.38 2.27 0 1.38.99 2.15 2.46 2.15.98 0 1.79-.45 2.23-1.19h.04l.19 1h1.71c-.07-.42-.13-1.08-.13-1.67v-2.46z"/>
    </svg>""",

    # Prime Video
    "prime-video": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M8 6.82v10.36c0 .79.87 1.27 1.54.84l8.14-5.18a1 1 0 0 0 0-1.68L9.54 5.98A1 1 0 0 0 8 6.82z"/>
    </svg>""",

    # Microsoft Edge
    "microsoft-edge": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M21 9.5c0-3.59-3.13-6.5-7-6.5a7.31 7.31 0 0 0-5.6 2.6A5 5 0 0 0 4 10.5c0 1.07.32 2.06.87 2.89C3.76 14.07 3 15.2 3 16.5 3 19 5.24 21 8 21h11.5a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5H8c-1.38 0-2.5-.9-2.5-2 0-.85.62-1.58 1.5-1.9C8.33 15.66 10 16 12 16c1.95 0 3.7-.31 5-1.03V17h2V9.5zM12 14c-3.31 0-6-1.12-6-2.5S8.69 9 12 9s6 1.12 6 2.5S15.31 14 12 14z"/>
    </svg>""",

    # Darktable — aperture/camera
    "darktable": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 2a8 8 0 0 1 8 8 8 8 0 0 1-8 8 8 8 0 0 1-8-8 8 8 0 0 1 8-8zm0 2a6 6 0 0 0-6 6 6 6 0 0 0 6 6 6 6 0 0 0 6-6 6 6 0 0 0-6-6zm0 2a4 4 0 0 1 4 4 4 4 0 0 1-4 4 4 4 0 0 1-4-4 4 4 0 0 1 4-4z"/>
    </svg>""",

    # Rhythmbox — music note
    "rhythmbox": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 3v10.55A4 4 0 1 0 14 17V7h4V3h-6zm-2 16a2 2 0 1 1 2-2 2 2 0 0 1-2 2z"/>
    </svg>""",

    # GitHub Desktop
    "github-desktop": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2A10 10 0 0 0 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0 0 12 2z"/>
    </svg>""",

    # Docker Desktop (whale)
    "docker-desktop": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M13 3.5h2v2h-2zm-3 0h2v2h-2zm-3 0h2v2H7zm3 3h2v2h-2zm3 0h2v2h-2zm3 0h2v2h-2zm-9 0h2v2H7zm-3 3h2v2H4zm3 0h2v2H7zm3 0h2v2h-2zm3 0h2v2h-2zm3 0h2v2h-2zm2.5 2.5a1 1 0 0 0-1-1H3.5a1 1 0 0 0-1 1v.5C2.5 15 4 17 8.5 17c3.5 0 5.5-1 6.93-2.5H17a3 3 0 0 0 2.5-4.5c-.5 0-1 .5-1 .5z"/>
    </svg>""",

    # Bottles (wine glass)
    "bottles": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M15 3H9v2l-2 4v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9l-2-4V3zm0 2v1H9V5h6zm1 4v9H8V9h8zm-5 2v2H9v-2h2zm0 3v2H9v-2h2z"/>
    </svg>""",

    # Timeshift — clock with arrow
    "timeshift": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7zM7 4.07L3.07 8 2 6.93 5.93 3 7 4.07zM21.93 8 18 4.07 19.07 3 23 6.93 21.93 8z"/>
    </svg>""",

    # Brasero — disc with flame
    "brasero": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-12.5c0 2.5-2.5 3-2.5 5.5h5c0-2.5-2.5-3-2.5-5.5zm-1.25 7.5h2.5v1h-2.5z"/>
    </svg>""",

    # Evolution — envelope
    "evolution": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"/>
    </svg>""",

    # Videos / Totem — play button
    "totem": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4zM10 15V9l5 3-5 3z"/>
    </svg>""",

    # Sunshine — sun (remote play)
    "sunshine": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 7a5 5 0 1 0 5 5 5 5 0 0 0-5-5zm0 8a3 3 0 1 1 3-3 3 3 0 0 1-3 3zm-1-14h2v3h-2zm0 16h2v3h-2zM3 11h3v2H3zm15 0h3v2h-3zM5.64 5.64l1.42 1.42-1.42 1.42-1.42-1.42zm12.73 12.73 1.42 1.42-1.42 1.42-1.42-1.42zm-12.73 0-1.42 1.42-1.42-1.42 1.42-1.42zm12.73-12.73 1.42-1.42 1.42 1.42-1.42 1.42z"/>
    </svg>""",

    # Solaar — wireless/Logitech
    "solaar": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2A7.2 7.2 0 0 1 5 14c0-2.38 2.81-4 7-4s7 1.62 7 4a7.2 7.2 0 0 1-7 5.2z"/>
    </svg>""",

    # Remmina — remote desktop screen
    "remmina": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M20 3H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h3l-1 1v2h12v-2l-1-1h3a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2zm0 13H4V5h16v11zM9.5 8.5l4 3-4 3V8.5z"/>
    </svg>""",

    # Camera
    "camera": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 15.2a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4zM9 2L7.17 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-3.17L15 2H9zm3 15a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"/>
    </svg>""",

    # Weather
    "org.gnome.Weather": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M6.76 4.84l-1.8-1.79-1.41 1.41 1.79 1.79 1.42-1.41zM4 10.5H1v2h3v-2zm9-9.95h-2V3.5h2V.55zm7.45 3.91-1.41-1.41-1.79 1.79 1.41 1.41 1.79-1.79zm-3.21 13.7 1.79 1.8 1.41-1.41-1.8-1.79-1.4 1.4zM20 10.5v2h3v-2h-3zm-8-5a6 6 0 0 0-6 6 6 6 0 0 0 6 6 6 6 0 0 0 6-6 6 6 0 0 0-6-6zm-1 16.95h2V19.5h-2v2.95zm-7.45-3.91 1.41 1.41 1.79-1.8-1.41-1.41-1.79 1.8z"/>
    </svg>""",

    # Clocks / Clock
    "org.gnome.clocks": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
    </svg>""",

    # Calendar
    "org.gnome.Calendar": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M19 3h-1V1h-2v2H8V1H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
    </svg>""",

    # Contacts
    "org.gnome.Contacts": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M20 0H4v2h16V0zM4 24h16v-2H4v2zM20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm-8 2.75A2.25 2.25 0 1 1 9.75 9 2.25 2.25 0 0 1 12 6.75zM17 17H7v-.75c0-1.67 3.33-2.5 5-2.5s5 .83 5 2.5V17z"/>
    </svg>""",

    # Settings / System Settings
    "gnome-control-center": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.49.49 0 0 0-.59-.22l-2.39.96a7.03 7.03 0 0 0-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54a7.4 7.4 0 0 0-1.62.94l-2.39-.96a.48.48 0 0 0-.59.22L2.74 8.87a.47.47 0 0 0 .12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54a7.4 7.4 0 0 0 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.47.47 0 0 0-.12-.61l-2.01-1.58zM12 15.6a3.6 3.6 0 1 1 0-7.2 3.6 3.6 0 0 1 0 7.2z"/>
    </svg>""",

    # Files / Nautilus
    "org.gnome.Nautilus": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M10 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-8l-2-2z"/>
    </svg>""",

    # Image Viewer / Eye of GNOME
    "eog": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17a5 5 0 1 1 0-10 5 5 0 0 1 0 10zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"/>
    </svg>""",

    # Text Editor / gedit
    "org.gnome.TextEditor": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M14.06 9.02l.92.92L5.92 19H5v-.92l9.06-9.06zM17.66 3a1 1 0 0 0-.7.29L15.13 5.12l3.75 3.75 1.82-1.82a1 1 0 0 0 0-1.41l-2.34-2.34a.98.98 0 0 0-.7-.3zM3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"/>
    </svg>""",

    # Calculator
    "org.gnome.Calculator": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2zm-7 3h2v2h2v2h-2v2h-2v-2H8V8h2V6zm-4 9h2v2H8v-2zm4 0h2v2h-2v-2zm4 0h2v2h-2v-2zm0-4h2v2h-2v-2z"/>
    </svg>""",

    # System Monitor
    "gnome-system-monitor": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M22 9V7h-2V5a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-2h2v-2h-2v-2h2v-2h-2V9h2zm-4 10H4V5h14v14zM6 13h2l2-6 2 9 2-5 1 2h2v-2h-1l-2-4-2 5-2-8L8 13H6v-2H5v2h1z"/>
    </svg>""",

    # Disks
    "gnome-disks": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8zm0-12a4 4 0 1 0 4 4 4 4 0 0 0-4-4zm0 6a2 2 0 1 1 2-2 2 2 0 0 1-2 2z"/>
    </svg>""",

    # File Roller (archive manager)
    "file-roller": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M20 6h-8l-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2zm-8 10h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V6h2v2z"/>
    </svg>""",

    # Passwords / Seahorse
    "seahorse": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12.65 10A6 6 0 0 0 7 6a6 6 0 0 0-6 6 6 6 0 0 0 6 6 6 6 0 0 0 5.65-4H17v4h4v-4h2v-4H12.65zM7 14a2 2 0 1 1 2-2 2 2 0 0 1-2 2z"/>
    </svg>""",

    # Tweaks / GNOME Tweaks
    "org.gnome.tweaks": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/>
    </svg>""",

    # Logs / GNOME Logs
    "gnome-logs": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM8 15h8v2H8zm0-4h8v2H8z"/>
    </svg>""",

    # Backups / Deja Dup
    "deja-dup": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M13 3a9 9 0 0 0-9 9H1l3.89 3.89.07.14L9 12H6a7 7 0 0 1 7-7 7 7 0 0 1 7 7 7 7 0 0 1-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0 0 13 21a9 9 0 0 0 9-9 9 9 0 0 0-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"/>
    </svg>""",

    # Extension Manager
    "com.mattjakeman.ExtensionManager": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M20.5 11H19V7a2 2 0 0 0-2-2h-4V3.5A2.5 2.5 0 0 0 10.5 1 2.5 2.5 0 0 0 8 3.5V5H4a2 2 0 0 0-2 2v3.8h1.5a2.7 2.7 0 0 1 2.7 2.7 2.7 2.7 0 0 1-2.7 2.7H2V19a2 2 0 0 0 2 2h3.8v-1.5a2.7 2.7 0 0 1 2.7-2.7 2.7 2.7 0 0 1 2.7 2.7V21H17a2 2 0 0 0 2-2v-4h1.5a2.5 2.5 0 0 0 2.5-2.5 2.5 2.5 0 0 0-2.5-2.5z"/>
    </svg>""",

    # dconf Editor
    "ca.desrt.dconf-editor": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M3 3h18v2H3zm0 4h18v2H3zm0 4h18v2H3zm0 4h18v2H3zm0 4h18v2H3z"/>
    </svg>""",

    # Document Viewer / Evince
    "evince": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2zm-7 3l4 4h-4V6zM8 17v-2h8v2H8zm0-4v-2h8v2H8zm4-6v3h3l-3-3z"/>
    </svg>""",

    # Document Scanner
    "simple-scan": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M19 4H5a1 1 0 0 0-1 1v1h16V5a1 1 0 0 0-1-1zM4 18h16V8H4v10zm2-8h12v6H6v-6zm0 0v1h12v-1H6zM3 20h18v2H3z"/>
    </svg>""",

    # Firewall Config
    "firewall-config": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 4c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm6 10.13A8.997 8.997 0 0 1 12 19a8.997 8.997 0 0 1-6-3.87V14c0-2 4-3.1 6-3.1 2 0 6 1.1 6 3.1v1.13z"/>
    </svg>""",

    # Characters (GNOME Characters)
    "org.gnome.Characters": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M2.5 4v3h5v12h3V7h5V4h-13zm19 5h-9v3h3v7h3v-7h3V9z"/>
    </svg>""",

    # Fonts (GNOME Fonts)
    "org.gnome.font-viewer": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M9.93 13.5h4.14L12 7.98 9.93 13.5zM20 2H4a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zm-4.05 16.5-1.14-3H9.17l-1.12 3H5.96l5.11-13h1.86l5.11 13h-2.09z"/>
    </svg>""",

    # Disk Usage Analyzer (Baobab)
    "baobab": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 2a8 8 0 0 1 7.94 7H13V4.06A8 8 0 0 1 12 4zM4.06 13H11v6.94A8 8 0 0 1 4.06 13zm8.94 6.94V13h6.94A8 8 0 0 1 13 19.94z"/>
    </svg>""",

    # Advanced Network Config
    "nm-connection-editor": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8 3 3 3-3a4.237 4.237 0 0 0-6 0zm-4-4 2 2a7.074 7.074 0 0 1 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/>
    </svg>""",

    # Power Statistics
    "gnome-power-statistics": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4zM13 18h-2v-2h2v2zm0-4h-2V9h2v5z"/>
    </svg>""",

    # Parental Controls
    "malcontent-control": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2C8.13 2 5 5.13 5 9v2H3v10h18V11h-2V9c0-3.87-3.13-7-7-7zm0 2c2.76 0 5 2.24 5 5v2H7V9c0-2.76 2.24-5 5-5zm0 9a2 2 0 0 1 2 2c0 .74-.4 1.38-1 1.73V19h-2v-2.27A2 2 0 0 1 10 15a2 2 0 0 1 2-2z"/>
    </svg>""",

    # Sound Recorder
    "org.gnome.SoundRecorder": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-3-3 3 3 0 0 0-3 3v6a3 3 0 0 0 3 3zm5.3-3a5.3 5.3 0 0 1-5.3 5.3A5.3 5.3 0 0 1 6.7 11H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-1.7z"/>
    </svg>""",

    # Startup Applications
    "gnome-session-properties": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M8 5.14v14l11-7-11-7z"/>
    </svg>""",

    # Web Apps (Gnome Web / Epiphany)
    "epiphany": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zm6.93 6h-2.95a15.65 15.65 0 0 0-1.38-3.56A8.03 8.03 0 0 1 18.92 8zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14C4.1 13.36 4 12.69 4 12s.1-1.36.26-2h3.38c-.08.66-.14 1.32-.14 2s.06 1.34.14 2H4.26zm.82 2h2.95c.32 1.25.78 2.45 1.38 3.56A7.987 7.987 0 0 1 5.08 16zm2.95-8H5.08a7.987 7.987 0 0 1 4.33-3.56A15.65 15.65 0 0 0 8.03 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82c-.43 1.43-1.08 2.76-1.91 3.96zM14.34 14H9.66c-.09-.66-.16-1.32-.16-2s.07-1.35.16-2h4.68c.09.65.16 1.32.16 2s-.07 1.34-.16 2zm.25 5.56A15.65 15.65 0 0 0 15.97 16h2.95a8.03 8.03 0 0 1-4.33 3.56zM15.97 8c-.32-1.25-.78-2.45-1.38-3.56A8.03 8.03 0 0 1 18.92 8h-2.95z"/>
    </svg>""",

    # Main Menu (alacarte)
    "alacarte": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
    </svg>""",

    # Zorin Appearance
    "zorin-appearance": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 3a9 9 0 0 0-9 9 9 9 0 0 0 9 9 9 9 0 0 0 9-9 9 9 0 0 0-9-9zm0 2a7 7 0 0 1 7 7 7 7 0 0 1-7 7V5z"/>
    </svg>""",

    # Zorin Connect
    "zorin-connect": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M17 1H7a2 2 0 0 0-2 2v18a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2zm-5 20a1.5 1.5 0 0 1 0-3 1.5 1.5 0 0 1 0 3zm5-5H7V4h10v12z"/>
    </svg>""",

    # Help (yelp)
    "yelp": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
    </svg>""",
}

# ---------------------------------------------------------------------------
# Brand icons from simple-icons + their output filename (GNOME icon name)
# ---------------------------------------------------------------------------

BRAND_ICONS = [
    # Previously generated
    ("siVscodium",              "vscodium"),
    ("siClaude",                "claude"),
    ("siSimplenote",            "simplenote"),
    ("siLibreoffice",           "libreoffice-startcenter"),
    ("siLibreofficewriter",     "libreoffice-writer"),
    ("siLibreofficecalc",       "libreoffice-calc"),
    ("siLibreofficeimpress",    "libreoffice-impress"),
    ("siLibreofficedraw",       "libreoffice-draw"),
    ("siLibreofficebase",       "libreoffice-base"),
    ("siLibreofficemath",       "libreoffice-math"),
    # Browsers
    ("siBrave",                 "brave-browser"),
    ("siFirefox",               "firefox"),
    ("siGooglechrome",          "google-chrome"),
    # Social / communication
    ("siDiscord",               "discord"),
    ("siWhatsapp",              "whatsapp-desktop"),
    ("siReddit",                "reddit"),
    ("siTelegram",              "telegram-desktop"),
    ("siSignal",                "signal-desktop"),
    # Media
    ("siSpotify",               "spotify"),
    ("siYoutube",               "youtube"),
    ("siVlcmediaplayer",        "vlc"),
    # Dev tools
    ("siGithub",                "github-desktop"),
    ("siObsidian",              "obsidian"),
    ("siDocker",                "docker"),
    # Creative
    ("siGimp",                  "gimp"),
    ("siInkscape",              "inkscape"),
    ("siPenpot",                "penpot"),
    ("siKrita",                 "krita"),
    ("siFreecad",               "freecad"),
    ("siBlender",               "blender"),
    # Knowledge / reference
    ("siWikipedia",             "wikipedia"),
    ("siPerplexity",            "perplexity"),
    # Google web apps
    ("siGmail",                 "gmail"),
    ("siGoogledrive",           "google-drive"),
    ("siGoogledocs",            "google-docs"),
    ("siGoogleslides",          "google-slides"),
    ("siGoogletranslate",       "google-translate"),
    ("siGooglepay",             "google-pay"),
    ("siGooglemaps",            "google-maps"),
    ("siGooglephotos",          "google-photos"),
    # Proton suite
    ("siProtonmail",            "protonmail"),
    ("siProtonvpn",             "proton-vpn"),
    # Other brands
    ("siShazam",                "shazam"),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def svg_path_to_image(svg_str: str, size: int) -> Image.Image:
    """Rasterize an SVG string to a PIL RGBA image at the given size."""
    png_bytes = cairosvg.svg2png(
        bytestring=svg_str.encode(),
        output_width=size,
        output_height=size,
    )
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def make_black(img: Image.Image) -> Image.Image:
    """Force all visible pixels to black, preserving alpha."""
    r, g, b, a = img.split()
    black = Image.new("RGBA", img.size, (0, 0, 0, 255))
    black.putalpha(a)
    return black


def composite_on_circle(glyph: Image.Image, canvas_size: int) -> Image.Image:
    """Place a black glyph centered on a white circle."""
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    # Draw white circle
    circle = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, canvas_size - 1, canvas_size - 1), fill=(255, 255, 255, 255))
    canvas.paste(circle, (0, 0), circle)

    # Center glyph
    gx, gy = glyph.size
    ox = (canvas_size - gx) // 2
    oy = (canvas_size - gy) // 2
    canvas.paste(glyph, (ox, oy), glyph)

    return canvas


def generate(name: str, svg_str: str):
    glyph_size = int(SIZE * GLYPH_SCALE)
    glyph = svg_path_to_image(svg_str, glyph_size)
    glyph = make_black(glyph)
    icon = composite_on_circle(glyph, SIZE)
    out = os.path.join(OUTPUT_DIR, f"{name}.png")
    icon.save(out, "PNG")
    print(f"  ✓  {name}.png")


# ---------------------------------------------------------------------------
# Fetch brand icon SVGs via Node + simple-icons
# ---------------------------------------------------------------------------

def get_brand_svgs() -> dict:
    """Ask Node to dump all needed SVG paths as JSON."""
    keys = [k for k, _ in BRAND_ICONS]
    script = f"""
const si = require('./node_modules/simple-icons');
const keys = {json.dumps(keys)};
const out = {{}};
keys.forEach(k => {{
    const icon = si[k];
    if (icon) {{
        out[k] = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="${{icon.path}}"/></svg>`;
    }}
}});
process.stdout.write(JSON.stringify(out));
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Node error: {result.stderr}")
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"\nNothing OS Icon Generator")
    print(f"Canvas: {SIZE}px  |  Glyph: {int(SIZE * GLYPH_SCALE)}px  ({int(GLYPH_SCALE*100)}% scale)")
    print(f"Output: {os.path.abspath(OUTPUT_DIR)}\n")

    # Brand icons
    print("Brand icons:")
    brand_svgs = get_brand_svgs()
    for si_key, filename in BRAND_ICONS:
        if si_key in brand_svgs:
            generate(filename, brand_svgs[si_key])
        else:
            print(f"  ✗  {filename} (not found in simple-icons)")

    # Custom hand-crafted icons
    print("\nCustom icons:")
    for filename, svg_str in CUSTOM_SVGS.items():
        generate(filename, svg_str)

    print(f"\nDone! Copy to your icon theme with:")
    print(f"  cp output/*.png ~/.local/share/icons/NothingOS/scalable/apps/")
    print(f"  gtk-update-icon-cache ~/.local/share/icons/NothingOS")
