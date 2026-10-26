"""Etapa 7: exportação. Os dados do site -> docs/dados.json e docs/lugares.json (os dois arquivos que o site lê)

Regras (METODOLOGIA.md, etapa 7):
- o mapa é a cidade em quadradinhos de GRADE metros; a grade usa só os pontos de rua (os de centro de bairro se
  acumulariam num quadradinho só);
- bairros, regiões, ranking e comparação usam todos os comércios, pelo bairro onde o ponto cai;
- ranking: bairros com 150+ comércios e 5+ casos do tipo (3+ nos tipos com menos de 150 na cidade); entre regiões
  de planejamento, as que têm 600+ comércios e 3+ casos.
dados.json: grade (total e contagem por tipo em cada quadradinho), ranking (bairros onde cada tipo mais pesa, contra
a média da cidade, e o contraste entre regiões), comparacao (quantidade e peso de cada tipo nas seis regiões), centros
dos bairros e das regiões, e as sequencias de nomes de destaque.
lugares.json: bairros (região, total e contagem por tipo), o bairro de cada quadradinho e até POR_BAIRRO nomes reais por
tipo e bairro.
Uso: python pipeline/07_exporta.py
"""
import json
import math
import os
from collections import Counter, defaultdict
from difflib import SequenceMatcher

import pandas as pd

from caminhos import BAIRROS, GEO, SITE
from categorias import CONCEITOS
from cnae import rotulo as tipo_cnae
from pessoas import norm
from sequencias import SEQUENCIAS

LON0, LAT0 = -43.80, -22.74
KX = math.cos(math.radians(22.9)) * 111320
KY = 110540
GRADE = 750
POR_BAIRRO = 6
SUBS = [s for subs in CONCEITOS.values() for s in subs]
# quando um nome tem dois graus, qual vale (Os Filhos da Mãe é dos filhos, não da mãe)
PRIORIDADE = {'familia': ['avos', 'tios', 'irmaos', 'filhos', 'agregados', 'pais']}
# seis regiões: as cinco Áreas de Planejamento da Prefeitura, com a AP 2 dividida em Zona Sul e Grande Tijuca
REGIOES = ['Centro', 'Zona Sul', 'Grande Tijuca', 'Zona Norte', 'Barra e Jacarepaguá', 'Zona Oeste']
AP = {'1': 'Centro', '3': 'Zona Norte', '4': 'Barra e Jacarepaguá', '5': 'Zona Oeste'}
RUIDO = set('LTDA ME EIRELI EPP SA S A CIA SLU MEI LTD'.split())
# contam no mapa, mas não vão aos nomes mostrados: "Fulano Coiffeur" é a fórmula de um terço do francês
NAO_MOSTRA = {'frances': set('COIFFEUR COIFFEURS COIFEUR COIFFURE'.split())}


def limpa(nome):
    return ' '.join(w for w in norm(nome).split() if w not in RUIDO)


def xy(lon, lat):
    return round((lon - LON0) * KX), round((LAT0 - lat) * KY)


malha = json.load(open(BAIRROS))['features']
RP = {f['properties']['nome'].strip(): f['properties']['rp'] for f in malha}
APB = {f['properties']['nome'].strip(): f['properties']['area_plane'].strip() for f in malha}


def regiao(b):
    ap = APB.get(b)
    if ap == '2':
        return 'Grande Tijuca' if RP[b] == 'Tijuca' else 'Zona Sul'
    return AP.get(ap)


df = pd.read_csv(GEO, dtype=str, keep_default_na=False)
df = df[df.bairro_mapa != '']
df['subs'] = df.categorias.map(lambda c: set(c.split(';')) & set(SUBS))   # só os tipos dos capítulos do site
df['nome'] = df.nome_fantasia.map(limpa)
df['x'], df['y'] = zip(*[xy(float(a), float(b)) for a, b in zip(df.lon, df.lat)])
df['rua'] = df.posicao != 'centro do bairro'

celulas = defaultdict(lambda: [0] * (1 + len(SUBS)))
cel_b = defaultdict(Counter)                    # quantos comércios de cada bairro caem em cada quadradinho
pool = defaultdict(lambda: defaultdict(dict))   # nomes reais por tipo e bairro, para explorar lugares
tot_b, tot_rp, sub_b, sub_rp = Counter(), Counter(), defaultdict(Counter), defaultdict(Counter)
xy_b, ap_xy, por_nome, cont = defaultdict(lambda: [0, 0, 0]), defaultdict(lambda: [0, 0, 0]), {}, Counter()
tot_ap, sub_ap = Counter(), defaultdict(Counter)
for r in df.itertuples():
    b, rp, ap = r.bairro_mapa, RP.get(r.bairro_mapa), regiao(r.bairro_mapa)
    tot_b[b] += 1
    if rp:
        tot_rp[rp] += 1
    if ap:
        tot_ap[ap] += 1
    if r.rua:
        cel = (r.x // GRADE, r.y // GRADE)
        celulas[cel][0] += 1
        cel_b[cel][b] += 1
        xy_b[b][0] += r.x; xy_b[b][1] += r.y; xy_b[b][2] += 1
        if ap:
            ap_xy[ap][0] += r.x; ap_xy[ap][1] += r.y; ap_xy[ap][2] += 1
    for s in r.subs:
        if r.rua:
            celulas[cel][1 + SUBS.index(s)] += 1
        sub_b[s][b] += 1
        cont[s] += 1
        if rp:
            sub_rp[s][rp] += 1
        if ap:
            sub_ap[s][ap] += 1
        if not NAO_MOSTRA.get(s, set()) & set(r.nome.split()):
            pool[s][b].setdefault(r.nome, (r.x, r.y, tipo_cnae(r.cnae)))
    por_nome.setdefault(r.nome, (r.x, r.y, b, tipo_cnae(r.cnae)))
N = sum(tot_b.values())
print('comércios', N, '| na grade', sum(c[0] for c in celulas.values()), '| quadradinhos', len(celulas))
print(dict(cont))

# ranking por bairro (mín. 150 comércios e 5 casos; 3 nos tipos com menos de 150) e contraste entre regiões
ranking = {}
for s in SUBS:
    taxa, minimo = cont[s] / N, 5 if cont[s] >= 150 else 3
    bs = sorted(((sub_b[s][b] / tot_b[b]) / taxa, b) for b in sub_b[s] if tot_b[b] >= 150 and sub_b[s][b] >= minimo)[::-1]
    reg = {rp: sub_rp[s][rp] / n for rp, n in tot_rp.items() if n >= 600 and sub_rp[s][rp] >= 3}
    # o site não usa alto/baixo; nos tipos pequenos (Sogras e compadres) nenhuma região tem casos suficientes
    alto, baixo = (max(reg, key=reg.get), min(reg, key=reg.get)) if reg else (None, None)
    ranking[s] = {'total': cont[s], 'umEm': round(1 / taxa),
                  'bairros': [[b, round(i, 1), sub_b[s][b], round(tot_b[b] / sub_b[s][b])] for i, b in bs[:5]],
                  'alto': [alto, round(1 / reg[alto])] if alto else None,
                  'baixo': [baixo, round(1 / reg[baixo])] if baixo else None}
    print(s, [(b[0], b[1]) for b in ranking[s]['bairros'][:3]], '| região', alto, '×', baixo)

centros = {b: [round(v[0] / v[2]), round(v[1] / v[2])] for b, v in xy_b.items() if v[2]}

sequencias = {}
for conceito, caps in SEQUENCIAS.items():
    sequencias[conceito] = []
    for rotulo, *nomes in caps:
        itens = []
        for dado, exib in nomes:
            p = por_nome.get(limpa(dado))
            if p is None:
                print('não achado:', conceito, dado)
                continue
            subs = df.loc[df.nome == limpa(dado), 'subs'].iloc[0] & set(CONCEITOS[conceito])
            sub = next((x for x in PRIORIDADE.get(conceito, CONCEITOS[conceito]) if x in subs), None)
            if sub is None:
                print('sem tipo no capítulo:', conceito, dado)
                sub = CONCEITOS[conceito][0]
            itens.append([p[0], p[1], exib, p[2], sub, p[3]])
        sequencias[conceito].append([rotulo, itens])

comparacao = {s: [[r, sub_ap[s][r], tot_ap[r]] for r in REGIOES] for s in SUBS}
grade = [[ix, iy] + c for (ix, iy), c in celulas.items()]
regioes = [[round(ap_xy[r][0] / ap_xy[r][2]), round(ap_xy[r][1] / ap_xy[r][2]), r] for r in REGIOES]

os.makedirs(SITE, exist_ok=True)
json.dump({'conceitos': CONCEITOS, 'subs': SUBS, 'grade_m': GRADE, 'grade': grade, 'regioes': regioes,
           'ranking': ranking, 'centros': centros, 'sequencias': sequencias, 'comparacao': comparacao},
          open(SITE / 'dados.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('dados.json', round(os.path.getsize(SITE / 'dados.json') / 1e3), 'KB')

nomes_b = sorted(b for b in tot_b if b in APB)
idx_b = {b: i for i, b in enumerate(nomes_b)}
bairros = {b: [regiao(b) or '', tot_b[b], [sub_b[s][b] for s in SUBS]] for b in nomes_b}
celula_bairro = [idx_b.get(cel_b[k].most_common(1)[0][0], -1) for k in celulas]


def escolhe(cands):
    """Os mais legíveis primeiro, sem quase-repetidos (FABRICA / FRABRICA DE BOLO VO ALZIRA)."""
    out = []
    for n, (x, y, t) in sorted(cands.items(), key=lambda kv: (abs(len(kv[0]) - 16), kv[0])):
        if 4 <= len(n) <= 30 and not any(SequenceMatcher(None, n, o[0]).ratio() > .8 for o in out):
            out.append([n, x, y, t])
        if len(out) == POR_BAIRRO:
            break
    return out


nomes = {s: {b: escolhe(pool[s][b]) for b in pool[s] if b in idx_b} for s in SUBS}
json.dump({'bairros': bairros, 'celula_bairro': [nomes_b, celula_bairro], 'nomes': nomes},
          open(SITE / 'lugares.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('lugares.json', round(os.path.getsize(SITE / 'lugares.json') / 1e3), 'KB')
