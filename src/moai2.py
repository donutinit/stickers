"""Moai gigachad edit: cuts, pans, dolly zoom, tilt, vine boom."""
import os
from moai_common import *

ease = lambda t: t * t * (3 - 2 * t)
frames, delays = [], []


def add(f, d):
    frames.append(f); delays.append(d)


# 1) pan left -> right across the face, whip in
for i in range(6):
    t = ease(i / 5)
    add(shot(1.7, 0.30 + 0.42 * t, 0.42, blur=18 if i == 0 else 6 if i == 1 else 0), 80)
# 2) dolly zoom: moai pushes in while the background pulls back
for i in range(6):
    t = ease(i / 5)
    add(shot(1.0 + 0.35 * t, 0.55, 0.5, bg_zoom=1.6 - 0.55 * t, sweep=-0.2 + 1.6 * t), 90)
# 3) extreme close-up on the eye, fast zoom + dutch tilt
for i in range(4):
    t = i / 3
    add(shot(2.6 + 0.6 * t, 0.58, 0.27, rot=-8 + 4 * t), 70)
# 4) tilt up from the jaw to the brow
for i in range(5):
    t = ease(i / 4)
    add(shot(1.6, 0.58, 0.78 - 0.45 * t, blur=0), 80)
# 5) vine boom
for z, sh, fl in ((1.35, (14, -10), 0.6), (1.3, (-9, 7), 0.25), (1.32, (5, -4), 0.08), (1.3, (0, 0), 0)):
    add(shot(z, 0.6, 0.4, shake=sh, flash=fl), 70)
delays[-1] = 900

d = os.path.join(here, "moai2frames"); os.makedirs(d, exist_ok=True)
for f in os.listdir(d):
    os.remove(os.path.join(d, f))
for i, f in enumerate(frames):
    f.save(os.path.join(d, f"f{i:02d}.png"))
open(os.path.join(d, "delays.txt"), "w").write(" ".join(map(str, delays)))
print(len(frames), sum(delays))
