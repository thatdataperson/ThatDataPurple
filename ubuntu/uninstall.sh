#!/usr/bin/env bash
# Removes what install.sh added and puts Ubuntu's defaults back. The accent and dark style are left as they are.
set -euo pipefail

DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}"
MARK='ThatDataPurple for GNOME apps'

if gsettings list-schemas | grep -qx org.gnome.Ptyxis; then
    for uuid in $(gsettings get org.gnome.Ptyxis profile-uuids | sed 's/^@as //' | tr -d "[]',"); do
        path="org.gnome.Ptyxis.Profile:/org/gnome/Ptyxis/Profiles/$uuid/"
        [ "$(gsettings get "$path" palette)" = "'ThatDataPurple'" ] && gsettings reset "$path" palette
    done
fi
rm -f "$DATA/org.gnome.Ptyxis/palettes/ThatDataPurple.palette"

css="$CONFIG/gtk-4.0/gtk.css"
if [ -f "$css" ] && grep -q "$MARK" "$css"; then
    rm "$css"
    [ -f "$css.before-thatdatapurple" ] && mv "$css.before-thatdatapurple" "$css"
fi

uri="file://$DATA/backgrounds/ThatDataPurple.jpg"
for key in picture-uri picture-uri-dark; do
    [ "$(gsettings get org.gnome.desktop.background $key)" = "'$uri'" ] && gsettings reset org.gnome.desktop.background $key
done
[ "$(gsettings get org.gnome.desktop.screensaver picture-uri)" = "'$uri'" ] && gsettings reset org.gnome.desktop.screensaver picture-uri
rm -f "$DATA/backgrounds/ThatDataPurple.jpg"
echo "ThatDataPurple removed. Restart open apps to see the change."
