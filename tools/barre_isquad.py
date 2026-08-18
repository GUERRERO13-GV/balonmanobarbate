"""Busca en que competiciones y grupos juega el club, leyendo iSquad con curl.

    python tools/barre_isquad.py > barrido.log

Recorre cada categoria federada, cada competicion y CADA GRUPO, y se queda
solo con los grupos cuya clasificacion trae el escudo del club 100165. El
carrusel de escudos de cabecera NO sirve: es de toda la competicion, no del
grupo. Barbate casi nunca esta en el grupo que carga por defecto.

Las filas que salgan aqui se pasan a tools/torneos.py.

Club Balonmano Barbate — Francisco Vidal Mateo (FranVi)
"""
import re, json, html, time, urllib.request, sys

NUESTRO = "100165"
UA = {"User-Agent": "Mozilla/5.0"}
B = "https://resultadosbalonmano.isquad.es/"

def baja(u):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90).read().decode("utf-8", "replace")
        except Exception as e:
            time.sleep(2)
    return ""

def arregla(t):
    try: return t.encode("latin-1").decode("utf-8")
    except Exception: return t

def limpio(t): return arregla(html.unescape(re.sub("<[^>]+>", "", t)).strip())

def opciones(s, sid):
    m = re.search(r'<select[^>]*id=["\']' + sid + r'["\'][^>]*>(.*?)</select>', s, re.S | re.I)
    if not m: return []
    return [(v, limpio(t)) for v, t in re.findall(r'<option[^>]*value=["\']([^"\']*)["\'][^>]*>(.*?)</option>', m.group(1), re.S)]

CELDA = re.compile(r"<td class='nombre-clasi'>(.*?)</td>", re.S)
def filas(u):
    s = baja(u); o = []
    for c in CELDA.findall(s):
        cid = re.search(r'afiliacion_clubs/(\d+)/', c)
        o.append((cid.group(1) if cid else '?', limpio(c.split('</span>')[-1])))
    return o

def escanea(terr, surf, temp, etiqueta):
    print(f"\n{'='*70}\n{etiqueta}  (territorial={terr}, superficie={surf}, temporada={temp})\n{'='*70}", flush=True)
    raiz = f"{B}competicion.php?id_superficie={surf}&seleccion=0&id_territorial={terr}&id_temp={temp}&id_ambito=0"
    s0 = baja(raiz)
    m = re.search(r'var EMBED_CATEGORIAS\s*=\s*(\[.*?\]);', s0, re.S)
    cats = json.loads(m.group(1)) if m else []
    suf = "_playa" if surf == "2" else ""
    clasi = "clasificacion_playa.php" if surf == "2" else "clasificacion.php"
    hall = []
    for cat in cats:
        cid, cnom = cat["id"], arregla(cat["nombre"])
        s1 = baja(f"{raiz}&id_categoria={cid}")
        semilla = re.findall(r'id_competicion=(\d+)', s1)
        semilla = [x for x in semilla if x != "0"]
        if not semilla:
            print(f"  [{cid}] {cnom}: sin competiciones", flush=True); continue
        s2 = baja(f"{raiz}&id_categoria={cid}&id_competicion={semilla[0]}")
        comps = opciones(s2, "competiciones" + suf) or [(semilla[0], "(unica)")]
        print(f"  [{cid}] {cnom}: {len(comps)} competiciones", flush=True)
        for kid, knom in comps:
            sk = baja(f"{raiz}&id_categoria={cid}&id_competicion={kid}")
            if NUESTRO not in sk:
                continue
            print(f"      *** {knom} (id_competicion={kid}) contiene al club", flush=True)
            for gid, gnom in opciones(sk, "torneos" + suf):
                f = filas(f"{B}{clasi}?seleccion=0&id={gid}&id_ambito=0&id_territorial={terr}"
                          f"&id_superficie={surf}&iframe=0&id_categoria={cid}&id_competicion={kid}")
                nues = [n for c, n in f if c == NUESTRO]
                if nues:
                    print(f"          GRUPO id={gid}  {gnom}  -> {' / '.join(nues)}  ({len(f)} eq.)", flush=True)
                    hall.append((etiqueta, cnom, knom, cid, kid, gid, gnom, nues[0]))
                time.sleep(0.2)
            time.sleep(0.2)
    return hall

# Que barrer. territorial 26 = Andalucia, 9999 = Real Federacion Española.
# superficie 1 = pista, 2 = playa. id_temp SI se respeta: cambia la lista
# entera de categorias.
BARRIDOS = [
    ("26",   "1", "2627", "ANDALUCIA PISTA 2026/27"),
    ("26",   "1", "2526", "ANDALUCIA PISTA 2025/26"),
    ("26",   "1", "2425", "ANDALUCIA PISTA 2024/25"),
    ("26",   "2", "2526", "ANDALUCIA PLAYA 2025/26"),
    ("26",   "2", "2425", "ANDALUCIA PLAYA 2024/25"),
    ("9999", "2", "2526", "ESPAÑA PLAYA 2025/26"),
    ("9999", "1", "2526", "ESPAÑA PISTA 2025/26"),
]

todo = []
for terr, surf, temp, etiqueta in BARRIDOS:
    todo += escanea(terr, surf, temp, etiqueta)
print(chr(10) + "##### RESUMEN", flush=True)
for t in todo:
    print(t[0] + " | " + t[1] + " | " + t[2] + " | categoria=" + str(t[3]) +
          " competicion=" + str(t[4]) + " grupo=" + str(t[5]) + " | " + t[6] + " | " + t[7], flush=True)
