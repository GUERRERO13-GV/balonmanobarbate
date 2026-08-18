# -*- coding: utf-8 -*-
"""Escribe en el sitio los partidos que recogio tools/recoge_partidos.py.

    python tools/genera_partidos.py

Reescribe dos bloques, cada uno entre sus marcadores:

    index.html    <!-- PROXIMO:INICIO -->     el proximo partido del club
    equipos.html  <!-- MARCADORES:INICIO -->  resultados y clasificacion por equipo

Lo que hay entre los marcadores es generado: si se edita a mano, la siguiente
pasada lo pisa. Los marcadores tienen que existir en el HTML; si faltan, el
script avisa y no toca nada.

El HTML sale completo, sin depender de JavaScript: la cuenta atras de la
portada es un anyadido que main.js revela si puede, y sin el sigue viendose la
fecha, el rival y el pabellon.

Club Balonmano Barbate — Francisco Vidal Mateo (FranVi)
"""
import datetime
import html
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from genera_torneos import ORDEN_CAT, SEXOS      # noqa: E402  la misma jerarquia

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:                                # noqa: BLE001
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, "datos", "deportivo.json")

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Siglas que se quedan en mayusculas al pasar un nombre federado a caja mixta.
SIGLAS = {"BM", "BMP", "CB", "CBM", "CBMP", "CD", "CDB", "AD", "SD", "FC", "CF",
          "DF", "DFC", "UD", "EM", "ED", "CE", "AA", "AMPA", "II", "III", "IV",
          "SL", "SUR", "A", "B", "C", "D"}
MINUSCULAS = {"de", "del", "la", "las", "los", "el", "y", "e", "en", "a"}


def esc(t):
    return html.escape(t or "", quote=True)


def _trozo(t):
    """Capitaliza respetando guiones y puntos: MUBAK-BHB no puede quedar como
    Mubak-bhb, y C.H. tiene que seguir siendo C.H."""
    fuera, palabra = [], ""
    for ch in t:
        if ch in "-./":
            fuera.append(palabra)
            fuera.append(ch)
            palabra = ""
        else:
            palabra += ch
    fuera.append(palabra)
    salida = ""
    for n, parte in enumerate(fuera):
        if parte in "-./" or not parte:
            salida += parte
        elif len(parte) == 1 or (n and fuera[n - 1] == "."):
            salida += parte.upper()     # iniciales: C.H., D.F.C.
        else:
            salida += parte.capitalize()
    return salida


def bonito(nombre):
    """El nombre federado viene en mayusculas y sin acentos; los titulares del
    sitio van en caja mixta. No se inventan acentos: solo se cambia la caja."""
    if not nombre:
        return ""
    fuera = []
    for n, palabra in enumerate(nombre.split()):
        if palabra.upper().strip(".-") in SIGLAS:
            fuera.append(palabra.upper())
        elif n and palabra.lower() in MINUSCULAS:
            fuera.append(palabra.lower())
        else:
            fuera.append(_trozo(palabra))
    return " ".join(fuera)


def fecha(iso):
    return datetime.date.fromisoformat(iso) if iso else None


def fecha_larga(iso):
    d = fecha(iso)
    return "%s %d de %s" % (DIAS[d.weekday()], d.day, MESES[d.month - 1])


def fecha_corta(iso):
    d = fecha(iso)
    return "%02d/%02d" % (d.day, d.month)


def jugado(p):
    return p["goles_club"] is not None and p["goles_rival"] is not None


def signo(p):
    if not jugado(p):
        return ""
    if p["sets_club"] is not None:      # en playa manda el marcador en sets
        a, b = p["sets_club"], p["sets_rival"]
    else:
        a, b = p["goles_club"], p["goles_rival"]
    return "gana" if a > b else ("pierde" if a < b else "empata")


def tanteo(p):
    """En playa gana quien gana los sets, no quien mete mas goles: hubo un
    49-48 que era derrota por 0-2. Se ensenya lo que decide el partido."""
    if p["sets_club"] is not None:
        return "%d – %d" % (p["sets_club"], p["sets_rival"])
    return "%d – %d" % (p["goles_club"], p["goles_rival"])


def parciales(p):
    """Los sets de un partido de playa, ya vistos desde nuestro lado."""
    if not p.get("sets"):
        return ""
    fuera = []
    for s in p["sets"]:
        a, b = s.split("-")
        fuera.append("%s-%s" % (a, b) if p["local"] else "%s-%s" % (b, a))
    return " · ".join(fuera)


def rotulo(e):
    sexo = "Masculino" if e["sexo"] == "M" else "Femenino"
    return "%s %s" % (sexo, e["categoria"])


def partidos_de(datos):
    """Todos los partidos con su equipo al lado, para poder ordenarlos juntos."""
    salida = []
    for e in datos["equipos"]:
        for p in e["partidos"]:
            if p["fecha"]:
                salida.append((p, e))
    return salida


# ------------------------------------------------------------ portada

def ficha_proxima(p, e):
    donde = "en casa" if p["local"] else "a domicilio"
    cuando = fecha_larga(p["fecha"])
    hora = p["hora"] or "hora por confirmar"
    marca = p["fecha"] + ("T" + p["hora"] + ":00" if p["hora"] else "T12:00:00")
    out = [
        '        <p class="eyebrow">Próximo partido · %s</p>' % esc(rotulo(e)),
        # El club siempre delante: esta es su web, no un tablon neutral. Quien
        # juega en casa se dice justo debajo.
        '        <h2>Barbate — %s</h2>' % esc(bonito(p["rival"]) or "Rival por designar"),
        '        <p class="proximo-cuando"><time datetime="%s">%s</time> · %s · %s</p>'
        % (esc(marca), esc(cuando[0].upper() + cuando[1:]), esc(hora), donde),
        '        <dl class="proximo-datos">',
        '          <div><dt>Competición</dt><dd>%s</dd></div>' % esc(p_competicion(e)),
        '          <div><dt>Pabellón</dt><dd>%s</dd></div>' % esc(bonito(p["lugar"]) or "Por confirmar"),
        '        </dl>',
        '        <p class="proximo-cuenta" data-cuenta="%s" hidden></p>' % esc(marca),
    ]
    return out


def p_competicion(e):
    disciplina = "Pista" if e["superficie"] == "1" else "Playa"
    return "%s · %s %s" % (e["torneo"], disciplina, e["temporada"])


def ficha_ultimo(p, e):
    cuando = fecha_larga(p["fecha"])
    out = [
        '        <p class="eyebrow">Último partido · %s</p>' % esc(rotulo(e)),
        '        <h2>Barbate — %s</h2>' % esc(bonito(p["rival"]) or "—"),
        '        <p class="proximo-cuando"><span class="proximo-tanteo %s">%s</span> · <time datetime="%s">%s</time> · %s</p>'
        % (signo(p), esc(tanteo(p)), esc(p["fecha"]),
           esc(cuando[0].upper() + cuando[1:]), "en casa" if p["local"] else "a domicilio"),
        '        <dl class="proximo-datos">',
        '          <div><dt>Competición</dt><dd>%s</dd></div>' % esc(p_competicion(e)),
    ]
    if parciales(p):
        out += ['          <div><dt>Sets</dt><dd>%s</dd></div>' % esc(parciales(p))]
    out += ['          <div><dt>Pabellón</dt><dd>%s</dd></div>' % esc(bonito(p["lugar"]) or "—"),
            '        </dl>']
    return out


def bloque_proximo(datos):
    todos = partidos_de(datos)
    hoy = datetime.date.today()
    futuros = sorted([(p, e) for p, e in todos if not jugado(p) and fecha(p["fecha"]) >= hoy],
                     key=lambda x: (x[0]["fecha"], x[0]["hora"] or "99:99"))
    jugados = sorted([(p, e) for p, e in todos if jugado(p)],
                     key=lambda x: (x[0]["fecha"], x[0]["hora"] or ""), reverse=True)

    if not futuros and not jugados:
        return ""                        # sin datos no se pinta un hueco

    out = ['<!-- Próximo partido. Bloque generado por tools/genera_partidos.py a',
           '     partir de datos/deportivo.json: no se edita a mano. -->',
           '<section class="banda banda-arena proximo">',
           '  <div class="container">',
           '    <div class="rejilla">',
           '      <div class="col-a filete">']
    if futuros:
        out += ficha_proxima(*futuros[0])
    else:
        out += ficha_ultimo(*jugados[0])
    out += ['      </div>']

    resto = jugados[1:] if not futuros else jugados
    if resto:
        out += ['      <div class="col-b filete">',
                '        <p class="eyebrow">Últimos resultados</p>',
                '        <ul class="ultimos">']
        for p, e in resto[:4]:
            rival = bonito(p["rival"]) or "—"
            # En playa el tanteo va en sets: sin los parciales al lado, un 2-1
            # no se entiende.
            detalle = (" <span class=\"u-sets\">%s</span>" % esc(parciales(p))) if parciales(p) else ""
            out += ['          <li>',
                    '            <span class="u-fecha">%s</span>' % esc(fecha_corta(p["fecha"])),
                    '            <span class="u-quien">%s</span>' % esc(rotulo(e)),
                    '            <span class="u-rival">%s %s%s</span>'
                    % ("vs" if p["local"] else "en", esc(rival), detalle),
                    '            <span class="u-tanteo %s">%s</span>' % (signo(p), esc(tanteo(p))),
                    '          </li>']
        out += ['        </ul>',
                '        <a class="enlace-filete" href="equipos.html#resultados">Todos los resultados</a>',
                '      </div>']
    out += ['    </div>', '  </div>', '</section>']
    return "\n".join(out)


# ------------------------------------------------------------ equipos.html

def linea_clasificacion(c, superficie):
    if not c or not c.get("pj"):
        return '                <p class="marcador-clasi">Sin jornadas disputadas</p>'
    trozos = []
    if c.get("puesto"):
        trozos.append("<b>%d.º</b> de %d" % (c["puesto"], c["de"]))
    trozos.append("%d pts" % (c.get("puntos") or 0))
    trozos.append("%d PJ" % c["pj"])
    trozos.append("%d G · %d E · %d P" % (c.get("pg") or 0, c.get("pe") or 0, c.get("pp") or 0))
    if superficie == "2" and c.get("sg") is not None:
        trozos.append("%d–%d sets" % (c["sg"], c["sp"]))
    if c.get("gf") is not None:
        trozos.append("%d–%d goles" % (c["gf"], c["gc"]))
    return '                <p class="marcador-clasi">%s</p>' % " · ".join(trozos)


def lista_partidos(e):
    hoy = datetime.date.today()
    ps = [p for p in e["partidos"] if p["fecha"]]
    jugados = sorted([p for p in ps if jugado(p)], key=lambda p: p["fecha"])[-5:]
    futuros = sorted([p for p in ps if not jugado(p) and fecha(p["fecha"]) >= hoy],
                     key=lambda p: p["fecha"])[:2]
    if not jugados and not futuros:
        return []
    out = ['                <ol class="marcador-partidos">']
    for p in jugados + futuros:
        rival = bonito(p["rival"]) or "—"
        marca = tanteo(p) if jugado(p) else (p["hora"] or "—")
        detalle = parciales(p)
        out += ['                  <li>',
                '                    <span class="m-fecha">%s</span>' % esc(fecha_corta(p["fecha"])),
                '                    <span class="m-rival">%s %s%s</span>'
                % ("vs" if p["local"] else "en", esc(rival),
                   ' <span class="m-sets">%s</span>' % esc(detalle) if detalle else ""),
                '                    <span class="m-tanteo %s">%s</span>' % (signo(p), esc(marca)),
                '                  </li>']
    out += ['                </ol>']
    return out


def linea_suelta(p, e, con_tanteo=True):
    """Un partido en la lista corrida, con su equipo delante: quien entra a la
    pagina tiene que ver que ha pasado sin abrir nada ni saber de antemano en
    que categoria buscar."""
    rival = bonito(p["rival"]) or "—"
    detalle = (' <span class="u-sets">%s</span>' % esc(parciales(p))) if parciales(p) else ""
    if con_tanteo:
        marca = '<span class="u-tanteo %s">%s</span>' % (signo(p), esc(tanteo(p)))
    elif p["hora"]:
        marca = '<span class="u-tanteo">%s</span>' % esc(p["hora"])
    else:
        marca = ""                      # sin hora fijada no se pinta un guion suelto
    fuera = ['          <li>',
             '            <span class="u-fecha">%s</span>' % esc(fecha_corta(p["fecha"])),
             '            <span class="u-quien">%s · %s</span>' % (esc(rotulo(e)), esc(e["torneo"])),
             '            <span class="u-rival">%s %s%s</span>'
             % ("vs" if p["local"] else "en", esc(rival), detalle)]
    if marca:
        fuera.append('            %s' % marca)
    fuera.append('          </li>')
    return fuera


def bloque_marcadores(datos):
    equipos = [e for e in datos["equipos"] if e["partidos"]]
    if not equipos:
        return ""
    cuando = datos.get("actualizado", "")[:10]
    hoy = datetime.date.today()
    todos = partidos_de(datos)
    ultimos = sorted([(p, e) for p, e in todos if jugado(p)],
                     key=lambda x: (x[0]["fecha"], x[0]["hora"] or ""), reverse=True)[:10]
    # Como mucho dos por equipo: si no, el único equipo que ya tiene calendario
    # publicado se come la lista entera y parece que el club solo juega eso.
    proximos, cuantos = [], {}
    for x in sorted([(p, e) for p, e in todos if not jugado(p) and fecha(p["fecha"]) >= hoy],
                    key=lambda x: (x[0]["fecha"], x[0]["hora"] or "99:99")):
        k = x[1]["clave"]
        if cuantos.get(k, 0) >= 2:
            continue
        cuantos[k] = cuantos.get(k, 0) + 1
        proximos.append(x)
        if len(proximos) >= 6:
            break

    out = ['<!-- Resultados. Bloque generado por tools/genera_partidos.py a partir',
           '     de datos/deportivo.json: no se edita a mano. Lo último y lo que',
           '     viene van sueltos y a la vista; el detalle por equipo se pliega. -->',
           '    <div class="marcadores">',
           '      <p class="eyebrow marcadores-sello">Temporada en curso · actualizado el %s</p>'
           % esc(fecha_larga(cuando) if cuando else "—"),
           '      <div class="rejilla">']

    if proximos:
        out += ['        <div class="col-a filete">',
                '          <h3>Lo que viene</h3>',
                '          <ul class="ultimos">']
        for p, e in proximos:
            out += linea_suelta(p, e, con_tanteo=False)
        out += ['          </ul>', '        </div>']

    if ultimos:
        out += ['        <div class="col-b filete">',
                '          <h3>Lo último</h3>',
                '          <ul class="ultimos">']
        for p, e in ultimos:
            out += linea_suelta(p, e)
        out += ['          </ul>', '        </div>']
    out += ['      </div>']

    out += ['      <details class="mas-equipos">',
            '        <summary><span>Ver equipo por equipo</span></summary>']
    out += ['      <div class="comp-grupos">']
    for cod, sexo in SEXOS:
        suyos = [e for e in equipos if e["sexo"] == cod]
        if not suyos:
            continue
        out += ['        <div class="comp-sexo">', '          <h3>%s</h3>' % sexo]
        cats = [c for c in ORDEN_CAT if any(e["categoria"] == c for e in suyos)]
        cats += sorted({e["categoria"] for e in suyos} - set(cats))
        for cat in cats:
            fs = sorted([e for e in suyos if e["categoria"] == cat],
                        key=lambda e: max(p["fecha"] for p in e["partidos"] if p["fecha"]),
                        reverse=True)
            out += ['          <details class="comp-categoria">',
                    '            <summary><h4>%s <span>%d %s</span></h4></summary>'
                    % (esc(cat), len(fs), "torneo" if len(fs) == 1 else "torneos"),
                    '            <ul class="marcador-lista">']
            for e in fs:
                out += ['              <li>',
                        '                <p class="comp-torneo">%s</p>' % esc(e["torneo"]),
                        '                <span class="comp-detalle">%s · %s · %s</span>'
                        % ("Pista" if e["superficie"] == "1" else "Playa",
                           esc(e["temporada"]), esc(e["nombre_federado"])),
                        linea_clasificacion(e["clasificacion"], e["superficie"])]
                out += lista_partidos(e)
                out += ['              </li>']
            out += ['            </ul>', '          </details>']
        out += ['        </div>']
    out += ['      </div>', '      </details>', '    </div>']
    return "\n".join(out)


# ------------------------------------------------------------ empalme

BLOQUES = [
    ("index.html", "<!-- PROXIMO:INICIO -->", "<!-- PROXIMO:FIN -->", bloque_proximo),
    ("equipos.html", "<!-- MARCADORES:INICIO -->", "<!-- MARCADORES:FIN -->", bloque_marcadores),
]


def inserta(archivo, ini, fin, cuerpo):
    ruta = os.path.join(RAIZ, archivo)
    s = io.open(ruta, encoding="utf-8").read()
    a, b = s.find(ini), s.find(fin)
    if a < 0 or b < 0 or b < a:
        raise SystemExit("%s: faltan los marcadores %s / %s" % (archivo, ini, fin))
    fuera = s[a + len(ini):b].count("\n")
    nuevo = s[:a + len(ini)] + "\n" + cuerpo + ("\n" if cuerpo else "") + s[b:]
    io.open(ruta, "w", encoding="utf-8", newline="").write(nuevo)
    return fuera, cuerpo.count("\n") + 1 if cuerpo else 0


def main():
    if not os.path.exists(ORIGEN):
        raise SystemExit("no existe %s: lanza antes tools/recoge_partidos.py"
                         % os.path.relpath(ORIGEN, RAIZ))
    with io.open(ORIGEN, encoding="utf-8") as fh:
        datos = json.load(fh)
    for archivo, ini, fin, hazlo in BLOQUES:
        fuera, dentro = inserta(archivo, ini, fin, hazlo(datos))
        print("%s: %d lineas fuera, %d dentro" % (archivo, fuera, dentro))
    return 0


if __name__ == "__main__":
    sys.exit(main())
