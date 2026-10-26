"""Etapa 2: atividade. Do universo, o comércio e os serviços com fachada para a rua -> dados/intermediarios/atividade.csv

Pela atividade principal (CNAE) declarada à Receita; os CNAEs secundários não contam (METODOLOGIA.md, etapa 2).
Cada prefixo casa com startswith; EXCETO tira subclasses de dentro de um prefixo incluído.
Uso: python pipeline/02_atividade.py
"""
import pandas as pd

from caminhos import UNIVERSO, ATIVIDADE

INCLUI = {
    'varejo': ['47'],
    'veículos': ['4511', '4520', '4530', '4541', '4543'],     # revendas, oficinas, lava-jato, autopeças, motos
    'comida': ['5611',                                         # restaurantes, lanchonetes, bares
               '5620104',                                      # marmitarias, pizzarias de entrega
               '1091101', '1091102',                           # padarias e confeitarias
               '1053800', '1094500'],                          # açaí e sorvete, massas
    'beleza e cuidados': ['9602', '9601', '9609208', '9609206'],  # salões, lavanderias, banho e tosa, tatuagem
    'bichos': ['7500', '9609207'],                             # veterinárias, hotel para pet
    'consertos': ['9511', '9512', '9521', '9529'],             # assistência técnica, sapateiro, chaveiro
    'serviços de balcão': ['8299706', '8219901', '7723300'],   # lotéricas, copiadoras, aluguel de roupas
    'lazer': ['9313', '9329801', '9329804'],                   # academias, danceterias, lan house e escape
    'funerárias': ['9603'],
}
EXCETO = {
    '9603301': 'gestão de cemitérios',
    '9603305': 'cursos de somatoconservação',
}
# bancos (6421, 6422), hotéis e hostels (5510, 5590601) e cinemas (5914) não entram: são redes, ou não são comércio de bairro

df = pd.read_csv(UNIVERSO, dtype=str, keep_default_na=False)
print('universo:', len(df))

grupo = pd.Series('', index=df.index)
for g, prefixos in INCLUI.items():
    grupo[(grupo == '') & df.cnae.str.startswith(tuple(prefixos))] = g
grupo[df.cnae.isin(EXCETO)] = ''
df['grupo'] = grupo
df = df[df.grupo != '']

print('comércio e serviços de rua:', len(df))
print(df.grupo.value_counts().to_string())
df.to_csv(ATIVIDADE, index=False)
print('salvo:', ATIVIDADE)
