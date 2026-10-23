# Pipeline do Nomes fantasia. Cada passo grava num arquivo; o make só refaz o que mudou.
#   make baixar PROJETO=seu-projeto-gcp   baixa os CNPJs (BigQuery) e os mapas da Prefeitura
#   make site                             refaz docs/dados.json e docs/lugares.json a partir do que foi baixado
#   make servir                           abre o site em http://localhost:8000
PY ?= python3
B = dados/brutos
I = dados/intermediarios

.PHONY: baixar site servir

baixar: $(B)/cnpj_rio.csv $(B)/trechos.json

$(B)/cnpj_rio.csv: pipeline/01_cnpj_rio.sql
	$(PY) pipeline/01_baixa_cnpj.py --projeto $(PROJETO)

$(B)/trechos.json $(B)/logradouros.csv $(B)/bairros.geojson:
	$(PY) pipeline/02_baixa_datario.py

$(I)/comercios_rua.csv: $(B)/cnpj_rio.csv pipeline/03_comercio_rua.py
	$(PY) pipeline/03_comercio_rua.py

$(I)/cnpj_geo.csv: $(B)/cnpj_rio.csv $(B)/trechos.json $(B)/logradouros.csv pipeline/04_geocodifica.py
	$(PY) pipeline/04_geocodifica.py

site: $(I)/comercios_rua.csv $(I)/cnpj_geo.csv $(B)/bairros.geojson
	$(PY) pipeline/05_exporta.py

servir:
	$(PY) -m http.server 8000 --directory docs
