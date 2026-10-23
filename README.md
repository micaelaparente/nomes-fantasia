# Nomes fantasia

**Uma homenagem à criatividade do carioca em dar nome a comércios de rua.**

Site: https://micaelaparente.github.io/nomes-fantasia/

Um mapa do Rio de Janeiro feito com os letreiros do comércio de bairro. Os nomes aparecem pouco a pouco em volta do mapa, cada um ligado ao lugar onde fica; dá para filtrar por tipo de nome e chegar mais perto de uma região. São cinco capítulos:

| Capítulo | Tipos de nome |
|---|---|
| Lojões e lojinhas | Ãos · Inhos e inhas |
| Frases feitas | Chamados · Promessas · Primeira pessoa · Interjeições |
| Sotaques | Inglês · Francês · Imigrantes · Sotaques do Brasil |
| Família | Avós · Pai e mãe · Tios · Irmãos e primos · Filhos e netos · Sogras e compadres |
| Fé | Santos · Aleluias · Axés · Deus no comando |

> Protótipo em revisão. A metodologia, os nomes de exemplo e a representação no mapa ainda vão passar por uma limpeza.

## De onde vêm os dados

- **CNPJ** (Receita Federal), pela [Base dos Dados](https://basedosdados.org) no BigQuery (`br_me_cnpj.estabelecimentos`): todos os estabelecimentos do município do Rio, com nome fantasia, atividade (CNAE), situação, endereço e bairro.
- **Logradouros e trechos de rua** (Instituto Pereira Passos / [data.rio](https://www.data.rio)), camada `CadLog/Trechos_Logradouros` do servidor de mapas da Prefeitura: a geometria de cada trecho de rua e a faixa de numeração de cada lado.
- **Limite de bairros** (IPP / data.rio), camada `Hosted/LimitedeBairroshosted`: o desenho dos bairros, com a área de planejamento e a região de planejamento de cada um.

## Metodologia

1. **Comércio de rua** (`03_comercio_rua.py`): CNPJs ativos, com nome fantasia, em atividades com fachada para a rua (varejo, bares e restaurantes, salões, oficinas, academias, consertos etc.; lista de CNAEs no script). Saem rótulos internos de rede ("FILIAL 449") e nomes que são só o nome de uma pessoa. **63.466 comércios.**
2. **Geocodificação** (`04_geocodifica.py`): cada endereço é casado com o trecho de rua do mesmo nome e bairro e posicionado pela numeração, do lado par ou ímpar. É uma aproximação: a numeração dos trechos não é uniforme.
3. **Comércio de bairro** (`05_exporta.py`): pequenos negócios com fachada para a rua, **fora redes** (a mesma empresa, isto é, a mesma raiz de CNPJ, em 3 ou mais lojas), **franquias** (o mesmo nome de marca em 3 ou mais empresas), bancos, cinemas, hotéis e shoppings. **50.584 comércios** no mapa.
4. **Classificação dos nomes** (`vozes.py`, com léxicos de `sotaques.py`): por regras de linguagem (sufixos, léxicos, expressões). Cada nome pode ter tipos de capítulos diferentes; dentro da Fé e das Frases feitas, fica num só tipo. As regras erram, para mais e para menos.
5. **Mapa**: a cidade em quadradinhos de 750 m. A cor de cada quadradinho é o tipo que mais pesa ali comparado à média da cidade (os vizinhos contam metade, para poucos casos não piscarem), e fica mais forte quanto mais acima da média. Regiões: as cinco áreas de planejamento da Prefeitura, com a Grande Tijuca separada da Zona Sul (seis no total).
6. **Nomes que aparecem**: na cidade, uma seleção curada (`SEQUENCIAS` em `05_exporta.py`); numa região, primeiro os curados que caem nela e depois até seis nomes reais por tipo e bairro. O tipo do comércio que aparece junto do bairro é a atividade declarada à Receita (`cnae.py`), não necessariamente o que a loja vende hoje.

**Limites.** A base é de comércios ativos: os que fecharam não aparecem. A classificação é por regras, sem leitura humana de cada nome. As contagens são pequenas fora da escala da cidade; por isso o site fala em palavras ("bem mais comum que no resto da cidade") e não mostra números.

## Como refazer os dados

Requisitos: Python 3.8+, `pip install -r requirements.txt` e, para baixar os CNPJs, um projeto no Google Cloud com BigQuery (`gcloud auth application-default login`).

```bash
make baixar PROJETO=seu-projeto-gcp   # 01 e 02: CNPJs do BigQuery e mapas da Prefeitura -> dados/brutos/
make site                             # 03, 04 e 05: -> dados/intermediarios/ e docs/dados.json, docs/lugares.json
make servir                           # http://localhost:8000
```

Sem o Python do BigQuery, dá para rodar `pipeline/01_cnpj_rio.sql` no console do BigQuery e salvar o resultado em `dados/brutos/cnpj_rio.csv`. A consulta foi **reconstruída** (a original não foi guardada); vale conferir o resultado.

| Passo | Lê | Grava |
|---|---|---|
| `01_baixa_cnpj.py` + `01_cnpj_rio.sql` | BigQuery | `dados/brutos/cnpj_rio.csv` |
| `02_baixa_datario.py` | servidor de mapas da Prefeitura | `dados/brutos/logradouros.csv`, `trechos.json`, `bairros.geojson` |
| `03_comercio_rua.py` | `cnpj_rio.csv` | `dados/intermediarios/comercios_rua.csv` |
| `04_geocodifica.py` | `cnpj_rio.csv`, logradouros e trechos | `dados/intermediarios/cnpj_geo.csv` |
| `05_exporta.py` | comércios, geocodificação e bairros | `docs/dados.json`, `docs/lugares.json` |

`dados/` fica fora do git (os arquivos passam de 100 MB). O site em `docs/` é uma versão estática, publicada pelo GitHub Pages.

**Baixar de novo não dá exatamente o mesmo site.** A versão de `docs/` foi feita com o extrato de CNPJ de 21/10/2026 e com cópias antigas dos mapas da Prefeitura; com esses arquivos, os passos 03 a 05 reproduzem `docs/` byte a byte. Com os mapas baixados hoje pelo passo 02, o resultado muda pouco (50.564 comércios no mapa em vez de 50.584; os bairros de destaque continuam os mesmos), por duas razões:
- o servidor tem 65 trechos de rua a mais que a cópia antiga;
- a camada de bairros do servidor não tem Argentino nem Ingleses e junta Imperial de São Cristóvão em São Cristóvão, enquanto o cadastro de logradouros usa os nomes novos. Vale tratar isso (como em `GRAFIA`, no `05_exporta.py`) antes de republicar.

## Estrutura

```
pipeline/   scripts numerados, regras de classificação (vozes.py, sotaques.py) e rótulos de CNAE (cnae.py)
docs/       o site: index.html (sem build, sem dependências) e os dois JSON que ele lê
dados/      brutos/ e intermediarios/, criados pelo pipeline
```
