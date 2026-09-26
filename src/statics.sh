#!/bin/bash
# The first two stickers (Pinkie OKI DOKI!, Fluttershy VETE ALV) were plain ImageMagick one-offs.
set -e
cd "$(dirname "$0")"
F=~/.local/share/fonts/Impact.TTF
mkdir -p out
meme() {  # meme <src.png> <text> <pointsize> <out.webp>
  magick "$1" -trim +repage -resize x512 -gravity center -background none -extent 512x512 \
    -font "$F" -pointsize "$3" -gravity south \
    -stroke black -strokewidth 14 -fill black -annotate +0+14 "$2" \
    -stroke none -fill white -annotate +0+14 "$2" out/tmp.png
  cwebp -quiet -q 80 out/tmp.png -o "$4" && rm out/tmp.png
}
meme Pinkie_Pie_high_resolution_from_HubWorld.png "OKI DOKI!" 110 out/pinkie_oki_doki.webp
meme FANMADE_Fluttershy_Idle_Vector.png "VETE ALV" 120 out/fluttershy_vete_alv.webp
