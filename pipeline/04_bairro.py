"""Etapa 4: comércio de bairro. Tira redes, marcas e lojas de shopping -> dados/intermediarios/bairro.csv

Regras (METODOLOGIA.md, etapa 4):
- rede: a mesma empresa (raiz do CNPJ, 8 dígitos) em 3 ou mais lojas;
- marca: o mesmo nome em 5 ou mais empresas diferentes (Cacau Show, Óticas Carol, Fábrica de Bolo Vó Alzira), e as
  variantes que começam pelo nome da marca, se ele tem duas palavras ou mais ("CACAU SHOW MARACANA");
- shopping: endereço com 30 ou mais comércios em que pelo menos 35% são rede ou marca.
Os que saem vão para bairro_excluidos.csv, com o motivo.
Uso: python pipeline/04_bairro.py
"""
import pandas as pd

from caminhos import NOMES, BAIRRO, BAIRRO_EXCLUIDOS
from pessoas import norm

REDE, MARCA = 3, 5
SHOPPING, PARTE_CADEIA = 30, .35
RUIDO = set('LTDA ME EIRELI EPP SA S A CIA SLU MEI LTD'.split())

df = pd.read_csv(NOMES, dtype=str, keep_default_na=False)
print('nomes (etapa 3):', len(df))

marca_de = df.nome_fantasia.map(lambda n: ' '.join(w for w in norm(n).split() if w not in RUIDO))  # "X LTDA" = "X"
raiz = df.cnpj.str[:8]
rede = raiz.map(raiz.value_counts()) >= REDE

empresas = pd.DataFrame({'m': marca_de, 'r': raiz}).groupby('m').r.nunique()
marcas = set(empresas[empresas >= MARCA].index)
# variantes com sufixo de lugar ("CACAU SHOW MARACANA", "FABRICA DE BOLO VO ALZIRA - PIEDADE") são da marca,
# quando a marca tem duas palavras ou mais
longas = sorted(m for m in marcas if ' ' in m)
marca = marca_de.map(lambda n: n in marcas or any(n.startswith(m + ' ') for m in longas))

# endereço: logradouro + o primeiro número sem zeros à esquerda ("AVENIDA DAS AMERICAS 4666")
numero = df.numero.str.extract(r'(\d+)')[0].fillna('').str.lstrip('0')
endereco = (df.logradouro.map(norm) + ' ' + numero).str.strip()
por_end = pd.DataFrame({'e': endereco, 'c': rede | marca}).groupby('e').c.agg(['size', 'mean'])
shoppings = set(por_end[(por_end['size'] >= SHOPPING) & (por_end['mean'] >= PARTE_CADEIA)].index)
shopping = endereco.isin(shoppings)
print('endereços de shopping:', len(shoppings))

motivo = pd.Series('', index=df.index)
motivo[shopping] = 'shopping'
motivo[marca] = 'marca'
motivo[rede] = 'rede'

print('saem:', (motivo != '').sum())
print(motivo[motivo != ''].value_counts().to_string())
df['motivo'] = motivo
df[motivo != ''].to_csv(BAIRRO_EXCLUIDOS, index=False)
df = df[motivo == ''].drop(columns='motivo')
print('ficam:', len(df))
df.to_csv(BAIRRO, index=False)
print('salvos:', BAIRRO, BAIRRO_EXCLUIDOS)
