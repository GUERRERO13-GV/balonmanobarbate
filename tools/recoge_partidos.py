# -*- coding: utf-8 -*-
"""Recoge de iSquad los partidos, resultados y clasificaciones del club.

    python tools/recoge_partidos.py

Escribe datos/deportivo.json, que es de donde tira genera_partidos.py. Lo lanza
la GitHub Action cada domingo por la noche; a mano solo hace falta para probar.

Solo barre la temporada en curso de cada superficie (ver filas_activas() en
tools/torneos.py): la historia de temporadas cerradas ya no cambia.

Guardarrailes, porque de esto depende que la web no se rompa sola:

  - Si un grupo no se puede descargar, se conserva lo que ya habia en el JSON
    anterior. Nunca se escribe un hueco.
  - Si la pasada saliera con menos grupos con datos que la anterior, el script
    NO escribe nada y termina con codigo 1. Preferimos publicar los datos de la
    semana pasada a publicar una web vacia porque iSquad estuviera caido.

No guarda ningun dato personal: de la plantilla solo sale cuantos jugadores hay
inscritos. Ver la nota de tools/isquad.py.

Club Balonmano Barbate — Francisco Vidal Mateo (FranVi)
"""
import datetime
import io
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import isquad                                    # noqa: E402
from torneos import filas_activas                # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")     # la consola de Windows si no revienta
except Exception:                                # noqa: BLE001
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "datos", "deportivo.json")
PAUSA = 0.4                                      # cortesia con el servidor de la federacion


def clave(f):
    return "%s-%s-%s" % (f[0], f[1], f[10])


def previo():
    try:
        with io.open(DESTINO, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:                            # noqa: BLE001 - la primera vez no existe
        return {"equipos": []}


def con_datos(equipos):
    return sum(1 for e in equipos if e.get("partidos"))


def ahora():
    try:
        from zoneinfo import ZoneInfo
        t = datetime.datetime.now(ZoneInfo("Europe/Madrid"))
    except Exception:                            # noqa: BLE001 - sin tzdata, UTC
        t = datetime.datetime.now(datetime.timezone.utc)
    return t.replace(microsecond=0).isoformat()


def recoge():
    anterior = previo()
    antes = {e["clave"]: e for e in anterior.get("equipos", [])}
    filas = filas_activas()
    equipos, fallos = [], []
    print("%d grupos activos" % len(filas))

    for n, f in enumerate(filas, 1):
        k = clave(f)
        etiqueta = "%s %s · %s (%s)" % (f[0], f[1], f[2], f[5])
        try:
            partidos = isquad.calendario(f)
            clasificacion = isquad.clasificacion(f)
            id_equipo = next((p["id_equipo_club"] for p in partidos if p["id_equipo_club"]), None)
            plantilla = isquad.plantilla(f, id_equipo) if id_equipo else None
        except isquad.ErrorRed as e:
            fallos.append(k)
            print("  [%d/%d] FALLO %s -> %s" % (n, len(filas), etiqueta, e))
            if k in antes:
                equipos.append(antes[k])         # se conserva lo de la semana pasada
            continue

        jugados = sum(1 for p in partidos if p["goles_club"] is not None)
        print("  [%d/%d] %s: %d partidos (%d jugados)%s"
              % (n, len(filas), etiqueta, len(partidos), jugados,
                 "" if clasificacion else "  sin clasificacion"))
        equipos.append({
            "clave": k,
            "sexo": f[0],
            "categoria": f[1],
            "torneo": f[2],
            "nombre_federado": f[3],
            "fase": f[4],
            "temporada": f[5],
            "superficie": f[6],
            "grupo": f[10],
            "clasificacion": clasificacion,
            "plantilla": plantilla,
            "partidos": partidos,
        })
        time.sleep(PAUSA)

    equipos.sort(key=lambda e: e["clave"])
    return equipos, fallos, len(filas) - len(fallos), anterior


def main():
    equipos, fallos, refrescados, anterior = recoge()
    ahora_con = con_datos(equipos)
    tenia = con_datos(anterior.get("equipos", []))
    print("\ngrupos con datos: %d (antes %d) · refrescados: %d · fallos: %d"
          % (ahora_con, tenia, refrescados, len(fallos)))

    # Ni un grupo pudo leerse: la federación está caída o ha cambiado su HTML.
    # Escribir ahora solo serviría para sellar la página con una fecha de hoy y
    # los datos de la semana pasada, que es mentir al visitante.
    if not refrescados:
        print("ABORTA: no se ha podido leer NI UN grupo. No se escribe nada.")
        return 1

    if tenia and ahora_con < tenia:
        print("ABORTA: se han perdido %d grupos respecto al JSON anterior. "
              "No se escribe nada." % (tenia - ahora_con))
        return 1

    # Si el deporte no ha cambiado, no se toca el archivo: así no hay un commit
    # semanal vacío cuyo único contenido sea una marca de tiempo nueva. Los
    # fallos entran en la comparación: si la semana pasada se quedó un grupo sin
    # leer y esta ya se leyó, eso sí es una novedad aunque el marcador sea igual.
    if equipos == anterior.get("equipos") and fallos == anterior.get("fallos"):
        print("sin novedades: la federación no ha movido nada. No se reescribe.")
        return 0

    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with io.open(DESTINO, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"actualizado": ahora(), "fallos": fallos, "equipos": equipos},
                  fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    partidos = sum(len(e["partidos"]) for e in equipos)
    print("escrito %s · %d equipos · %d partidos"
          % (os.path.relpath(DESTINO, RAIZ), len(equipos), partidos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
