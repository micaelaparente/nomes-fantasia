"""Onde ficam os arquivos do pipeline, relativos à raiz do repositório.

dados/brutos         o que se baixa (CNPJ do BigQuery, logradouros e bairros do data.rio); fora do git
dados/intermediarios o que o pipeline produz no meio do caminho; fora do git
docs                 o site estático (GitHub Pages): index.html, dados.json, lugares.json
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / 'dados' / 'brutos'
INTER = RAIZ / 'dados' / 'intermediarios'
SITE = RAIZ / 'docs'

CNPJ_RIO = BRUTOS / 'cnpj_rio.csv'            # 01: todos os CNPJs do município, de qualquer situação
LOGRADOUROS = BRUTOS / 'logradouros.csv'      # 02: cadastro dos trechos de logradouro (faixas de numeração)
TRECHOS = BRUTOS / 'trechos.json'             # 02: geometria dos trechos, [cod_trecho, tipo, coordenadas lon/lat]
BAIRROS = BRUTOS / 'bairros.geojson'          # 02: limite de bairros, com região de planejamento
COMERCIOS = INTER / 'comercios_rua.csv'       # 03: comércio de rua ativo, com nome fantasia, sem nomes de pessoa
GEO = INTER / 'cnpj_geo.csv'                  # 04: CNPJs geocodificados nos trechos

for d in (BRUTOS, INTER, SITE):
    d.mkdir(parents=True, exist_ok=True)
