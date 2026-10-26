"""Baixa do servidor de mapas da Prefeitura do Rio (IPP / data.rio) -> dados/brutos/

- logradouros.csv e trechos.json: a camada CadLog/Trechos_Logradouros (cadastro com as faixas de numeração de cada
  trecho de rua, e a geometria do trecho em lon/lat);
- bairros.geojson: a camada Hosted/LimitedeBairroshosted (limite dos bairros, com área e região de planejamento).

Uso: python pipeline/baixa_datario.py   (só biblioteca padrão; leva alguns minutos)
"""
import csv, json, time, urllib.parse, urllib.request
from caminhos import LOGRADOUROS, TRECHOS, BAIRROS

SERVIDOR = 'https://pgeo3.rio.rj.gov.br/arcgis/rest/services/'
TRECHOS_URL = SERVIDOR + 'CadLog/Trechos_Logradouros/FeatureServer/0/query'
BAIRROS_URL = SERVIDOR + 'Hosted/LimitedeBairroshosted/FeatureServer/0/query'
PAGINA = 2000


def pedir(url, **params):
    """GET com algumas tentativas: o servidor às vezes falha no meio de uma paginação longa."""
    q = url + '?' + urllib.parse.urlencode(params)
    for tentativa in range(5):
        try:
            with urllib.request.urlopen(q, timeout=120) as r:
                return json.load(r)
        except Exception as e:
            print('  falhou, tentando de novo:', e)
            time.sleep(3 * (tentativa + 1))
    raise RuntimeError('não consegui baixar ' + q)


def tudo(url, **params):
    """Todas as feições de uma camada, página a página, em ordem estável."""
    total = pedir(url, where='1=1', returnCountOnly='true', f='json')['count']
    feicoes = []
    while len(feicoes) < total:
        pg = pedir(url, where='1=1', outFields='*', outSR=4326, orderByFields='objectid', f='geojson',
                   resultOffset=len(feicoes), resultRecordCount=PAGINA, **params)['features']
        if not pg:
            break
        feicoes += pg
        print(f'  {len(feicoes)} de {total}')
    if len(feicoes) != total:
        raise RuntimeError(f'esperava {total} feições e vieram {len(feicoes)}')
    return feicoes


print('trechos de logradouro')
trechos = tudo(TRECHOS_URL)
campos = list(trechos[0]['properties'])
with open(LOGRADOUROS, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=campos)
    w.writeheader()
    for t in trechos:
        w.writerow(t['properties'])
arred = lambda c: [round(c[0], 5), round(c[1], 5)] if isinstance(c[0], (int, float)) else [arred(x) for x in c]
json.dump([[t['properties']['cod_trecho'], t['geometry']['type'], arred(t['geometry']['coordinates'])]
           for t in trechos if t.get('geometry')],
          open(TRECHOS, 'w'), separators=(',', ':'))
print('salvos:', LOGRADOUROS, TRECHOS, len(trechos), 'trechos')

print('limite de bairros')
bairros = tudo(BAIRROS_URL)
json.dump({'type': 'FeatureCollection', 'features': bairros}, open(BAIRROS, 'w'), ensure_ascii=False)
print('salvo:', BAIRROS, len(bairros), 'bairros')
