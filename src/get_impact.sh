#!/bin/bash
# Impact isn't redistributable, so it's not in the repo: fetch it from the
# Microsoft core fonts package and install it where the scripts look for it.
set -e
tmp=$(mktemp -d)
curl -sL -o "$tmp/impact32.exe" "https://downloads.sourceforge.net/corefonts/impact32.exe"
7z e -y -o"$tmp" "$tmp/impact32.exe" >/dev/null
mkdir -p ~/.local/share/fonts
cp "$tmp/Impact.TTF" ~/.local/share/fonts/
fc-cache -f ~/.local/share/fonts >/dev/null
rm -rf "$tmp"
echo "Impact installed in ~/.local/share/fonts/Impact.TTF"
