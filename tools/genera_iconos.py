#!/usr/bin/env python3
"""Genera los iconos del sitio y la imagen de las tarjetas sociales.

Club Balonmano Barbate — web oficial
Desarrollo: Francisco Vidal Mateo (FranVi)

No forma parte del despliegue. Se lanza a mano cuando cambia el escudo o la
foto elegida para la tarjeta social:

    python -m pip install Pillow fonttools brotli
    python tools/genera_iconos.py

Escribe (todo bajo assets/img/, más el favicon.ico de la raíz, que los
navegadores y los rastreadores piden a pelo aunque no esté enlazado):

    favicon.ico                  16 · 32 · 48 px
    assets/img/apple-touch-icon.png       180 px, fondo navy (iOS no respeta
                                          la transparencia y la deja en negro)
    assets/img/icono-192.png              PWA / Android
    assets/img/icono-512.png              PWA / Android
    assets/img/og-club-balonmano-barbate.jpg   1200 x 630, tarjeta social

La tarjeta social sigue la dirección ALMADRABA: manda la foto, encima un velo
de navy en degradado desde la izquierda, y sobre él el escudo y el nombre en
la serif del sitio. Nada de cajas.
"""

import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

RAIZ = Path(__file__).resolve().parent.parent
IMG = RAIZ / "assets" / "img"
FUENTES = RAIZ / "assets" / "fonts"

ESCUDO = IMG / "escudo-club-balonmano-barbate.webp"
FOTO_OG = IMG / "aficion-y-equipo-del-club-balonmano-barbate-celebrando-en-el.webp"

# Tokens de la dirección ALMADRABA (assets/css/styles.css, :root).
NAVY_DEEP = (0x0A, 0x2A, 0x43)
GOLD_LIGHT = (0xF0, 0xC8, 0x68)
SAND = (0xF6, 0xF1, 0xE4)


def carga_escudo() -> Image.Image:
    if not ESCUDO.exists():
        sys.exit(f"Falta el escudo: {ESCUDO}")
    return Image.open(ESCUDO).convert("RGBA")


def sobre_fondo(escudo: Image.Image, lado: int, fondo, margen: float = 0.12) -> Image.Image:
    """El escudo centrado sobre un cuadrado opaco, con aire alrededor."""
    lienzo = Image.new("RGBA", (lado, lado), fondo)
    util = int(lado * (1 - 2 * margen))
    pieza = escudo.copy()
    pieza.thumbnail((util, util), Image.LANCZOS)
    lienzo.alpha_composite(pieza, ((lado - pieza.width) // 2, (lado - pieza.height) // 2))
    return lienzo


def fuente_serif(tam: int) -> ImageFont.FreeTypeFont:
    """Source Serif 4 del propio sitio. El .woff2 se pasa a TTF en memoria:
    Pillow no lee woff2, pero fontTools sí lo descomprime."""
    origen = FUENTES / "source-serif-4-normal-latin.woff2"
    if not origen.exists():
        sys.exit(f"Falta la fuente: {origen}")
    tt = TTFont(str(origen))
    buf = io.BytesIO()
    tt.flavor = None          # quita la compresión woff2
    tt.save(buf)
    buf.seek(0)
    fuente = ImageFont.truetype(buf, tam)
    # Es una fuente variable: sin fijar el eje sale en Regular y el rótulo
    # queda blando sobre la foto.
    try:
        fuente.set_variation_by_axes([700])
    except Exception:
        pass
    return fuente


def fuente_mono(tam: int) -> ImageFont.FreeTypeFont:
    origen = FUENTES / "jetbrains-mono-normal-latin.woff2"
    tt = TTFont(str(origen))
    buf = io.BytesIO()
    tt.flavor = None
    tt.save(buf)
    buf.seek(0)
    return ImageFont.truetype(buf, tam)


def genera_favicons(escudo: Image.Image) -> None:
    # .ico multirresolución. Va en la raíz: es la ruta que el navegador pide
    # por su cuenta cuando el <link> no le vale (y la que usan los rastreadores).
    sobre_fondo(escudo, 256, SAND + (255,), margen=0.06).convert("RGB").save(
        RAIZ / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    print("favicon.ico")

    # iOS recorta el icono y pinta de negro lo transparente: fondo navy sí o sí.
    sobre_fondo(escudo, 180, NAVY_DEEP + (255,), margen=0.10).convert("RGB").save(
        IMG / "apple-touch-icon.png"
    )
    print("assets/img/apple-touch-icon.png")

    for lado in (192, 512):
        # Margen ancho para que el recorte "maskable" de Android no coma el escudo.
        sobre_fondo(escudo, lado, NAVY_DEEP + (255,), margen=0.18).convert("RGB").save(
            IMG / f"icono-{lado}.png"
        )
        print(f"assets/img/icono-{lado}.png")


def genera_og(escudo: Image.Image) -> None:
    if not FOTO_OG.exists():
        sys.exit(f"Falta la foto de la tarjeta: {FOTO_OG}")

    W, H = 1200, 630
    foto = Image.open(FOTO_OG).convert("RGB")

    # Recorte centrado a 1200x630 sin deformar.
    escala = max(W / foto.width, H / foto.height)
    foto = foto.resize((round(foto.width * escala), round(foto.height * escala)), Image.LANCZOS)
    foto = foto.crop((
        (foto.width - W) // 2,
        max(0, (foto.height - H) // 3),      # un tercio: deja arriba las caras
        (foto.width - W) // 2 + W,
        max(0, (foto.height - H) // 3) + H,
    ))
    lienzo = foto.convert("RGBA")

    # Velo de navy en degradado desde la izquierda: el mismo recurso que usa
    # .banda-foto::before para que el texto se lea sobre cualquier foto.
    velo = Image.new("RGBA", (W, H), NAVY_DEEP + (0,))
    pincel = ImageDraw.Draw(velo)
    for x in range(W):
        t = x / W
        alfa = int(238 * (1 - t) ** 1.35 + 40)      # 238 a la izquierda, 40 al borde
        pincel.line([(x, 0), (x, H)], fill=NAVY_DEEP + (min(alfa, 250),))
    lienzo.alpha_composite(velo)

    # Un filete de oro arriba, como el resto del sitio.
    ImageDraw.Draw(lienzo).rectangle([0, 0, W, 6], fill=GOLD_LIGHT + (255,))

    margen_x, cursor_y = 74, 128

    marca = escudo.copy()
    marca.thumbnail((132, 132), Image.LANCZOS)
    lienzo.alpha_composite(marca, (margen_x, cursor_y))
    cursor_y += marca.height + 46

    pincel = ImageDraw.Draw(lienzo)
    pincel.text((margen_x, cursor_y), "DESDE 1997 · BARBATE, CÁDIZ",
                font=fuente_mono(19), fill=GOLD_LIGHT + (255,))
    cursor_y += 46

    serif = fuente_serif(76)
    for linea in ("Club Balonmano", "Barbate"):
        pincel.text((margen_x, cursor_y), linea, font=serif, fill=SAND + (255,))
        cursor_y += 84

    cursor_y += 16
    pincel.text((margen_x, cursor_y), "Balonmano pista y balonmano playa",
                font=fuente_mono(21), fill=SAND + (216,))

    destino = IMG / "og-club-balonmano-barbate.jpg"
    lienzo.convert("RGB").save(destino, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"assets/img/og-club-balonmano-barbate.jpg  ({destino.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    escudo = carga_escudo()
    genera_favicons(escudo)
    genera_og(escudo)
