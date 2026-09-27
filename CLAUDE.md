# stickers

Stickers de WhatsApp para el dueño del repo (español mexicano, humor irónico y grosero, memes). Repo público: https://github.com/donutinit/stickers. `AGENTS.md` es un hardlink de este archivo: edita cualquiera de los dos, son el mismo.

## Reglas del dueño (no negociables)

- **Todos los stickers van en el README.** Cada `.webp` de `packs/` tiene que aparecer en la galería. Después de agregar, quitar o renombrar cualquier sticker: `~/ml/envs/rembg/bin/python src/gallery.py` y luego `--check` (debe salir sin errores). Nunca edites la galería a mano.
- **Todo sticker nuevo termina en `packs/`, con commit y push.** Mensaje de commit en español, corto, diciendo qué stickers se agregaron o cambiaron.
- **Créditos:** toda imagen, foto, emoji o fuente nueva se anota en `CREDITS.md` con fuente, autor y licencia. Prefiere dominio público o CC0; CC BY/BY-SA solo con crédito (BY-SA hace que el sticker derivado sea BY-SA). Impact no se versiona (`src/get_impact.sh`).
- **No borres stickers anteriores** cuando pida "otro estilo" o "una versión así": agrega, no reemplaces, salvo que lo pida explícitamente.
- **Cambio puntual = solo ese cambio.** "El mismo pero con X" significa no tocar nada más (ni animación, ni posición, ni efectos).
- **Nada tapa la cara** del personaje: textos, emojis, brillitos y corazones van a los lados o abajo.
- **El texto se tiene que leer** a tamaño de sticker: letras grandes, contorno, halo detrás si el fondo es ruidoso; frases largas en 2–3 renglones. Cuidado con letras góticas: en UnifrakturMaguntia la k/d/V son ilegibles (la V parece B); usa New Rocker.
- Revisa cada sticker viéndolo (contact sheet de un par de frames sobre fondo claro `#efeae2` y oscuro `#0b141a`) antes de darlo por bueno.

## Límites de WhatsApp

- 512×512 WebP. Fijos < 100 KB. Animados < 500 KB y ≤ 10 s.
- Animados: siempre con `src/encode.sh` (`img2webp -kmin 0 -kmax 1`, todos los frames completos). Sin eso WhatsApp pinta líneas negras.
- `img2webp` junta frames idénticos en uno largo y WhatsApp los recorta: para pausas largas usa frames de ≤ 750 ms con una diferencia mínima (p. ej. bob de 2 px).
- Si se pasa de 500 KB: primero menos frames o desenfocar un poco el fondo fotográfico; bajar la calidad es lo último. Los transparentes con glow pesan el doble que los de fondo opaco.
- Un paquete no mezcla fijos y animados; cada carpeta de `packs/` lleva su `tray.png` de 96×96.

## Entorno (lizeth)

- Python: `~/ml/envs/rembg/bin/python` (pillow, numpy, scipy, rembg). No hay venv propio; ver `~/ml/README.md`.
- Correr los scripts **desde `src/`** (usan rutas relativas y se importan entre sí).
- Sistema: `cwebp`, `img2webp`, `webpmux` (libwebp-tools), `magick`, `gh`. Impact en `~/.local/share/fonts/Impact.TTF`.
- rembg: modelos `isnet-general-use` (general) y `u2net_human_seg` (personas, cuando el general deja fondo). Limpia islas sueltas con `scipy.ndimage.label`; objetos pegados al sujeto se quitan por color.
- Fotos reales: Wikimedia Commons (Unsplash bloquea bots y su API pide clave). La API a veces responde vacío por rate limit: reintentar con backoff y User-Agent propio.
- **WhatsApp desde lizeth:** los stickers de prueba se mandan a "📝REELS CAPTIONS" con `wacli-send sticker reels packs/<pack>/<x>.webp`. `wacli` a secas es de solo lectura; ver la skill `wacli`.

## Estructura

- `packs/<paquete>/*.webp` — stickers finales (lo único que se publica en la galería).
- `src/*.py` — un script por familia; cada uno escribe frames en `src/<algo>frames/<nombre>/f00.png…` + `delays.txt` (ms por frame). Esas carpetas están en `.gitignore`.
- `src/encode.sh <frames_dir> <out.webp> [q]` — animado. Fijos: `cwebp -q 75-85 in.png -o out.webp`.
- `src/gallery.py` — regenera/verifica la galería del README.
- Assets: `src/pp`, `src/rd`, `src/m6`, `src/kit` (ponis, fandom wiki), `src/kratos` (+ `cut/` sin fondo), `src/arte`, `src/bm` (Commons), `src/fotos` (fotos reales + `*_cut.png`), `src/emoji` (Twemoji PNG 150 px), `src/fonts`.
- Módulos compartidos: `m6.py` (texto meme `meme_text`/`meme_block`, `grad_text`, `emoji`, `sparkle`, `rounded`), `tias.py` (`build` de tarjeta de tía con chequeo de cara), `kratos.py` (`head`, `cute`), `semana.py` (`photo`, `cut`, `glow_behind`, `cursive`), `blackmetal.py` (`grim`, `spiky_logo`), `buchon.py` (`base_frames`), `moai_common.py` (capas del moai + `shot`).
- Ojo: `moai.py` se ejecuta al importarse (regenera `moaiframes/`).

## Estilos que ya existen (para "hazlo en todos los estilos")

fijos (meme Impact blanco), arte (Goya/Doré con marco y placa solo con título), minimal (Inter suizo, Nº consecutivo + definición de diccionario), black metal (grabados/fotos oscuras, logo New Rocker con espinas hacia arriba + emoji tierno), moai fijo, ponis animados, tías (cursiva Pacifico, flores, brillitos), buchones (greca dorada, gótica de oro, billetes), Kratos cute (cabeza sin fondo, moño, Pacifico), Kratos Chayanne (fotos reales de flores/cielos, Fredoka), moai animado (gigachad + vine boom). `voluntad.py` y `valgo.py` son la plantilla para sacar una frase en todos.
