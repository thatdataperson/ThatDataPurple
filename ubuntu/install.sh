#!/usr/bin/env bash
# Installs ThatDataPurple for Ubuntu (GNOME): the Ptyxis terminal palette, libadwaita colours and the wallpaper.
# Run it as yourself, not with sudo. Undo it with uninstall.sh.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
MARK='ThatDataPurple for GNOME apps'
GNOME_TERMINAL_PROFILE='40507e64-001d-47fb-bceb-9f05fe0426bd'

# Terminal: add the palette and select it in every Ptyxis profile.
mkdir -p "$DATA/org.gnome.Ptyxis/palettes"
cp "$HERE/terminal/ThatDataPurple.palette" "$DATA/org.gnome.Ptyxis/palettes/"
if gsettings list-schemas | grep -qx org.gnome.Ptyxis; then
    for uuid in $(gsettings get org.gnome.Ptyxis profile-uuids | sed 's/^@as //' | tr -d "[]',"); do
        gsettings set "org.gnome.Ptyxis.Profile:/org/gnome/Ptyxis/Profiles/$uuid/" palette 'ThatDataPurple'
    done
    echo "Ptyxis: palette set (open a new window if it doesn't change straight away)"
fi

# GNOME Terminal (Ubuntu 25.04 and earlier): add a ThatDataPurple profile and make it the default.
if gsettings list-schemas | grep -qx org.gnome.Terminal.ProfilesList && command -v dconf >/dev/null; then
    dconf load "/org/gnome/terminal/legacy/profiles:/:$GNOME_TERMINAL_PROFILE/" < "$HERE/terminal/ThatDataPurple.gnome-terminal.dconf"
    profiles="$(gsettings get org.gnome.Terminal.ProfilesList list)"
    if [[ "$profiles" != *"$GNOME_TERMINAL_PROFILE"* ]]; then
        gsettings set org.gnome.Terminal.ProfilesList list "$(echo "$profiles" | sed "s/^@as //; s/]$/, '$GNOME_TERMINAL_PROFILE']/; s/\[, /[/")"
    fi
    gsettings set org.gnome.Terminal.ProfilesList default "$GNOME_TERMINAL_PROFILE"
    echo "GNOME Terminal: ThatDataPurple profile added and set as default"
fi

# GNOME apps: keep any gtk.css that isn't ours, so uninstall.sh can put it back.
mkdir -p "$CONFIG/gtk-4.0"
css="$CONFIG/gtk-4.0/gtk.css"
if [ -f "$css" ] && ! grep -q "$MARK" "$css"; then
    mv "$css" "$css.before-thatdatapurple"
    echo "Kept your old gtk.css as $css.before-thatdatapurple"
fi
cp "$HERE/gtk-4.0/gtk.css" "$css"
echo "GNOME apps: colours installed (apps pick them up when they next start)"

# Desktop: wallpaper, purple accent and dark style.
mkdir -p "$DATA/backgrounds"
cp "$HERE/backgrounds/ThatDataPurple.jpg" "$DATA/backgrounds/"
uri="file://$DATA/backgrounds/ThatDataPurple.jpg"
gsettings set org.gnome.desktop.background picture-uri "$uri"
gsettings set org.gnome.desktop.background picture-uri-dark "$uri"
gsettings set org.gnome.desktop.background picture-options 'zoom'
gsettings set org.gnome.desktop.screensaver picture-uri "$uri"
gsettings set org.gnome.desktop.interface accent-color 'purple'
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
gsettings set org.gnome.desktop.interface gtk-theme 'Yaru-purple-dark'
echo "Desktop: wallpaper, purple accent and dark style set"
