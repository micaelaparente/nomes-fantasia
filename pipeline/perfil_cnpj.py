"""Retrato do bruto de CNPJ (dados/brutos/cnpj_rio.csv): situação cadastral, vazios, datas, CNAE, endereço e nomes.

Não grava nada; só mede. Uso: python pipeline/perfil_cnpj.py
"""
import sys
from pathlib import Path

import pandas as pd

BRUTO = Path(__file__).resolve().parent.parent / 'dados' / 'brutos' / 'cnpj_rio.csv'

df = pd.read_csv(BRUTO, dtype=str, keep_default_na=False)
N = len(df)


def pct(n, d=N):
    return f'{n:>9,} ({n / d:6.1%})'.replace(',', '.')


print('linhas:', N, '| colunas:', list(df.columns))

print('\n# chave')
print('cnpj com 14 dígitos:', pct(df.cnpj.str.fullmatch(r'\d{14}').sum()))
print('cnpj repetido:      ', pct(df.cnpj.duplicated().sum()))
print('raízes (8 dígitos): ', f'{df.cnpj.str[:8].nunique():,}'.replace(',', '.'))
print('matriz (ordem 0001):', pct((df.cnpj.str[8:12] == '0001').sum()))

print('\n# vazios por coluna')
for c in df.columns:
    print(f'  {c:<18}', pct((df[c].str.strip() == '').sum()))

print('\n# situação cadastral (1 nula, 2 ativa, 3 suspensa, 4 inapta, 8 baixada)')
print(df.situacao_cadastral.value_counts().to_string())

ativos = df[df.situacao_cadastral == '2']
com_nome = ativos[ativos.nome_fantasia.str.strip() != '']
print('\nativos:', pct(len(ativos)), '| ativos com nome fantasia:', pct(len(com_nome), len(ativos)))

print('\n# datas')
print('inicio: ', df.inicio.min(), '→', df.inicio.max())
f = df.fim[df.fim != '']
print('fim:    ', f.min(), '→', f.max(), '| fim preenchido em ativo:', (ativos.fim != '').sum())
print('aberturas por ano (ativos com nome, últimos 8):')
print(com_nome.inicio.str[:4].value_counts().sort_index().tail(8).to_string())

print('\n# CNAE principal (ativos com nome): 2 primeiros dígitos, top 15')
print(com_nome.cnae.str[:2].value_counts().head(15).to_string())
print('cnae fora do padrão de 7 dígitos:', (~df.cnae.str.fullmatch(r'\d{7}')).sum())

print('\n# endereço (ativos com nome)')
print('numero sem dígito:  ', pct((~com_nome.numero.str.contains(r'\d')).sum(), len(com_nome)))
print('numero "SN"/"S/N":  ', pct(com_nome.numero.str.upper().str.replace(r'\W', '', regex=True).isin(['SN']).sum(), len(com_nome)))
print('cep fora de 8 díg.: ', pct((~com_nome.cep.str.fullmatch(r'\d{8}')).sum(), len(com_nome)))
print('cep fora do Rio (20000000-23799999):',
      pct((~com_nome.cep.str.fullmatch(r'2[0-3]\d{6}')).sum(), len(com_nome)))
print('bairro imputado:    ', pct((com_nome.bairro_imputado == 'true').sum(), len(com_nome)))
print('bairros distintos:  ', com_nome.bairro.nunique())
print('top 10 tipos de logradouro:')
print(com_nome.logradouro.str.split().str[0].value_counts().head(10).to_string())

print('\n# nome fantasia (ativos com nome)')
nf = com_nome.nome_fantasia
print('com minúscula:      ', pct(nf.str.contains(r'[a-z]').sum(), len(com_nome)))
print('com acento:         ', pct(nf.str.contains(r'[À-ÿ]').sum(), len(com_nome)))
print('com 11 dígitos (CPF de MEI):', pct(nf.str.contains(r'\d{11}').sum(), len(com_nome)))
print('nomes distintos:    ', f'{nf.str.upper().str.strip().nunique():,}'.replace(',', '.'))
print('mais repetidos:')
print(nf.str.upper().str.strip().value_counts().head(15).to_string())
