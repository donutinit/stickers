"""Swiss-style typographic stickers: flat colour, tight Inter, strict grid, vulgar copy."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

S = 512
M = 34  # margin / grid unit
here = os.path.dirname(os.path.abspath(__file__))

RED = (228, 0, 43)
BLACK = (18, 18, 18)
PAPER = (242, 239, 232)
KLEIN = (0, 47, 167)
YELLOW = (255, 214, 0)


def inter(size, weight, opsz=32):
    f = ImageFont.truetype(os.path.join(here, "fonts", "Inter.ttf"), size)
    f.set_variation_by_axes([opsz, weight])
    return f


def tracked_width(f, txt, track):
    return sum(f.getlength(c) for c in txt) + track * f.size * (len(txt) - 1)


def draw_tracked(d, xy, txt, f, fill, track):
    """Pillow has no letter-spacing: place glyphs one by one with a (negative) tracking."""
    x, y = xy
    for i, c in enumerate(txt):
        # kerning-aware advance: width of the pair minus width of the next glyph
        nxt = txt[i + 1] if i + 1 < len(txt) else ""
        adv = f.getlength(c + nxt) - f.getlength(nxt) if nxt else f.getlength(c)
        d.text((x, y), c, font=f, fill=fill, anchor="ls")
        x += adv + track * f.size


def wrap(txt, f, track, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if tracked_width(f, cand, track) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def card(no, phrase, gloss, bg, fg, accent=None, weight=800, track=-0.045):
    im = Image.new("RGBA", (S, S))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, S - 1, S - 1], 28, fill=bg + (255,))
    accent = accent or fg
    # header row: index left, category right, hairline under it
    small = inter(20, 500, 14)
    d.text((M, M), f"Nº {no:02d}", font=small, fill=accent, anchor="lt")
    d.text((S - M, M), "declaración", font=small, fill=fg, anchor="rt")
    d.line([(M, M + 34), (S - M, M + 34)], fill=fg, width=2)
    # the phrase: as large as fits in the grid, flush-left, ragged right, tight leading
    top, bottom = M + 60, S - M - 70
    size = 190
    while True:
        f = inter(size, weight)
        lines = wrap(phrase, f, track, S - 2 * M)
        lead = size * 0.92
        if all(tracked_width(f, l, track) <= S - 2 * M for l in lines) and lead * len(lines) <= bottom - top:
            break
        size -= 4
    y = top + size * 0.78
    for l in lines:
        draw_tracked(d, (M - size * 0.04, y), l, f, fg, track)
        y += lead
    # footer: hairline + gloss like a dictionary entry
    d.line([(M, S - M - 40), (S - M, S - M - 40)], fill=fg, width=2)
    d.text((M, S - M - 8), gloss, font=inter(19, 450, 14), fill=fg, anchor="ls")
    d.text((S - M, S - M - 8), "2026", font=inter(19, 450, 14), fill=accent, anchor="rs")
    return im


CARDS = [
    (1, "me vale verga.", "loc. adv. — indiferencia total", RED, PAPER),
    (2, "vete alv.", "loc. verb. — despedida cordial", PAPER, BLACK, RED),
    (3, "nel.", "adv. — negación rotunda", BLACK, PAPER, YELLOW),
    (4, "no mames.", "interj. — asombro, incredulidad", KLEIN, PAPER),
    (5, "me turbo vale pito.", "loc. — indiferencia acelerada", YELLOW, BLACK),
    (6, "que te valga verga.", "loc. — consejo de vida", PAPER, KLEIN),
    (7, "no autorizo.", "fórm. — trámite denegado", RED, PAPER),
    (8, "ya voy.", "loc. — mentira piadosa", BLACK, PAPER, RED),
    (9, "te amo.", "loc. — declaración, sin garantía", PAPER, RED),
    (10, "oki doki.", "interj. — conformidad", KLEIN, YELLOW),
    (11, "ni en su casa lo conocen.", "loc. — irrelevancia certificada", PAPER, BLACK, RED),
    (12, "no tengo nada en contra tu punto, pero me estás hablando como si me aguantaras un vergazo.", "loc. — diplomacia mexicana", BLACK, PAPER, RED),
    (13, "intrínseco.", "adj. — palabra para ganar discusiones", PAPER, BLACK, KLEIN),
    (14, "es broma. pero si quieres no es broma.", "loc. — cláusula de salida", RED, PAPER),
]

if __name__ == "__main__":
    out = os.path.join(here, "minframes"); os.makedirs(out, exist_ok=True)
    for no, phrase, gloss, bg, fg, *acc in CARDS:
        name = f"min_{no:02d}"
        if len(sys.argv) > 1 and name not in sys.argv[1:]:
            continue
        card(no, phrase, gloss, bg, fg, *acc).save(os.path.join(out, name + ".png"))
        print(name, phrase)
