"""Baixa os CNPJs do Rio do BigQuery (Base dos Dados) -> dados/brutos/cnpj_rio.csv

Uso: python pipeline/baixa_cnpj.py --projeto SEU_PROJETO_GCP
Precisa de um projeto no Google Cloud com faturamento (a consulta lê ~1 GB; cabe na cota gratuita mensal) e de login:
gcloud auth application-default login
Sem Python/BigQuery: rode cnpj_rio.sql no console do BigQuery e salve o resultado como dados/brutos/cnpj_rio.csv.
"""
import argparse
from pathlib import Path
from caminhos import CNPJ_RIO

from google.cloud import bigquery

p = argparse.ArgumentParser()
p.add_argument('--projeto', required=True, help='projeto do Google Cloud que paga a consulta')
args = p.parse_args()

sql = (Path(__file__).parent / 'cnpj_rio.sql').read_text()
df = bigquery.Client(project=args.projeto).query(sql).to_dataframe()
df.to_csv(CNPJ_RIO, index=False)
print('salvo:', CNPJ_RIO, len(df), 'CNPJs')
