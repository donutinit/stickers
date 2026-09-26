"""Ironic tía cards: sweet good-morning aesthetics, rude messages."""
import os, sys
from PIL import Image, ImageDraw
import tias
from tias import GOLD, RAINBOW, SILVER, BLUE, bokeh, rays, spinner, floaters, fluttering
from deepfry import fry

here = os.path.dirname(os.path.abspath(__file__))
RMASK = Image.new("L", (512, 512)); ImageDraw.Draw(RMASK).rounded_rectangle([0, 0, 511, 511], 44, fill=255)

CONFIGS = [
    dict(out="ti_feliz_lunes", seed=11, fried=True, pony="FANMADE_Pinkie_Pie_vector_2", fit=("h", 490), pos=(60, 22),
         face=(0.45, 0.18, 0.83, 0.47),
         bg=((255, 235, 245), (255, 190, 220)), radial=True,
         decorate_bg=lambda bg: (rays(bg, (255, 240, 180), alpha=70, center=(256, 200)), bokeh(bg, [(255, 255, 255), (255, 180, 220)], 20, 11)),
         behind=[],
         corners=[("1f339", 96, (-10, 400), -15), ("1f490", 100, (415, 400), 12), ("1f64f", 70, (18, 150), 0)],
         front=[floaters(["1f496", "1f495"], 5, 12)],
         texts=[("Feliz Lunes", 84, GOLD, 300), ("Que Dios te Bendiga", 64, RAINBOW, 392)]),
    dict(out="ti_vete_alv", seed=12, pony="FANMADE_Fluttershy_Idle_Vector", fit=("h", 480), pos=(40, 10),
         face=(0.06, 0.13, 0.42, 0.40),
         bg=((255, 248, 220), (250, 200, 170)), radial=True,
         decorate_bg=lambda bg: (rays(bg, (255, 225, 140), alpha=70, center=(440, 70)), bokeh(bg, [(255, 255, 255), (255, 210, 150)], 18, 12)),
         behind=[spinner("2600", 96, (406, 16))],
         corners=[("1f339", 90, (-8, 408), -15), ("1f33b", 80, (425, 410), 10), ("1f337", 70, (455, 300), 12)],
         front=[fluttering("1f98b", 56, (330, 150)), floaters(["1f496"], 4, 13, y0=460, y1=260)],
         texts=[("Buenos Días", 80, GOLD, 300), ("vete alv", 92, [(255, 215, 0), (255, 255, 190), (255, 170, 20), (255, 215, 0)], 380)]),
    dict(out="ti_feliz_viernes", seed=13, pony="MLP_The_Movie_Applejack_official_artwork_2", fit=("h", 470), pos=(100, 20),
         face=(0.22, 0.10, 0.68, 0.40),
         bg=((230, 255, 220), (140, 210, 255)), radial=True,
         decorate_bg=lambda bg: bokeh(bg, [(255, 255, 255), (255, 240, 150)], 22, 13),
         behind=[],
         corners=[("1f389", 96, (8, 10), 8), ("1f388", 100, (20, 160), -8), ("1f389", 80, (420, 330), -12)],
         front=[floaters(["2b50", "1f31f"], 6, 14)],
         texts=[("Feliz Viernes", 80, RAINBOW, 300), ("de Desmadre", 84, BLUE, 388)]),
    dict(out="ti_gracias_dios", seed=15, pony="FANMADE_Fluttershy_Idle_Vector", fit=("h", 460), pos=(40, 14),
         face=(0.06, 0.13, 0.42, 0.40),
         bg=((255, 250, 225), (255, 215, 170)), radial=True,
         decorate_bg=lambda bg: (rays(bg, (255, 240, 170), alpha=80, center=(256, 60)), bokeh(bg, [(255, 255, 255), (255, 230, 160)], 20, 15)),
         behind=[],
         corners=[("1f64f", 84, (420, 170), 0), ("1f339", 90, (-8, 405), -15), ("1f490", 96, (418, 400), 12)],
         front=[fluttering("1f98b", 52, (400, 60)), floaters(["1f496", "2728"], 5, 16, y0=460, y1=260)],
         texts=[("Gracias a Dios", 80, GOLD, 296), ("Bendiciones", 70, RAINBOW, 376)]),
    dict(out="ti_ahorcar_rukas", seed=14, pony="MLP_The_Movie_Rarity_official_artwork", fit=("h", 440), pos=(40, 20),
         face=(0.18, 0.10, 0.55, 0.36),
         bg=((255, 240, 250), (230, 190, 255)), radial=True,
         decorate_bg=lambda bg: (rays(bg, (255, 235, 200), alpha=60, center=(256, 180)), bokeh(bg, [(255, 255, 255), (220, 180, 255)], 22, 14)),
         behind=[],
         corners=[("1f339", 92, (-8, 405), -15), ("1f490", 96, (418, 402), 12), ("1f48e", 60, (440, 40), 10), ("1f338", 64, (446, 190), -10)],
         front=[floaters(["1f496", "1f495"], 5, 15), fluttering("1f98b", 52, (400, 110))],
         texts=[("Feliz Viernes", 80, GOLD, 300), ("de ahorcar rukas", 76, RAINBOW, 388)]),
]

if __name__ == "__main__":
    which = sys.argv[1:]
    for cfg in CONFIGS:
        if which and cfg["out"] not in which:
            continue
        if cfg.get("fried"):  # fry the card, then lay the (clean, shimmering) text on top so it stays legible
            texts = cfg["texts"]
            frames, face = tias.build(dict(cfg, texts=[]))
            frames = [fry(f) for f in frames]
            for i, f in enumerate(frames):
                f.putalpha(RMASK)
                for txt, sz, st, y in texts:
                    im = tias.fancy_text(txt, sz, st, i / len(frames))
                    f.alpha_composite(im, ((512 - im.width) // 2, y))
        else:
            frames, face = tias.build(cfg)
        d = os.path.join(here, "tiframes", cfg["out"]); os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        for i, f in enumerate(frames):
            f.save(os.path.join(d, f"f{i:02d}.png"))
        open(os.path.join(d, "delays.txt"), "w").write(" ".join(["110"] * len(frames)))
        dbg = frames[0].copy(); ImageDraw.Draw(dbg).rectangle(face, outline="cyan", width=2)
        dbg.save(os.path.join(here, "tiframes", cfg["out"] + "_dbg.png"))
        print(cfg["out"], [int(v) for v in face])
