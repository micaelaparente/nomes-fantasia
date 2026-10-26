"""Etapa 5: categorias. Cada comércio de bairro com as categorias do nome -> dados/intermediarios/categorias.csv

Regras em categorias.py (METODOLOGIA.md, etapa 5). Coluna categorias: as categorias separadas por ";" (vazia se nenhuma).
Uso: python pipeline/05_categorias.py
"""
from collections import Counter

import pandas as pd

from caminhos import BAIRRO, CATEGORIAS
from categorias import categorias

df = pd.read_csv(BAIRRO, dtype=str, keep_default_na=False)
cats = df.nome_fantasia.map(categorias)
df['categorias'] = cats.map(lambda c: ';'.join(sorted(c)))

print('comércios:', len(df), '| com alguma categoria:', (df.categorias != '').sum())
print(Counter(c for cs in cats for c in cs).most_common())
df.to_csv(CATEGORIAS, index=False)
print('salvo:', CATEGORIAS)
