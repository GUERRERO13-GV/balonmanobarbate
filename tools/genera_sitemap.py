#!/usr/bin/env python3
"""Reescribe sitemap.xml con la fecha real de cada página.

Club Balonmano Barbate — web oficial
Desarrollo: Francisco Vidal Mateo (FranVi)

    python tools/genera_sitemap.py

El <lastmod> sale de la fecha del último commit que tocó cada archivo, no de
la fecha de hoy: si se pone hoy en todas, Google aprende que el dato miente y
deja de hacerle caso. Las páginas que aún no están en git (recién creadas)
caen a su fecha de modificación en disco.

Se lanza también desde .github/workflows/resultados.yml, porque la pasada
semanal de la federación reescribe index.html y equipos.html y su fecha tiene
que moverse con ellas.

Solo biblioteca estándar: el runner de la Action no instala nada.
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://balonmanobarbate.vercel.app"

# Solo las páginas indexables. 404.html va con noindex y no entra en el
# sitemap; el resto del sitio no tiene más rutas públicas.
PAGINAS = [
    ("index.html",          "/",                    "weekly",  "1.0"),
    ("equipos.html",        "/equipos.html",        "weekly",  "0.9"),
    ("club.html",           "/club.html",           "monthly", "0.8"),
    ("galeria.html",        "/galeria.html",        "monthly", "0.7"),
    ("patrocinadores.html", "/patrocinadores.html", "monthly", "0.7"),
    ("equipaciones.html",   "/equipaciones.html",   "yearly",  "0.7"),
    ("contacto.html",       "/contacto.html",       "yearly",  "0.6"),
]


def fecha(archivo: str) -> str:
    """Fecha del último commit que tocó el archivo, en formato ISO."""
    try:
        salida = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", archivo],
            cwd=RAIZ, capture_output=True, text=True, timeout=20,
        )
        marca = salida.stdout.strip()
        if marca:
            return marca
    except (OSError, subprocess.SubprocessError):
        pass
    # Sin git o sin historial: la fecha del archivo en disco.
    sello = (RAIZ / archivo).stat().st_mtime
    return datetime.fromtimestamp(sello, timezone.utc).strftime("%Y-%m-%d")


def main() -> int:
    filas = []
    for archivo, ruta, frecuencia, prioridad in PAGINAS:
        if not (RAIZ / archivo).exists():
            print(f"aviso: falta {archivo}, se salta", file=sys.stderr)
            continue
        filas.append(
            "  <url>\n"
            f"    <loc>{BASE}{ruta}</loc>\n"
            f"    <lastmod>{fecha(archivo)}</lastmod>\n"
            f"    <changefreq>{frecuencia}</changefreq>\n"
            f"    <priority>{prioridad}</priority>\n"
            "  </url>"
        )

    if not filas:
        print("error: ninguna página que publicar", file=sys.stderr)
        return 1

    nuevo = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!-- Generado por tools/genera_sitemap.py: no se edita a mano. -->\n"
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(filas)
        + "\n</urlset>\n"
    )

    destino = RAIZ / "sitemap.xml"
    # Si nada ha cambiado no se reescribe: así la Action semanal no genera un
    # commit cuyo único contenido sea una marca de tiempo nueva.
    if destino.exists() and destino.read_text(encoding="utf-8") == nuevo:
        print("sitemap.xml sin cambios")
        return 0

    destino.write_text(nuevo, encoding="utf-8")
    print(f"sitemap.xml reescrito con {len(filas)} páginas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
