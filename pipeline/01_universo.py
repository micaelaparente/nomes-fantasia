"""Etapa 1: o universo. CNPJs ativos com nome fantasia de verdade -> dados/intermediarios/universo.csv

Regras (METODOLOGIA.md, etapa 1):
- só situação cadastral 2 (ativa); inaptas, suspensas, baixadas e nulas ficam de fora;
- nome fantasia com pelo menos uma letra ("****", "-", "." não são nome);
- as fechadas desde 2021, que vêm no bruto, não são usadas.
Uso: python pipeline/01_universo.py
"""
import pandas as pd

from caminhos import CNPJ_RIO, UNIVERSO

df = pd.read_csv(CNPJ_RIO, dtype=str, keep_default_na=False)
print('bruto:', len(df))

df = df[df.situacao_cadastral == '2']
print('ativos:', len(df))

df = df[df.nome_fantasia.str.contains('[A-Za-z]')]
print('com nome fantasia (ao menos uma letra):', len(df))

df.drop(columns=['situacao_cadastral', 'fim']).to_csv(UNIVERSO, index=False)
print('salvo:', UNIVERSO)
