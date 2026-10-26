# Nomes fantasia

**Uma homenagem à criatividade do carioca em dar nome a comércios de rua.**

Site: https://micaelaparente.github.io/nomes-fantasia/

Um mapa do Rio de Janeiro feito com os letreiros do comércio de bairro. Os nomes aparecem pouco a pouco em volta do mapa, cada um ligado ao lugar onde fica; dá para filtrar por tipo de nome e chegar mais perto de uma região. São cinco capítulos:

| Capítulo | Tipos de nome |
|---|---|
| Frases feitas | Chamados · Promessas · Primeira pessoa · Interjeições |
| Lojões e lojinhas | Ãos · Inhos e inhas |
| Família | Avós · Pai e mãe · Tios · Irmãos e primos · Filhos e netos · Sogras e compadres |
| Sotaques | Inglês · Francês · Sotaques do Brasil |
| Poder | Reis e rainhas · Impérios e palácios · República e patentes |

## De onde vêm os dados

- **CNPJ** (Receita Federal), pela [Base dos Dados](https://basedosdados.org) no BigQuery (`br_me_cnpj.estabelecimentos`, retrato de 11/01/2026): os estabelecimentos do município do Rio ativos ou fechados a partir de 2021, com nome fantasia, atividade (CNAE), situação, endereço e bairro (quando vazio, o mais frequente do mesmo CEP).
- **Logradouros e trechos de rua** (Instituto Pereira Passos / [data.rio](https://www.data.rio)), camada `CadLog/Trechos_Logradouros` do servidor de mapas da Prefeitura: a geometria de cada trecho de rua e a faixa de numeração de cada lado.
- **Limite de bairros** (IPP / data.rio), camada `Hosted/LimitedeBairroshosted`: o desenho dos bairros, com a área de planejamento e a região de planejamento de cada um.

As camadas da Prefeitura mudam com o tempo (trechos novos, bairros renomeados), então baixá-las em outra data dá números um pouco diferentes.

## Metodologia

Resumo; o detalhe de cada etapa, com os números de cada corte, está em [`pipeline/METODOLOGIA.md`](pipeline/METODOLOGIA.md).

1. **Universo** (`01_universo.py`): CNPJs ativos com nome fantasia. **223.908.**
2. **Atividade** (`02_atividade.py`): comércio e serviços com fachada para a rua, pela atividade principal (varejo, bares e restaurantes, padarias, salões, oficinas, consertos, academias, lotéricas etc.; lista de CNAEs no script). **64.338.**
3. **Nomes de pessoa** (`03_nomes.py`): saem os nomes que identificam uma pessoa (CPF, só nome de pessoa, nome completo em marca pessoal). **63.410.**
4. **Comércio de bairro** (`04_bairro.py`): saem **redes** (a mesma empresa em 3 ou mais lojas), **marcas** (o mesmo nome em 5 ou mais empresas) e **lojas de shopping** (endereço com 30 ou mais comércios, um terço ou mais de rede ou marca). **52.717.**
5. **Categorias** (`05_categorias.py`, regras em `categorias.py`): cada nome nos tipos dos cinco capítulos, por regras de linguagem (sufixos, léxicos, expressões). Palavras que são só o nome do que a loja é ou vende (Mercadinho, Pet Shop, Sushi) não contam. Um nome pode ter tipos de capítulos diferentes; nas Frases e no Poder, fica num só tipo.
6. **Geocodificação** (`06_geocodifica.py`): cada endereço é casado com o trecho de rua do mesmo nome e bairro (ou de um bairro vizinho) e posicionado pela numeração, do lado par ou ímpar; sem rua, vai para o centro do bairro declarado. O bairro do comércio é o do polígono onde o ponto cai. **52.179** com ponto.
7. **Exportação** (`07_exporta.py`): a cidade em quadradinhos de 750 m, só com os pontos de rua. A cor de cada quadradinho é o tipo que mais pesa ali comparado à média da cidade (os vizinhos contam metade, para poucos casos não piscarem), e fica mais forte quanto mais acima da média. Regiões: as cinco áreas de planejamento da Prefeitura, com a Grande Tijuca separada da Zona Sul.

**Nomes que aparecem:** na cidade, uma seleção feita à mão (`pipeline/sequencias.py`); numa região, primeiro os da seleção que caem nela e depois até seis nomes reais por tipo e bairro. Nos Sotaques, só aparecem os curiosos: a mistura de línguas ("Pet du Rapha", "Nilza's Modas") e a fala regional ("Arretado Bom Demais", "Mineira das Baterias"), e não a fórmula (`pipeline/destaques.py`). O tipo do comércio que aparece junto do bairro é a atividade declarada à Receita (`pipeline/cnae.py`), não necessariamente o que a loja vende hoje.

**Limites.** A base é de comércios ativos: os que fecharam não aparecem. A classificação é por regras, sem leitura humana de cada nome, e erra para mais e para menos. A Receita guarda os nomes sem acento, e os da seleção são reacentuados à mão. As contagens são pequenas fora da escala da cidade; por isso o site fala em palavras ("bem mais comum que no resto da cidade") e não mostra números.

## Como refazer os dados

Requisitos: Python 3.8+, `pip install -r requirements.txt` e, para baixar os CNPJs, um projeto no Google Cloud com BigQuery (`gcloud auth application-default login`).

```bash
make baixar PROJETO=seu-projeto-gcp   # CNPJs do BigQuery e mapas da Prefeitura -> dados/brutos/
make site                             # etapas 1 a 7 -> dados/intermediarios/ e docs/dados.json, docs/lugares.json
make servir                           # http://localhost:8000
```

Sem o Python do BigQuery, dá para rodar `pipeline/cnpj_rio.sql` no console do BigQuery e salvar o resultado em `dados/brutos/cnpj_rio.csv`. A consulta pega o retrato de janeiro de 2026 (ativos e os que fecharam a partir de 2021); para um retrato mais novo, troque `ano` e `mes`.

| Passo | Lê | Grava |
|---|---|---|
| `baixa_cnpj.py` + `cnpj_rio.sql` | BigQuery | `dados/brutos/cnpj_rio.csv` |
| `baixa_datario.py` | servidor de mapas da Prefeitura | `dados/brutos/logradouros.csv`, `trechos.json`, `bairros.geojson` |
| `01_universo.py` | `cnpj_rio.csv` | `universo.csv` |
| `02_atividade.py` | `universo.csv` | `atividade.csv` |
| `03_nomes.py` | `atividade.csv` | `nomes.csv`, `nomes_excluidos.csv` |
| `04_bairro.py` | `nomes.csv` | `bairro.csv`, `bairro_excluidos.csv` |
| `05_categorias.py` | `bairro.csv` | `categorias.csv` |
| `06_geocodifica.py` | `categorias.csv`, logradouros, trechos e bairros | `geo.csv` |
| `07_exporta.py` | `geo.csv` e bairros | `docs/dados.json`, `docs/lugares.json` |

Os intermediários ficam em `dados/intermediarios/`. `pipeline/perfil_cnpj.py` mede o arquivo bruto de CNPJ. `dados/` fica fora do git (os arquivos passam de 100 MB). O site em `docs/` é uma versão estática, publicada pelo GitHub Pages.

## Estrutura

```
pipeline/   download, etapas numeradas, regras de nome de pessoa (pessoas.py), de categoria (categorias.py) e dos nomes
            mostrados (destaques.py), rótulos de CNAE (cnae.py), nomes da seleção (sequencias.py) e a metodologia
docs/       o site: index.html (sem build, sem dependências) e os dois JSON que ele lê
dados/      brutos/ e intermediarios/, criados pelo pipeline
```
