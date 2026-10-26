# Metodologia

Como o pipeline vai do cadastro de CNPJ da Receita aos dados do site, etapa por etapa, com o número de cada corte. Os
scripts ficam em `pipeline/`, numerados como as etapas.

## O que o site mostra

Uma exploração cultural e linguística dos nomes do comércio de bairro do Rio, com destaque para o jeito criativo,
afetivo e engraçado de dar nome. São duas camadas:
- **Categorias** (etapa 5): regras que descrevem a forma do nome (diminutivo, parentesco, inglês...). São a base do
  **mapa**: todos os nomes de cada categoria entram na conta, porque é o volume que deixa ver a geografia de um jeito de
  nomear. A categoria registra o fenômeno linguístico, mesmo quando ele é fórmula ("Dois Irmãos", "Rio Store").
- **Destaques**: os nomes mostrados um a um, nos cinco capítulos do site (Frases feitas, Lojões e lojinhas, Família,
  Sotaques e Poder). Na cidade, uma seleção feita à mão por capítulo (`sequencias.py`); numa região, os nomes da seleção
  que caem nela e, depois, nomes reais de cada tipo e bairro.

## Limites

- **Nome completo de pessoa fica de fora** (etapa 3), por privacidade; com ele, uma prática de nomear, a marca pessoal
  ("Sandra Lima Manicure").
- **Nome popular repetido pode sair como marca** (etapa 4). Um nome que cinco donos escolheram sem combinar é uma
  convenção popular, e a regra não o distingue de uma franquia: algumas dezenas de nomes, menos de 0,5% do corpus
  ("Quebra Galho", "Raio de Sol", "Ponto Certo", "Barbearia do Zé").
- **A grafia original se perdeu.** A Receita guarda os nomes sem acento e em maiúsculas; a pontuação sobrevive em parte
  ("Sacou Bicho!!!"). Os nomes da seleção são reacentuados à mão.
- **A classificação é por regras e tem erros**, para mais e para menos.
- **Os números por bairro são pequenos** (3 a 11 casos nos tipos menores): um nome a mais ou a menos muda o topo de um
  ranking. As regiões são bem mais estáveis.

## O bruto

`dados/brutos/cnpj_rio.csv`, pela consulta `cnpj_rio.sql` na Base dos Dados (`br_me_cnpj.estabelecimentos`, retrato de
11/01/2026, município 3304557): CNPJs ativos e fechados desde 2021. `perfil_cnpj.py` mede o arquivo.

- 1.762.105 CNPJs, sem repetidos. CNAE, CEP e bairro sempre preenchidos.
- Só ~3% são filiais (a ordem do CNPJ não é 0001): quase toda empresa é uma loja só.
- O bairro é texto livre declarado, com 1.020 grafias entre os ativos com nome (MAMGUINHOS, BOTTFOGO...).
- Não vêm razão social, porte, indicação de MEI nem complemento do endereço.

As ruas e os bairros vêm do servidor de mapas da Prefeitura (`baixa_datario.py`): o cadastro de trechos de rua com as
faixas de numeração de cada lado (132.065 trechos) e a malha de bairros (165), com a área e a região de planejamento.

## Etapa 1 · O universo (`01_universo.py`)

| Corte | Fica |
|---|---|
| bruto | 1.762.105 |
| situação cadastral ativa (2) | 1.058.421 |
| nome fantasia com ao menos uma letra | 223.908 |

- **Só ativas.** Inapta (305 mil) quer dizer que a empresa deixou de declarar, não que fechou, e muitas seguem
  abertas; mesmo assim ficam de fora, porque trariam muita loja que já fechou de fato.
- **Nome fantasia com letra.** 1.039 nomes não têm nenhuma ("****", "-", ".").

## Etapa 2 · Atividade (`02_atividade.py`)

Comércio e serviços com fachada para a rua, pela **atividade principal** (CNAE) declarada à Receita.

| Corte | Fica |
|---|---|
| universo (etapa 1) | 223.908 |
| atividade com fachada para a rua | 64.338 |

Por grupo: varejo 36.883 · comida 12.062 · veículos 5.214 · beleza e cuidados 4.768 · consertos 2.138 · lazer 1.875 ·
bichos 921 · serviços de balcão 417 · funerárias 60.

- **Entram:** todo o varejo; veículos (revendas, oficinas, lava-jato, autopeças, motos); restaurantes, lanchonetes e
  bares; marmitarias e pizzarias de entrega; padarias, confeitarias, açaí e sorvete, massas; salões, estética,
  lavanderias, banho e tosa, tatuagem; veterinárias e hotel para pet; consertos (assistência técnica, sapateiro,
  chaveiro); lotéricas, copiadoras, aluguel de roupas; academias, danceterias, lan house; funerárias.
- **Ficam fora:** bancos, hotéis e cinemas (redes, ou não são comércio de bairro); gestão de cemitérios ("Cemitério São
  João Batista" cairia na Fé); igrejas e terreiros (o capítulo Fé é sobre o sagrado em negócio que não é religioso);
  escolas e creches; escritórios, consultórios e condomínios.
- **CNAEs secundários não contam.** 25 mil empresas de fora têm algum secundário da lista; quase sempre é escritório
  que declara uma lista ampla. A atividade principal é o que a empresa diz que faz.
- **Limite:** sem o complemento do endereço (apto, sala, loja), não dá para separar a loja de rua da MEI que vende de
  casa pela internet; parte do varejo (roupas, 4.988) deve ser venda online.

## Etapa 3 · Nomes de pessoa (`03_nomes.py`, regras em `pessoas.py`)

| Corte | Fica |
|---|---|
| atividade (etapa 2) | 64.338 |
| sem nomes que identificam uma pessoa | 63.410 |

Saem 928: nome completo 782 · só nome 145 · CPF 1. Os excluídos ficam em `nomes_excluidos.csv`, com o motivo.

O filtro tem duas razões: privacidade (um nome completo num ponto exato do mapa, muitas vezes a casa de uma MEI,
identifica alguém) e editorial (nome de pessoa não é caso de criatividade). Três regras:
- **CPF** no nome (11 dígitos seguidos).
- **Só nome:** todas as palavras são prenome ou sobrenome, e ao menos uma é prenome ("Marcia Pinheiro", "Sheila & Fabio").
- **Nome completo:** um prenome seguido (com ou sem "de") de sobrenome, de outro prenome ou de palavra rara, isto é, que
  aparece em menos de 10 nomes do universo ("Sandra Lima Manicure", "Studio Ricardo Moreira", "Douglas dos Santos
  Atayde"). Prenome depois de São/Santo/Santa/N. S./Vila é santo ou lugar ("São Jorge de Rocha Miranda", "Vila
  Isabel"); depois de Zé/Zeca, palavra rara é apelido ("Zé Arruela", "Zé Pilintra"); número não é palavra rara.
- **Ficam:** só o primeiro nome com o negócio ("Bar do Luiz", "Casa Daniel"), só o sobrenome ("Papelaria Pereira",
  "Santana e Ribeiro Lanches"), "João e Maria".

**Limites.** O léxico tem 286 prenomes e 121 sobrenomes; nomes fora dele só são pegos pela regra da palavra rara. Numa
amostra de 100 nomes completos tirados, ~8 não eram pessoa: marcas e celebridades ("Carolina Herrera", "Bar do Zeca
Pagodinho"), comida ("Rosa Mexicana"), aumentativo ("Luiz Dogão"). Rótulos de filial ("FILIAL 449") e endereços no
lugar do nome não têm regra própria: quase todos saem como rede na etapa 4, e os ~12 que ficam não mudam as contagens.

## Etapa 4 · Comércio de bairro (`04_bairro.py`)

| Corte | Fica |
|---|---|
| nomes (etapa 3) | 63.410 |
| sem redes, marcas e lojas de shopping | 52.717 |

Saem 10.693: marca 4.415 · rede 3.974 · shopping 2.304 (quando há mais de um motivo, vale rede, depois marca). Os
excluídos ficam em `bairro_excluidos.csv`, com o motivo.

- **Rede:** a mesma empresa (raiz do CNPJ) em 3 ou mais lojas. Drogaria Pacheco, Venâncio, Smart Fit, Prezunic, e
  mini-redes locais de 3 lojas ("Colchões Botafogo").
- **Marca:** o mesmo nome (sem LTDA, ME...) em 5 ou mais empresas diferentes: Cacau Show, Casa do Biscoito, Óticas
  Carol, Mundo Verde, Fábrica de Bolo Vó Alzira. Também as variantes que começam pelo nome de uma marca de duas
  palavras ou mais ("CACAU SHOW MARACANA", "FABRICA DE BOLO VO ALZIRA - PIEDADE"). O corte em 5 vem da leitura por
  faixa: em 3 empresas, metade é coincidência ("Água de Coco", "Casa Rosa"); em 4–5, misturado ("Bar dos Amigos",
  "Depyl Action"); de 6 em diante, quase tudo marca.
- **Shopping:** endereço (logradouro + número) com 30 ou mais comércios em que pelo menos 35% são rede ou marca. São 37
  endereços: BarraShopping, Nova América, Norte Shopping, Bangu Shopping, West Shopping, Shopping Leblon, e as lojas do
  aeroporto do Galeão. Galerias (Visconde de Pirajá, Siqueira Campos 143) e mercados (Mercadão de Madureira, CADEG,
  CEASA) ficam: muitos comércios no mesmo endereço, mas poucas redes.
- **Limite:** ficam ~780 lojas de shopping onde as redes não chegam a 35% (Downtown, Shopping da Gávea, Casashopping), e
  as de shoppings com menos de 30 comércios.

## Etapa 5 · Categorias (`05_categorias.py`, regras em `categorias.py`)

Saída: `categorias.csv`, o comércio de bairro (52.717) com a coluna `categorias`. Os números abaixo são desse total.

**Palavra de tipo de loja não conta, em nenhum capítulo** (`TIPO_DE_LOJA`). Algumas palavras têm a forma de uma
categoria, mas são só o nome do que a loja é ou vende: Mercadinho, Atacadão, Mercadão, Armarinho, Sacolão, Varejão,
Coxinha, Quentinha, Martelinho; o inglês incorporado (Pet Shop, Delivery, Fitness, Studio, Burger, Grill, Pub,
Shopping, Auto Center, Self Service); o francês aportuguesado (Boutique, Bistrô, Ateliê, Salon); a comida estrangeira
(Sushi, Esfiha, Forneria, Gelateria, Kebab, Trattoria, Tasca). Se contassem, o mapa mostraria onde ficam os
mercadinhos, não como as pessoas dão nomes. "Mercadinho Bom Preço" não é diminutivo; "Mercadinho do Zezinho" é, pelo
Zezinho.

### Tamanho: 696 diminutivos · 358 aumentativos

- **Diminutivo:** palavra terminada em -INHO/-INHA(S) ou -ZIN/-ZIM/-ZITO/-ZITA ("Cafezin", "Quintalzin", "Joãozito"),
  menos as que só terminam assim (`NAO_DIMINUTIVO`: Rainha, Cozinha, Vinho, Caminho, Campainha, Sozinha, sobrenomes
  como Coutinho, lugares como Rocinha e Jacarezinho).
- **Aumentativo:** palavra terminada em -ZÃO, ou da lista `AUMENTATIVO`, revisada à mão (Sushirão, Gostosão, Felipão,
  Magrão, Sobradão, Piscinão, Importadão...). É lista, e não regra, porque palavras como Salão, Barão, Camarão, Feijão
  e Portão também terminam em -ÃO.
- **Apelidos contam:** Paulinho, Zezinho, Dinho, Carlão, Rodrigão.

### Família: 226 irmãos e primos · 83 pai e mãe · 63 filhos e netos · 59 avós · 58 tios · 13 sogras e compadres

Por grau de parentesco, com um léxico por grau (`PARENTES`). Um nome pode ter mais de um grau ("Pai e Filhos").
- **Não contam:** "Família/Family" (não é um parente); Mano/Mana, quase sempre gíria ou outra língua ("Fatto a Mano";
  Maninho e Maninha contam); Netinho, apelido; Neto e Filho no singular, quase sempre sobrenome ("Coelho Neto"). Filho
  conta junto de outro parente ou de "e" ("Pai e Filho"); "& Filhos" conta.
- **Expressões que não são parente:** "Mamma Mia", "Massa-Mãe", "Matéria-Prima".
- **Limite:** ~6 variantes da Vó Alzira escapam da regra de marca e contam como avós.

### Fé: 171 católico · 112 evangélico · 44 cristão sem igreja · 28 afro-brasileiro

Calculada em `categorias.csv`, mas fora do site.

Uma tradição por nome, a mais específica primeiro: evangélico (Ebenezer, Adonai, Canaã, El Shaddai, Peniel, Gospel),
católico (São/Santo/Santa + santo da lista, Nossa Senhora, Bom Jesus, São Miguel Arcanjo), afro-brasileiro (orixás,
Axé, Umbanda, Maria Padilha, Zé Pilintra), cristão sem igreja (Deus, Jesus, Bênção, Abençoado, Bíblia, "de fé").
- **Não contam:** lugares e sobrenomes com nome sagrado ("São Cristóvão", "Santa Cruz", "Rua Nossa Senhora", "Nossa
  Senhora de Copacabana", "dos Anjos", "Cidade de Deus"); Anjo, quase sempre doce, bicho ou sobrenome ("Papo de Anjo",
  "Anjos de Pata"), menos "Anjo da Guarda"; Arcanjo solto, sobrenome; Fátima, Lourdes, Aparecida e Nazaré soltos, nomes
  de gente; Divino/Divina ("Divina Pizza"), Céu, Glória, Fiel, Graça, Senhor e Fé solta (também café: "K-Fé").

### Sotaques: 6.514 inglês · 535 francês · 294 migração interna · 216 imigração

- **Inglês:** palavra do léxico, gerúndio -ING ou o 's ("Firmino's", "Nilza's Modas"). O inglês de vitrine conta ("Rio
  Store", "JR Car", "Luiza Hair"): ele é o fenômeno. "Show" não conta: já é português.
- **Francês:** palavra do léxico ou grafia francesa (-ERIE, -EAU). Artigo solto (Le, Les, Au, Mon...) só conta no começo
  do nome; "Du" conta em qualquer lugar, pelo francês abrasileirado ("Mercadinho du Fogo", "Pizza du Malt", "Vet du
  Bem"). "Três" e "Chic" não contam: são português.
- **Imigração:** gentílico, país ou parente ("Pastel do Japa", "Boteco do Portuga", "Atacadão da Cuba", "Armazém do
  Nonno"). "Israel" não conta (nome de gente ou referência evangélica).
- **Migração interna:** gentílico ou estado do Brasil e fala regional ("Uai", "Oxente", "Vixi", "Arretado").
- **Cozinha:** nas duas, o gentílico logo depois de uma palavra de cozinha não conta, porque só diz o tipo de cozinha
  ("Culinária Japonesa", "Restaurante Nordestino", "Comida Mineira"). "Tempero de Minas" e "Vixi Restaurante
  Nordestino" contam: o lugar e a fala são escolha.

### Frases: 186 chamados · 143 primeira pessoa · 116 promessas · 84 interjeições

Um tipo por nome, nesta ordem: interjeições ("Cervejei", "Oba!", "Oh My Dog!", "Bom Dia"), primeira pessoa ("Tô na
Skina", "Quero um de Cada", "Sonho Meu"), chamados ("Vem que Tem", "Zé Vai, Zé Vem!", "Cadê Teresa?", "Isso Não É uma
Barbearia") e promessas ("Tem Tudo", "Severino Tem Quase Tudo", "Tá pra Peixe da Cris", "Deu Match", "Pizza Já!").
- **Não contam:** "Tô" em inglês ("Buy to Buy", "One to One"); "Nos" (quase sempre "em os": "Acerta nos Brindes");
  "Leve" (quase sempre leveza: "Comida Leve"); verbos que são substantivo ou lugar ("Compra e Venda", "Liga dos
  Botecos", "São Tomé", "Aqui Embaixo").
- **Limite:** a fala é o tipo mais difícil de pegar por regra; expressões que não começam por uma palavra da lista
  escapam.

### Poder: 400 reis e rainhas · 200 impérios e palácios · 99 república e patentes

O pequeno comércio que se coroa, se faz império ou vira repartição. Um tipo por nome, nesta ordem:
- **República e patentes:** República, Ministério, Senado, Tribunal, Presidente, Embaixada, Pátria; General, Capitão,
  Major, Almirante, Chefe, Chefão, Patrão, Mestre, Doutor, Boss ("Ministério da Pizza", "República do Crepe", "Lotérica
  Adeus Patrão", "Mestre do Amassado").
- **Reis e rainhas:** Rei, Rainha, Príncipe, Princesa, Imperador, Duque, Conde, Baronesa, Lord, King, Queen ("Rei do
  Joelho", "Rainha do Bacalhau", "O Rei do Velocímetro", "Princesa do Gás").
- **Impérios e palácios:** Império, Reino, Palácio, Castelo, Majestade, Nobreza ("Império do Ovo", "Palácio das Rações",
  "Castelo do Frio", "Nobreza Canina").
- **Não contam:** título de gente seguido de "de/dos/das" ("Conde de Bonfim", "Duque de Caxias"); qualquer título seguido
  de nome de gente, sobrenome ou nome de rua comum ("Princesa Isabel", "Presidente Vargas"), ou depois de um prenome
  ("Eliza Conde"); Barão, quase sempre a Rua Barão de Mesquita; Marechal, quase sempre o bairro; lugares e expressões
  ("Ilha do Governador", "Senador Camará", "Engenho da Rainha", "Castelo Branco", "Pimenta do Reino", "Fruta do Conde",
  "Cristo Rei", "General Store"); adjetivos como Imperial, Real, Nobre e Supremo.

## Etapa 6 · Geocodificação (`06_geocodifica.py`)

| Como o comércio ganha um ponto | Comércios |
|---|---|
| rua no bairro declarado | 48.918 (o ponto cai no bairro declarado em 98,3%) |
| rua num bairro vizinho | 1.380 |
| sem rua: centro do bairro declarado | 1.881 |
| fica fora | 538 (1,0%) |

- **Chave da rua:** sem o tipo (Rua, Avenida...), sem títulos (Marechal, Ator, Almirante, Prof...), com a grafia
  simplificada (Z/S, Y/I, W/V, letras dobradas, -eia/-ea, -am/-ã) e as palavras em qualquer ordem. A Receita escreve
  "Avenida José Wilker Ator" e "Avenida Marechal Fontenelle"; o cadastro, "Avenida José Wilker" e "Avenida Marechal
  Fontenele".
- **Bairro vizinho:** se a rua não existe no bairro declarado, vale a mesma rua no bairro onde ela passa mais perto
  dele, a até 1 km. Pega a rua que está noutro bairro no cadastro (Abelardo Bueno e José Wilker na Barra Olímpica, Rua
  da Lapa na Lapa, Via Ápia na Rocinha). Mais longe, é outra rua com o mesmo nome.
- **Grafia dos bairros:** o cadastro chama São Cristóvão de "Imperial de São Cristóvão" e escreve Oswaldo Cruz; a
  malha, São Cristóvão e Osvaldo Cruz. Os dois são unificados.
- **Número:** o ponto vai pela faixa de numeração do lado (par ou ímpar) do trecho que contém o número (28.804) ou do
  mais próximo (18.492). Sem número ou sem faixa, no meio da rua (3.002).
- **Sem rua, centro do bairro:** quem não casa com nenhuma rua vai para o centro do bairro declarado, quando esse bairro
  existe na malha: o ponto de rua do bairro mais perto da média dos pontos de rua dele, sempre numa rua do bairro.
  Assim a Maré, onde muitas ruas não estão no cadastro, não perde 41% dos comércios. Ficam fora 538, quase todos com um
  bairro declarado que não é bairro da malha ("Ilha do Governador", "Freguesia" sem dizer qual).
- **O bairro do comércio é o do polígono onde o ponto cai**, na malha da Prefeitura, e não o declarado à Receita.
- **Limites:** a numeração dos trechos não é uniforme, então a posição na rua é aproximada (de algumas dezenas a
  centenas de metros). Os pontos de centro de bairro se acumulam num lugar só; a coluna `posicao` os marca.

## Etapa 7 · Exportação (`07_exporta.py`)

Grava `docs/dados.json` e `docs/lugares.json`, os dois arquivos que o site lê.
- **Mapa:** a cidade em quadradinhos de 750 m. A grade usa só os pontos de rua (50.297); os de centro de bairro
  formariam falsos focos. A cor de cada quadradinho é o tipo que mais pesa ali comparado à média da cidade.
- **Bairros, regiões, ranking e comparação** usam todos os comércios com ponto (52.178), pelo bairro onde o ponto cai.
  Regiões: as cinco Áreas de Planejamento da Prefeitura, com a AP 2 dividida em Zona Sul e Grande Tijuca.
- **Ranking:** os bairros onde cada tipo mais pesa contra a média da cidade, entre bairros com 150+ comércios e 5+
  casos do tipo (3+ nos tipos com menos de 150 na cidade). Sogras e compadres (13 nomes) não tem bairro com 3 casos, e
  o site não mostra ranking para ele.
- **Nomes mostrados:** a seleção à mão de `sequencias.py` e até 6 nomes reais por tipo e bairro, os de tamanho mais
  legível primeiro, sem quase-repetidos. No francês, os nomes com "Coiffeur" contam no mapa, mas não entram entre os
  nomes mostrados: "Fulano Coiffeur" é a fórmula de um terço do tipo.
