"""Etapa 6: geocodificação. Cada comércio num ponto da rua, e o bairro onde o ponto cai -> dados/intermediarios/geo.csv

Regras (METODOLOGIA.md, etapa 6):
- a rua do endereço é casada com o cadastro de logradouros da Prefeitura por uma chave tolerante: sem tipo (Rua,
  Avenida...), sem títulos (Marechal, Ator, Prof...), grafia simplificada (Z/S, Y/I, letras dobradas), em qualquer ordem;
- primeiro na rua com esse nome no bairro declarado; se não há, na rua com esse nome no bairro vizinho, se ela passa a
  até VIZINHO km do bairro declarado; mais longe, é outra rua com o mesmo nome e o comércio fica de fora;
- o ponto vai pela faixa de numeração do lado (par/ímpar); sem número ou sem faixa, no meio da rua;
- sem rua, o comércio vai para o centro do bairro declarado, se ele existe na malha: o ponto de rua do bairro mais perto
  da média dos pontos de rua dele (sempre numa rua do bairro);
- o bairro do comércio é o do polígono onde o ponto cai, na malha de bairros da Prefeitura.
Uso: python pipeline/06_geocodifica.py
"""
import csv
import json
import math
import re
from collections import defaultdict

import pandas as pd

from caminhos import CATEGORIAS, GEO, LOGRADOUROS, TRECHOS, BAIRROS
from pessoas import norm

FORA = set('''DE DA DO DOS DAS E D RUA R AVENIDA AV ESTRADA ESTR EST TRAVESSA TV PRACA PC LARGO LGO ALAMEDA AL RODOVIA
VIA BECO LADEIRA CAMINHO PRAIA ESTRADINHA VILA SERVIDAO PARQUE ATOR ATRIZ ALM ALMIRANTE PROF PROFESSOR PROFESSORA TEC
FUTE TECNICO MARECHAL MAL GENERAL GAL CORONEL CEL CAPITAO CAP TENENTE TEN SARGENTO SGT MAJOR MAJ BRIGADEIRO BRIG
COMANDANTE CMTE DOUTOR DR DRA ENGENHEIRO ENG PADRE PE MONSENHOR DOM DONA SAO SANTO SANTA NOSSA SENHORA N S SRA PRESIDENTE
PRES PREFEITO GOVERNADOR GOV DEPUTADO DEP SENADOR VEREADOR MINISTRO MIN JORNALISTA MAESTRO POETA ESCRITOR CANTOR
COMPOSITOR MOTORISTA DESEMBARGADOR DES BARAO VISCONDE CONDE MARQUES DUQUE PRINCESA PRINCIPE IMPERADOR'''.split())


def simples(w):
    w = w.replace('TH', 'T').replace('Y', 'I').replace('Z', 'S').replace('PH', 'F').replace('W', 'V')
    w = re.sub(r'(.)\1+', r'\1', w)                    # letras dobradas: Fontenelle ~ Fontenele
    w = re.sub(r'EIA$', 'EA', w)                       # Correia ~ Correa
    return re.sub(r'(AM|AN)$', 'A', w)                 # Paranapuam ~ Paranapuã


VIZINHO = 1      # km entre a rua e o bairro declarado
# o cadastro de ruas usa o nome novo; a malha de bairros, o antigo
GRAFIA = {'IMPERIAL DE SAO CRISTOVAO': 'SAO CRISTOVAO'}


def chave(rua):
    return ' '.join(sorted(simples(w) for w in norm(rua).split() if w not in FORA and not w.isdigit()))


def nome_bairro(b):
    """O bairro com a mesma grafia simplificada da rua: Oswaldo/Osvaldo Cruz, Braz/Brás de Pina."""
    b = ' '.join(simples(w) for w in norm(b).split())
    return GRAFIA.get(b, b)


def numero(s):
    m = re.search(r'\d+', s or '')
    return int(m.group()) if m else None


# --- malha de bairros: polígonos (lon/lat) com caixa, e os vértices de cada bairro (para a distância até uma rua)
bairros, vertices = [], defaultdict(list)
for f in json.load(open(BAIRROS))['features']:
    nome, g = f['properties']['nome'].strip(), f['geometry']
    for p in (g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]):
        anel = p[0]
        bairros.append((nome, anel, min(c[0] for c in anel), max(c[0] for c in anel),
                        min(c[1] for c in anel), max(c[1] for c in anel)))
        vertices[nome_bairro(nome)] += anel[::max(1, len(anel) // 400)]


def dentro(x, y, anel):
    c = False
    for (x1, y1), (x2, y2) in zip(anel, anel[1:] + anel[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def bairro_do_ponto(x, y):
    return next((n for n, anel, a, b, c, d in bairros if a <= x <= b and c <= y <= d and dentro(x, y, anel)), '')


# --- trechos de rua: geometria (a parte mais longa, se for multilinha) e faixas de numeração de cada lado
geo = {}
for cod, tipo, coords in json.load(open(TRECHOS)):
    geo[str(cod)] = max(coords, key=len) if tipo == 'MultiLineString' else coords
por_rb, bairros_da_rua = defaultdict(list), defaultdict(set)
for r in csv.DictReader(open(LOGRADOUROS, encoding='utf-8-sig')):
    g = geo.get(r['cod_trecho'])
    if not g or len(g) < 2:
        continue
    k, b = chave(r['completo']), nome_bairro(r['bairro'])
    por_rb[(k, b)].append({'g': g, 'par': (numero(r['np_ini_par']) or 0, numero(r['np_fin_par']) or 0),
                           'imp': (numero(r['np_ini_imp']) or 0, numero(r['np_fin_imp']) or 0)})
    bairros_da_rua[k].add(b)


def ponto(g, f):
    """O ponto a uma fração f do comprimento da linha."""
    segs = [(a, b, math.hypot(b[0] - a[0], b[1] - a[1])) for a, b in zip(g, g[1:])]
    alvo = f * (sum(s[2] for s in segs) or 1)
    for a, b, d in segs:
        if alvo <= d or (a, b, d) == segs[-1]:
            u = alvo / d if d else 0
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        alvo -= d


def na_rua(trechos, n):
    """Trecho e fração pela faixa do lado do número; sem número ou sem faixa, o meio da rua."""
    if n is not None:
        lado = 'par' if n % 2 == 0 else 'imp'
        com_faixa = [t for t in trechos if t[lado] != (0, 0)]
        if com_faixa:
            def dist(t):
                lo, hi = sorted(t[lado])
                return 0 if lo <= n <= hi else min(abs(n - lo), abs(n - hi))
            t = min(com_faixa, key=dist)
            a, b = t[lado]
            return t, (0.5 if a == b else min(1, max(0, (n - a) / (b - a)))), 'na faixa' if dist(t) == 0 else 'fora da faixa'
    return trechos[len(trechos) // 2], 0.5, 'meio da rua'


def km(p, q):
    return math.hypot((p[0] - q[0]) * 102.6, (p[1] - q[1]) * 110.6)      # graus -> km na latitude do Rio


def mais_perto(k, declarado):
    """Dos bairros onde a rua existe, aquele em que ela passa mais perto do bairro declarado, se a até VIZINHO km."""
    vs = vertices.get(declarado)
    if not vs:
        return None
    perto = []
    for b in bairros_da_rua.get(k, ()):
        pts = [c for t in por_rb[(k, b)] for c in t['g']]
        perto.append((min(km(p, v) for p in pts[::max(1, len(pts) // 50)] for v in vs), b))
    return min(perto)[1] if perto and min(perto)[0] <= VIZINHO else None


# centro de cada bairro: o meio de trecho do bairro mais perto da média dos meios de trecho dele
meios = defaultdict(list)
for (k, b), ts in por_rb.items():
    meios[b] += [ponto(t['g'], .5) for t in ts]
centro = {}
for b, ps in meios.items():
    m = (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
    centro[b] = min(ps, key=lambda p: km(p, m))


df = pd.read_csv(CATEGORIAS, dtype=str, keep_default_na=False)
saida = []
for r in df.itertuples():
    k, b = chave(r.logradouro), nome_bairro(r.bairro)
    como = 'rua no bairro'
    if (k, b) not in por_rb:
        b, como = mais_perto(k, b), 'rua no bairro vizinho'
    if not b:
        declarado = nome_bairro(r.bairro)
        if declarado in vertices and declarado in centro:
            x, y = centro[declarado]
            saida.append((r.cnpj, 'centro do bairro', 'centro do bairro', round(x, 6), round(y, 6), bairro_do_ponto(x, y)))
        else:
            saida.append((r.cnpj, 'não casou', '', '', '', ''))
        continue
    t, f, onde = na_rua(por_rb[(k, b)], numero(r.numero))
    x, y = ponto(t['g'], f)
    saida.append((r.cnpj, como, onde, round(x, 6), round(y, 6), bairro_do_ponto(x, y)))
g = pd.DataFrame(saida, columns=['cnpj', 'como', 'posicao', 'lon', 'lat', 'bairro_mapa'])
df = df.merge(g, on='cnpj')

print('comércios:', len(df))
print(df.como.value_counts().to_string())
print(df[df.como != 'não casou'].posicao.value_counts().to_string())
ok = df[df.como != 'não casou']
print('ponto fora da malha de bairros:', (ok.bairro_mapa == '').sum())
for c in ['rua no bairro', 'rua no bairro vizinho', 'centro do bairro']:
    s = ok[ok.como == c]
    print(f'{c}: {len(s)}; o ponto cai no bairro declarado em '
          f'{(s.bairro.map(nome_bairro) == s.bairro_mapa.map(nome_bairro)).mean():.1%}')
df = df[df.como != 'não casou']
df.to_csv(GEO, index=False)
print('salvo:', GEO, len(df))
