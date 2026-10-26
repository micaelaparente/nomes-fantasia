# Pipeline do Nomes fantasia. Cada passo grava num arquivo; o make só refaz o que mudou.
#   make baixar PROJETO=seu-projeto-gcp   baixa os CNPJs (BigQuery) e os mapas da Prefeitura
#   make site                             refaz docs/dados.json e docs/lugares.json a partir do que foi baixado
#   make servir                           abre o site em http://localhost:8000
PY ?= python3
B = dados/brutos
I = dados/intermediarios
P = pipeline

.PHONY: baixar site servir

baixar: $(B)/cnpj_rio.csv $(B)/trechos.json

$(B)/cnpj_rio.csv: $(P)/cnpj_rio.sql
	$(PY) $(P)/baixa_cnpj.py --projeto $(PROJETO)

$(B)/trechos.json $(B)/logradouros.csv $(B)/bairros.geojson:
	$(PY) $(P)/baixa_datario.py

$(I)/universo.csv: $(B)/cnpj_rio.csv $(P)/01_universo.py
	$(PY) $(P)/01_universo.py

$(I)/atividade.csv: $(I)/universo.csv $(P)/02_atividade.py
	$(PY) $(P)/02_atividade.py

$(I)/nomes.csv: $(I)/atividade.csv $(P)/03_nomes.py $(P)/pessoas.py
	$(PY) $(P)/03_nomes.py

$(I)/bairro.csv: $(I)/nomes.csv $(P)/04_bairro.py
	$(PY) $(P)/04_bairro.py

$(I)/categorias.csv: $(I)/bairro.csv $(P)/05_categorias.py $(P)/categorias.py
	$(PY) $(P)/05_categorias.py

$(I)/geo.csv: $(I)/categorias.csv $(B)/logradouros.csv $(B)/trechos.json $(B)/bairros.geojson $(P)/06_geocodifica.py
	$(PY) $(P)/06_geocodifica.py

site: $(I)/geo.csv $(P)/07_exporta.py $(P)/sequencias.py $(P)/cnae.py
	$(PY) $(P)/07_exporta.py

servir:
	$(PY) -m http.server 8000 --directory docs
