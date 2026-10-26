"""Onde ficam os arquivos do pipeline, relativos à raiz do repositório.

dados/brutos         o que se baixa (CNPJ da Receita, ruas e bairros da Prefeitura); fora do git
dados/intermediarios o que o pipeline produz no meio do caminho; fora do git
docs                 o site estático (GitHub Pages): index.html, dados.json, lugares.json
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / 'dados' / 'brutos'
INTER = RAIZ / 'dados' / 'intermediarios'
SITE = RAIZ / 'docs'

CNPJ_RIO = BRUTOS / 'cnpj_rio.csv'          # baixa_cnpj.py: CNPJs do município, ativos e fechados desde 2021
LOGRADOUROS = BRUTOS / 'logradouros.csv'    # baixa_datario.py: cadastro de trechos de rua, com as faixas de numeração
TRECHOS = BRUTOS / 'trechos.json'           # baixa_datario.py: geometria dos trechos, [cod_trecho, tipo, coordenadas lon/lat]
BAIRROS = BRUTOS / 'bairros.geojson'        # baixa_datario.py: limite dos bairros, com área e região de planejamento

UNIVERSO = INTER / 'universo.csv'           # 01: ativos com nome fantasia
ATIVIDADE = INTER / 'atividade.csv'         # 02: atividades com fachada para a rua, com o grupo
NOMES = INTER / 'nomes.csv'                 # 03: sem nomes que identificam uma pessoa
NOMES_EXCLUIDOS = INTER / 'nomes_excluidos.csv'    # 03: os que saíram, com o motivo
BAIRRO = INTER / 'bairro.csv'               # 04: comércio de bairro, sem redes, marcas e lojas de shopping
BAIRRO_EXCLUIDOS = INTER / 'bairro_excluidos.csv'  # 04: os que saíram, com o motivo
CATEGORIAS = INTER / 'categorias.csv'       # 05: com as categorias do nome
GEO = INTER / 'geo.csv'                     # 06: com ponto (lon/lat) e o bairro onde o ponto cai

for d in (BRUTOS, INTER, SITE):
    d.mkdir(parents=True, exist_ok=True)
