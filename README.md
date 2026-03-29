# Nothing Icons

A clean and minimal icon theme for Linux desktops, inspired by the Nothing OS aesthetic.

## Features

- **Minimalist Design**: High-contrast, dot-matrix inspired icons.
- **Dark & Light Variants**: Optimized for both dark and light desktop environments.
- **Comprehensive Coverage**: Includes application icons, status icons, and symbolic icons.
- **Automatic Scaling**: Supports standard and HiDPI displays.

## Installation

### Standard (Dark) Variant
Recommended for dark themes.
```bash
git clone https://github.com/asernasr/nothing-icons.git
cd nothing-icons
./install.sh
```

### Light Variant
Optimized for light themes (uses color inversion for PNG icons).
```bash
./install-light.sh
```

### Options
Both installation scripts support the following options:
- `-d, --dest`: Specify theme destination directory (Default: `~/.local/share/icons`)
- `-n, --name`: Specify theme name
- `-r, --remove`: Remove the theme
- `-h, --help`: Show help

## Usage

After installation, you can apply the icon theme using your desktop's customization tool:
- **GNOME**: Use `GNOME Tweaks` -> Appearance -> Icons.
- **KDE Plasma**: System Settings -> Appearance -> Icons.
- **XFCE**: Settings -> Appearance -> Icons.

## Credits
Inspired by the Nothing OS design language.
