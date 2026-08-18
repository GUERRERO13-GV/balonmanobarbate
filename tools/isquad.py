# -*- coding: utf-8 -*-
"""Lectura de la plataforma de la federacion (iSquad).

Aqui vive todo lo que habla con iSquad: la descarga, la limpieza del HTML y el
parseo de calendario, clasificacion y plantilla. Lo usan barre_isquad.py y
recoge_partidos.py.

CRITICO: el club se identifica SIEMPRE por el escudo (afiliacion_clubs/100165),
nunca por el nombre. En Barbate hay otro club (100186) con nombres casi
identicos y comparten grupo en algunas competiciones.

CRITICO: de la plantilla solo salen agregados (cuantos jugadores, cuantos goles
del equipo). Los nombres y las edades NO se extraen: son menores y este
repositorio es publico.

Lo que devuelve la plataforma, comprobado el 18/08/2026:

  calendario.php   sirve pista y playa (id_superficie=1|2). El
                   calendario_playa.php que uno esperaria NO trae la tabla.
                   <table class='tabla-calendario'>, 7 celdas por partido:
                   equipos | 1er set | 2o set | 3er set | resultado | fecha | lugar
                   En PISTA los goles estan en la celda del 1er set y la de
                   resultado es el marcador en sets (0 - 1 = gana el visitante).
                   En PLAYA los sets son las tres primeras celdas y la de
                   resultado son los sets ganados.
                   Las filas <tr class="second-table-info"> separan jornadas:
                   "JORNADA 3 (01-11-2025)". Un partido aun no jugado no trae
                   marcador ni fecha en su celda (solo "0:00"): la fecha se
                   hereda de la jornada y la hora queda sin fijar.
  clasificacion.php (pista) / clasificacion_playa.php (playa)
                   Posicion | Equipo | racha | PT | PJ | PG | PE | PP | GF | GC | DIF
  equipo.php       con id_equipo devuelve <table class='tabla-plantilla'>.
                   Sin id_equipo no sirve para nada.

Club Balonmano Barbate — Francisco Vidal Mateo (FranVi)
"""
import html
import re
import time
import unicodedata
import urllib.parse
import urllib.request

BASE = "https://resultadosbalonmano.isquad.es/"
CLUB = "100165"
UA = {"User-Agent": "Mozilla/5.0"}


class ErrorRed(Exception):
    """La pagina no se pudo descargar tras los reintentos."""


def baja(url, intentos=3, espera=2.0):
    fallo = None
    for n in range(intentos):
        try:
            pet = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(pet, timeout=90).read().decode("utf-8", "replace")
        except Exception as e:          # noqa: BLE001 - da igual el motivo, se reintenta
            fallo = e
            if n + 1 < intentos:
                time.sleep(espera * (n + 1))
    raise ErrorRed("%s -> %s" % (url, fallo))


def arregla(t):
    """Recupera el texto doblemente codificado que suelta la plataforma."""
    try:
        return t.encode("latin-1").decode("utf-8")
    except Exception:                   # noqa: BLE001
        return t


_UNI = re.compile(r"\\u([0-9a-fA-F]{4})")


def limpio(t):
    """Texto plano de un fragmento de HTML."""
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = _UNI.sub(lambda m: chr(int(m.group(1), 16)), t)
    t = t.replace('\\"', '"').replace("\\'", "'").replace("\\/", "/")
    return re.sub(r"\s+", " ", arregla(t)).strip()


def normaliza(t):
    """Para comparar nombres de equipo: sin acentos, sin puntuacion y en
    mayusculas. iSquad los escribe en caja alta y sin acentos, torneos.py en
    caja mixta y con ellos."""
    t = unicodedata.normalize("NFD", limpio(t).upper())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Z0-9]+", " ", t).strip()


def numero(t):
    """Primer entero de un texto ("13 93%" -> 13). None si no hay ninguno."""
    m = re.search(r"-?\d+", limpio(t))
    return int(m.group()) if m else None


# ---------------------------------------------------------------- HTML

def tabla(pagina, clase):
    """HTML interno de la primera <table> que lleve esa clase."""
    m = re.search(r"<table[^>]*class=['\"][^'\"]*" + clase + r"[^'\"]*['\"][^>]*>", pagina)
    if not m:
        return ""
    resto = pagina[m.end():]
    fin = resto.find("</table>")
    return resto if fin < 0 else resto[:fin]


def tabla_con(pagina, marca):
    """HTML interno de la <table> que contiene esa marca. La clasificacion no
    tiene clase propia: se localiza por sus celdas nombre-clasi."""
    i = pagina.find(marca)
    if i < 0:
        return ""
    ini = pagina.rfind("<table", 0, i)
    if ini < 0:
        return ""
    resto = pagina[pagina.find(">", ini) + 1:]
    fin = resto.find("</table>")
    return resto if fin < 0 else resto[:fin]


def filas(tabla_html):
    return re.findall(r"<tr([^>]*)>(.*?)</tr>", tabla_html, re.S)


def celdas(fila_html):
    return re.findall(r"<td[^>]*>(.*?)</td>", fila_html, re.S)


def url(pagina, fila, **extra):
    """URL de una pagina de iSquad para una fila de tools/torneos.py."""
    surf, terr, idcat, idcomp, idgr = fila[6], fila[7], fila[8], fila[9], fila[10]
    q = {"seleccion": "0", "id": idgr, "id_ambito": "0", "id_territorial": terr,
         "id_superficie": surf, "iframe": "0", "id_categoria": idcat,
         "id_competicion": idcomp}
    q.update({k: str(v) for k, v in extra.items()})
    return BASE + pagina + "?" + urllib.parse.urlencode(q)


# ---------------------------------------------------------------- calendario

_JORNADA = re.compile(r"JORNADA\s*(\d+)\s*\((\d{2})-(\d{2})-(\d{4})\)", re.I)
_MARCADOR = re.compile(r"(\d+)\s*-\s*(\d+)")
_FECHA = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
_HORA = re.compile(r"\b(\d{1,2}):(\d{2})\b")


def _bandos(celda):
    """(club_local, club_visitante, equipo_local, equipo_visitante).
    El club se lee del escudo, que lleva su identificador."""
    lados = []
    for clase in ("escudo-local-wrap", "escudo-visitante-wrap"):
        m = re.search(r"<a([^>]*" + clase + r"[^>]*)>(.*?)</a>", celda, re.S)
        if not m:
            lados = []
            break
        club = re.search(r"afiliacion_clubs/(\d+)", m.group(2))
        equipo = re.search(r"id_equipo=(\d+)", m.group(1))
        lados.append((club.group(1) if club else None, equipo.group(1) if equipo else None))
    if not lados:                       # respaldo: por orden de aparicion
        clubs = re.findall(r"afiliacion_clubs/(\d+)", celda)
        equipos = re.findall(r"id_equipo=(\d+)", celda)
        if len(clubs) != 2 or len(equipos) < 2:
            return None
        lados = [(clubs[0], equipos[0]), (clubs[1], equipos[1])]
    return lados[0][0], lados[1][0], lados[0][1], lados[1][1]


def _nombres(celda):
    m = re.search(r"nombres-equipos[^>]*>(.*?)</div>", celda, re.S)
    if not m:
        return None
    n = [limpio(a) for a in re.findall(r"<a[^>]*>(.*?)</a>", m.group(1), re.S)]
    return n if len(n) == 2 else None


def _partido(c, superficie, jornada, fecha_jornada, mio=None):
    """Un partido del club a partir de sus 7 celdas. None si no juega el club.

    `mio` es el id_equipo de NUESTRO equipo en ese grupo. Hace falta porque en
    algunos grupos el club mete dos equipos (La Chanca y Balonmano Barbate) y
    hasta se enfrentan entre si: por el escudo los dos son 100165 y no habria
    forma de saber de quien es cada partido ni quien iba de local."""
    bandos = _bandos(c[0])
    if not bandos:
        return None
    club_local, club_visit, eq_local, eq_visit = bandos
    if CLUB not in (club_local, club_visit):
        return None
    if mio and mio not in (eq_local, eq_visit):
        return None                     # es del otro equipo del club
    if mio:
        local = eq_local == mio
    elif club_local != club_visit:
        local = club_local == CLUB
    else:
        return None                     # derbi sin saber cual de los dos somos
    nombres = _nombres(c[0])

    sets = []
    for t in c[1:4]:
        m = _MARCADOR.search(limpio(t))
        if m:
            sets.append((int(m.group(1)), int(m.group(2))))
    if superficie == "1":               # pista: los goles estan en el "1er set"
        goles = sets[0] if sets else None
    else:                               # playa: se suman los sets jugados
        goles = (sum(a for a, _ in sets), sum(b for _, b in sets)) if sets else None

    m = _MARCADOR.search(limpio(c[4]))
    resultado = (int(m.group(1)), int(m.group(2))) if m else None

    texto_fecha = limpio(c[5])
    f = _FECHA.search(texto_fecha)
    fecha = "%s-%s-%s" % (f.group(3), f.group(2), f.group(1)) if f else fecha_jornada
    h = _HORA.search(texto_fecha)
    hora = "%02d:%s" % (int(h.group(1)), h.group(2)) if h else None
    if hora == "00:00":                 # aun sin fijar
        hora = None

    def mio(par):
        return None if par is None else (par[0] if local else par[1])

    def suyo(par):
        return None if par is None else (par[1] if local else par[0])

    return {
        "jornada": jornada,
        "fecha": fecha,
        "hora": hora,
        "local": local,
        "rival": (nombres[1] if local else nombres[0]) if nombres else None,
        "rival_club": club_visit if local else club_local,
        "lugar": limpio(c[6]) or None,
        "goles_club": mio(goles),
        "goles_rival": suyo(goles),
        "sets_club": mio(resultado) if superficie == "2" else None,
        "sets_rival": suyo(resultado) if superficie == "2" else None,
        "sets": ["%d-%d" % s for s in sets] if superficie == "2" and sets else None,
        "id_equipo_club": eq_local if local else eq_visit,
    }


def _nuestro_equipo(tb, nombre_federado):
    """El id_equipo de nuestro equipo en ese grupo, por el nombre con el que
    esta inscrito. En un grupo puede haber DOS equipos del club: por el escudo
    son indistinguibles, asi que aqui manda el nombre de tools/torneos.py."""
    busco = normaliza(nombre_federado)
    candidatos = {}                     # id_equipo -> nombre
    for _attrs, cuerpo in filas(tb):
        c = celdas(cuerpo)
        if len(c) < 7:
            continue
        bandos = _bandos(c[0])
        nombres = _nombres(c[0])
        if not bandos or not nombres:
            continue
        for club, equipo, nombre in ((bandos[0], bandos[2], nombres[0]),
                                     (bandos[1], bandos[3], nombres[1])):
            if club == CLUB and equipo:
                candidatos[equipo] = nombre
    for equipo, nombre in candidatos.items():
        if normaliza(nombre) == busco:
            return equipo
    return list(candidatos)[0] if len(candidatos) == 1 else None


def calendario(fila):
    """Partidos de NUESTRO equipo en ese grupo, en el orden de la plataforma."""
    superficie = fila[6]
    tb = tabla(baja(url("calendario.php", fila)), "tabla-calendario")
    if not tb:
        return []
    mio = _nuestro_equipo(tb, fila[3])
    salida, jornada, fecha_jornada = [], None, None
    for attrs, cuerpo in filas(tb):
        if "second-table-info" in attrs:
            m = _JORNADA.search(limpio(cuerpo))
            if m:
                jornada = int(m.group(1))
                fecha_jornada = "%s-%s-%s" % (m.group(4), m.group(3), m.group(2))
            continue
        c = celdas(cuerpo)
        if len(c) < 7:
            continue
        p = _partido(c, superficie, jornada, fecha_jornada, mio)
        if p:
            salida.append(p)
    return salida


# ---------------------------------------------------------------- clasificacion

def clasificacion(fila):
    """Puesto y balance del club en su grupo. None si no aparece."""
    pagina = baja(url("clasificacion_playa.php" if fila[6] == "2" else "clasificacion.php", fila))
    tb = tabla_con(pagina, "nombre-clasi")
    if not tb:
        return None
    equipos, nuestras = 0, []
    for _attrs, cuerpo in filas(tb):
        if "nombre-clasi" not in cuerpo:
            continue
        c = celdas(cuerpo)
        if len(c) < 11:
            continue
        equipos += 1
        if re.search(r"afiliacion_clubs/" + CLUB + r"/", c[1]):
            nuestras.append(c)
    if not nuestras:
        return None
    # Si el club tiene dos equipos en el grupo, el nombre de tools/torneos.py
    # dice cual es cual: por el escudo son el mismo.
    mia = nuestras[0]
    if len(nuestras) > 1:
        busco = normaliza(fila[3])
        mia = next((c for c in nuestras if normaliza(c[1]) == busco), nuestras[0])
    # Pista trae 11 columnas y playa 14 (mete los sets en medio), pero las tres
    # ultimas son siempre GF, GC y diferencia: se leen desde el final.
    salida = {
        # Con la liga sin empezar la plataforma pone un 0 en la posicion.
        "puesto": numero(mia[0]) or None,
        "de": equipos,
        "puntos": numero(mia[3]),
        "pj": numero(mia[4]),
        "pg": numero(mia[5]),
        "pe": numero(mia[6]),
        "pp": numero(mia[7]),
        "gf": numero(mia[-3]),
        "gc": numero(mia[-2]),
    }
    if fila[6] == "2" and len(mia) >= 14:
        salida["sg"] = numero(mia[8])
        salida["sp"] = numero(mia[9])
    return salida


# ---------------------------------------------------------------- plantilla

def plantilla(fila, id_equipo):
    """SOLO un agregado: cuantos jugadores tiene inscritos el equipo.

    La tabla trae nombre, apellidos, edad y goles de cada jugador. NO se
    extraen a proposito: son menores y este repositorio es publico. Si algun
    dia hay consentimiento de los tutores, el nombre esta en la celda 0.

    Los goles individuales tampoco se suman: no son de este grupo (el cadete
    masculino sumaba 2.269 cuando en su liga marco 551), asi que el dato
    enganya. Los goles del equipo salen de la clasificacion, que si es del
    grupo."""
    if not id_equipo:
        return None
    tb = tabla(baja(url("equipo.php", fila, id_equipo=id_equipo)), "tabla-plantilla")
    if not tb:
        return None
    jugadores = 0
    for _attrs, cuerpo in filas(tb):
        c = celdas(cuerpo)
        if len(c) < 4:
            continue
        if limpio(c[1]).lower() != "jugador":   # fuera tecnicos y delegados
            continue
        jugadores += 1
    return {"jugadores": jugadores} if jugadores else None
