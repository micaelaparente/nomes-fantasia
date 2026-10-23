"""Geocodificação rápida dos CNPJs nos trechos de rua do data.rio (interpolação pela numeração).

Uso: python pipeline/04_geocodifica.py   (lê dados/brutos/cnpj_rio.csv, grava dados/intermediarios/cnpj_geo.csv)
Lê o cadastro de logradouros e a geometria dos trechos baixados pelo 02.
"""
import csv, json, math, random, re, sys, unicodedata
from collections import defaultdict

from caminhos import CNPJ_RIO, GEO, LOGRADOUROS, TRECHOS
PREP = {'DE', 'DA', 'DO', 'DOS', 'DAS', 'E', 'D'}
random.seed(7)


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().upper()
    return re.sub(r'\s+', ' ', re.sub(r'[^A-Z0-9 ]', ' ', s)).strip()


def chave(s):
    return ' '.join(w for w in norm(s).split() if w not in PREP)


def num(s):
    m = re.search(r'\d+', s or '')
    return int(m.group()) if m else None


# --- geometria dos trechos (lon/lat) ---
geo = {}
for cod, tipo, coords in json.load(open(TRECHOS)):
    if tipo == 'MultiLineString':
        coords = max(coords, key=len)
    geo[str(cod)] = coords

# --- cadastro: (rua, bairro) -> trechos com faixas de numeração ---
por_rb = defaultdict(list)
por_rua = defaultdict(list)
for r in csv.DictReader(open(LOGRADOUROS, encoding='utf-8-sig')):
    g = geo.get(r['cod_trecho'])
    if not g or len(g) < 2:
        continue
    t = {'g': g, 'bairro': r['bairro'].strip(), 'cl': r['cl'], 'cod': r['cod_trecho'],
         'par': (num(r['np_ini_par']) or 0, num(r['np_fin_par']) or 0),
         'imp': (num(r['np_ini_imp']) or 0, num(r['np_fin_imp']) or 0)}
    k = chave(r['completo'])
    por_rb[(k, norm(r['bairro']))].append(t)
    por_rua[k].append(t)


def ponto(g, f):
    """Ponto a uma fração f do comprimento da linha + ângulo do segmento."""
    segs = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(g, g[1:])]
    tot = sum(s[2] for s in segs) or 1
    alvo = f * tot
    for a, b, d in segs:
        if alvo <= d or (a, b, d) == segs[-1]:
            u = alvo / d if d else 0
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, math.atan2(b[1] - a[1], b[0] - a[0])
        alvo -= d


def escolhe(cands, n):
    """Trecho cuja faixa (da paridade de n) contém n; senão o mais próximo."""
    if n is None:
        return random.choice(cands), random.random(), 0
    lado = 'par' if n % 2 == 0 else 'imp'
    melhor, dist = None, 1e9
    for t in cands:
        a, b = t[lado]
        if a == 0 and b == 0:
            continue
        lo, hi = min(a, b), max(a, b)
        d = 0 if lo <= n <= hi else min(abs(n - lo), abs(n - hi))
        if d < dist:
            melhor, dist = t, d
    if melhor is None:
        return random.choice(cands), random.random(), 1 if lado == 'par' else -1
    a, b = melhor[lado]
    f = 0.5 if a == b else min(1, max(0, (n - a) / (b - a)))
    return melhor, f, 1 if lado == 'par' else -1


ent, sai = CNPJ_RIO, GEO
ok = tot = 0
with open(ent, encoding='utf-8') as fi, open(sai, 'w', newline='') as fo:
    w = csv.writer(fo)
    w.writerow(['cnpj', 'cnae', 'situacao', 'inicio', 'fim', 'numero', 'lado', 'cl', 'bairro_oficial',
                'lon', 'lat', 'angulo', 'casou_bairro', 'cod_trecho'])
    for r in csv.DictReader(fi):
        tot += 1
        k = chave(r['logradouro'])
        cands = por_rb.get((k, norm(r['bairro'])))
        casou_b = bool(cands)
        if not cands:
            cands = por_rua.get(k)
        if not cands:
            continue
        n = num(r['numero'])
        t, f, lado = escolhe(cands, n)
        lon, lat, ang = ponto(t['g'], f)
        ok += 1
        w.writerow([r['cnpj'], r['cnae'], r['situacao_cadastral'], r['inicio'], r['fim'], n if n is not None else '',
                    lado, t['cl'], t['bairro'], round(lon, 6), round(lat, 6), round(math.degrees(ang)),
                    int(casou_b), t['cod']])
print(f'{ok}/{tot} geocodificados ({ok / tot:.1%})')
