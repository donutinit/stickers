#!/bin/bash
# encode.sh <frames_dir> <out.webp> [q] — per-frame delays from delays.txt, every frame a keyframe
dir=$1; out=$2; q=${3:-60}
read -a D < "$dir/delays.txt"
args=(); i=0
for f in "$dir"/f*.png; do args+=(-d "${D[$i]}" "$f"); i=$((i+1)); done
img2webp -loop 0 -m 4 -kmin 0 -kmax 1 -lossy -q "$q" "${args[@]}" -o "$out" 2>&1 | tail -1
