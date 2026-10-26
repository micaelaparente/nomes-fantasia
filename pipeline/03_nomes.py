"""Etapa 3: nomes. Tira os nomes que identificam uma pessoa -> dados/intermediarios/nomes.csv

Regras (METODOLOGIA.md, etapa 3): sai o nome com CPF, o que é só nome de pessoa e o que traz um nome completo em
marca pessoal (regras em pessoas.py). Os que saem vão para nomes_excluidos.csv, com o motivo, para conferir.
Uso: python pipeline/03_nomes.py
"""
from collections import Counter

import pandas as pd

from caminhos import ATIVIDADE, UNIVERSO, NOMES, NOMES_EXCLUIDOS
from pessoas import motivo_pessoa, norm

df = pd.read_csv(ATIVIDADE, dtype=str, keep_default_na=False)
print('atividade (etapa 2):', len(df))

# em quantos nomes do universo cada palavra aparece: palavra rara depois de um prenome sugere sobrenome
freq = Counter(w for n in pd.read_csv(UNIVERSO, dtype=str, keep_default_na=False, usecols=['nome_fantasia']).nome_fantasia
               for w in set(norm(n).split()))
df['motivo'] = df.nome_fantasia.map(lambda n: motivo_pessoa(n, freq) or '')

sai = df.motivo != ''
print('saem:', sai.sum())
print(df.motivo[sai].value_counts().to_string())
df[sai].to_csv(NOMES_EXCLUIDOS, index=False)
df = df[~sai].drop(columns='motivo')
print('ficam:', len(df))
df.to_csv(NOMES, index=False)
print('salvos:', NOMES, NOMES_EXCLUIDOS)
