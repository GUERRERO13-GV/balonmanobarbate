# -*- coding: utf-8 -*-
"""Reescribe el sumario de torneos de equipos.html a partir de tools/torneos.py.

    python tools/genera_torneos.py

Jerarquia: sexo -> categoria -> torneo. El visitante busca primero a su equipo
y solo despues elige en cual de sus torneos mirar la clasificacion. Con ciento
y pico torneos, escribir esto a mano en el HTML no es sostenible: se edita
tools/torneos.py y se vuelve a lanzar este script.

Club Balonmano Barbate — Francisco Vidal Mateo (FranVi)
"""
import html, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from torneos import FILAS

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEXOS = [("M", "Masculino"), ("F", "Femenino")]
ORDEN_CAT = ["Sénior", "Juvenil", "Cadete", "Infantil", "Alevín", "Benjamín"]
TEMPS = {"2024/25": "2425", "2025/26": "2526", "2026/27": "2627",
         "2025": "2425", "2026": "2526"}
EMBED = ("https://resultadosbalonmano.isquad.es/competicion.php?embed=1"
         "&id_categoria={cat}&id_competicion={comp}&id={grupo}&id_temp={temp}"
         "&id_territorial={terr}&id_ambito=0&id_superficie={surf}&seleccion=0"
         "&embed_menus=Y2xhc2lmaWNhY2lvbnx8Y2FsZW5kYXJpbw%3D%3D")

RANGO = [("Campeonato de España", 0), ("Campeonato de Andalucía", 1),
         ("Arena 1000", 2), ("Arena Sur · Barbate", 3), ("Arena Sur", 4),
         ("Diego Carrasco", 5), ("Circuito Arenas del Sur", 6)]

def peso_torneo(f):
    """Lo mas reciente primero, mezclando pista y playa: la temporada de playa
    de 2026 es posterior a la de pista 2025/26. Dentro del mismo anyo, pista
    antes que playa y, en playa, por peso del torneo: el Campeonato de España
    manda sobre el de Andalucia, y este sobre los circuitos."""""
    torneo, temporada, surf = f[2], f[5], f[6]
    anyo = -int(temporada[:4])
    rango = 0 if surf == "1" else next((r for pref, r in RANGO if torneo.startswith(pref)), 9)
    return (anyo, int(surf), rango, torneo)

def esc(t):
    return html.escape(t, quote=True)

def bloque():
    out = ['    <div class="comp-grupos">']
    for cod, sexo in SEXOS:
        out.append('      <div class="comp-sexo">')
        out.append('        <h3>%s</h3>' % sexo)
        cats = [c for c in ORDEN_CAT if any(f[0] == cod and f[1] == c for f in FILAS)]
        cats += sorted({f[1] for f in FILAS if f[0] == cod} - set(cats))
        for cat in cats:
            fs = sorted([f for f in FILAS if f[0] == cod and f[1] == cat], key=peso_torneo)
            out.append('        <details class="comp-categoria">')
            out.append('          <summary><h4>%s <span>%d %s</span></h4></summary>'
                       % (esc(cat), len(fs), "torneo" if len(fs) == 1 else "torneos"))
            out.append('          <ul class="comp-lista">')
            for (sx, ct, torneo, equipo, fase, temporada, surf, terr, idcat, idcomp, idgr) in fs:
                disciplina = "Pista" if surf == "1" else "Playa"
                detalle = "%s %s · %s · %s" % (disciplina, temporada, equipo, fase)
                nombre = "%s %s · %s — %s" % (sexo, ct, torneo, equipo)
                src = EMBED.format(cat=idcat, comp=idcomp, grupo=idgr,
                                   temp=TEMPS.get(temporada, "2526"), terr=terr, surf=surf)
                out.append('            <li>')
                out.append('              <div>')
                out.append('                <p class="comp-torneo">%s</p>' % esc(torneo))
                out.append('                <span class="comp-detalle">%s</span>' % esc(detalle))
                out.append('              </div>')
                out.append('              <button class="comp-ver" type="button" data-nombre="%s" data-src="%s">Ver clasificación</button>'
                           % (esc(nombre), esc(src)))
                out.append('            </li>')
            out.append('          </ul>')
            out.append('        </details>')
        out.append('      </div>')
    out.append('    </div>')
    return "\n".join(out)

def inserta(b):
    """Sustituye en equipos.html lo que hay entre el aviso y #tabla-federacion."""
    p = os.path.join(RAIZ, "equipos.html")
    s = io.open(p, encoding="utf-8").read()
    ini = s.index('    <div class="comp-grupos">')
    fin = s.index('    <div id="tabla-federacion">')
    fuera = s[ini:fin].count("\n")
    io.open(p, "w", encoding="utf-8", newline="").write(s[:ini] + b + "\n\n" + s[fin:])
    return fuera


if __name__ == "__main__":
    b = bloque()
    fuera = inserta(b)
    print("equipos.html: %d lineas fuera, %d dentro · %d torneos en %d fichas"
          % (fuera, b.count(chr(10)) + 1, b.count("comp-ver"),
             len({(f[0], f[1]) for f in FILAS})))
