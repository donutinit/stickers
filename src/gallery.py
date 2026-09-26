"""Regenerate the pack gallery in README.md from packs/ so every sticker is listed.

    python src/gallery.py          # rewrite the "## Paquetes" section
    python src/gallery.py --check  # exit 1 if README is missing a sticker or lists one that no longer exists
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# display order and titles; a new pack folder not listed here still shows up (at the end, titled by its folder name)
TITLES = {
    "respuestas": "Respuestas (fijos)",
    "arte": "Arte clásico (fijos)",
    "minimal": "Minimal (fijos)",
    "black-metal": "Black metal (fijos)",
    "moai-estatico": "Moai (fijos)",
    "ponis-animados": "Ponis (animados)",
    "tias": "Tías (animados)",
    "buchones": "Buchones (animados)",
    "kratos": "Kratos cute (animados)",
    "moai-animado": "Moai (animados)",
}


def packs():
    found = sorted(d for d in os.listdir(os.path.join(ROOT, "packs")) if os.path.isdir(os.path.join(ROOT, "packs", d)))
    return [p for p in TITLES if p in found] + [p for p in found if p not in TITLES]


def section():
    out = ["## Paquetes\n"]
    for p in packs():
        fs = sorted(f for f in os.listdir(os.path.join(ROOT, "packs", p)) if f.endswith(".webp"))
        imgs = " ".join(f'<img src="packs/{p}/{f}" width="128" title="{f[:-5]}">' for f in fs)
        out.append(f"### {TITLES.get(p, p)} — `packs/{p}` ({len(fs)})\n\n{imgs}\n")
    return "\n".join(out) + "\n"


def main():
    path = os.path.join(ROOT, "README.md")
    s = open(path).read()
    a, b = s.index("## Paquetes\n"), s.index("## Regenerarlos")
    if "--check" in sys.argv:
        listed = set(re.findall(r'src="(packs/[^"]+\.webp)"', s[a:b]))
        on_disk = {f"packs/{p}/{f}" for p in packs() for f in os.listdir(os.path.join(ROOT, "packs", p)) if f.endswith(".webp")}
        missing, stale = sorted(on_disk - listed), sorted(listed - on_disk)
        for f in missing:
            print("falta en README:", f)
        for f in stale:
            print("en README pero no existe:", f)
        sys.exit(1 if missing or stale else 0)
    open(path, "w").write(s[:a] + section() + s[b:])
    total = sum(len([f for f in os.listdir(os.path.join(ROOT, "packs", p)) if f.endswith(".webp")]) for p in packs())
    print(f"README: {total} stickers en {len(packs())} paquetes")


if __name__ == "__main__":
    main()
