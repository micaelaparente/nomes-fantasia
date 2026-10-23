"""Dados do site Nomes fantasia -> docs/dados.json e docs/lugares.json

Comércio de bairro ativo com nome fantasia (comercios_rua.csv, fora redes, franquias, bancos, cinemas, hotéis e
shoppings), unido aos pontos geocodificados, sem nomes de pessoa, classificado nos cinco conceitos (vozes.CONCEITOS). Exporta:
- grade: a cidade em quadradinhos de GRADE metros, com total de comércios e contagem por subcategoria;
- ranking: bairros onde cada subcategoria mais pesa (× a média da cidade) e o contraste entre regiões;
- comparacao: quantidade e peso de cada subcategoria nas seis regiões;
- sequencias: nomes curados, em capítulos que contam algo (pares grande/pequeno, conversas, gerações...), cada um
  com o tipo do comércio (cnae.py), que a página mostra junto do bairro.
Uso: python pipeline/05_exporta.py
"""
import csv, json, math, os, re, sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
sys.path.insert(0, os.path.dirname(__file__))
from sotaques import limpa, parece_pessoa
from vozes import CONCEITOS, classifica_conceitos
from cnae import rotulo as tipo_cnae

from caminhos import BAIRROS, COMERCIOS, GEO, SITE
OUT = str(SITE) + '/'
LON0, LAT0 = -43.80, -22.74
KX = math.cos(math.radians(22.9)) * 111320
KY = 110540
GRADE = 750
SUBS = [s for subs in CONCEITOS.values() for s in subs]
# quando um nome tem dois tipos, qual vale para a cor (Os Filhos da Mãe é dos filhos, não da mãe)
PRIORIDADE = {'familia': ['avos', 'tios', 'irmaos', 'filhos', 'agregados', 'pais']}
# seis regiões: as cinco Áreas de Planejamento da Prefeitura, com a AP 2 dividida em Zona Sul e Grande Tijuca
# (a sub-região Tijuca da própria malha), como o carioca fala
REGIOES = ['Centro', 'Zona Sul', 'Grande Tijuca', 'Zona Norte', 'Barra e Jacarepaguá', 'Zona Oeste']
AP = {'1': 'Centro', '3': 'Zona Norte', '4': 'Barra e Jacarepaguá', '5': 'Zona Oeste'}

# Sequências: grupos com rótulo e nomes [como está nos dados, como aparece]. A página alterna entre os grupos
# (um de cada por vez), para mostrar variedade com fio condutor; frases são uma conversa única, em ordem.
# tamanho: pares do mesmo radical, o grande e o pequeno aparecem juntos
SEQUENCIAS = {
    'tamanho': [
        ['Mercado', ['Mercadao dos Bichos', 'Mercadão dos Bichos'], ['Mercadinho Joinha', 'Mercadinho Joinha']],
        ['Loja', ['Lojao do Um Real', 'Lojão do Um Real'], ['Lojinha da Roca', 'Lojinha da Roça']],
        ['Casa', ['Casarao do Biscoito', 'Casarão do Biscoito'], ['Cafe Casinha da Cacau', 'Café Casinha da Cacau']],
        ['Atacado', ['Atacadao dos Tijolos', 'Atacadão dos Tijolos'], ['Atacadinho do Rei', 'Atacadinho do Rei']],
        ['Amigo', ['Amigao de Sepetiba', 'Amigão de Sepetiba'], ['Amiguinhos do Vovo', 'Amiguinhos do Vovô']],
        ['Feira', ['Feirao dos Doces e Brinquedos', 'Feirão dos Doces'], ['Bar da Feirinha Boteco Grill', 'Bar da Feirinha']],
        ['Dog', ['Dogao Pet Shop', 'Dogão Pet Shop'], ['Casa dos Doguinhos', 'Casa dos Doguinhos']],
        ['Gordo', ['Picanha do Gordao C', 'Picanha do Gordão'], ['Mercearia do Gordinho', 'Mercearia do Gordinho']],
        ['Carlos', ['Carlao Games', 'Carlão Games'], ['Carlinhos Bicicletas', 'Carlinhos Bicicletas']],
        ['Sacola', ['Sacolao Bolsa Cheia F', 'Sacolão Bolsa Cheia'], ['Sacolinho', 'Sacolinho']],
        ['Bicho', ['Bichao', 'Bichão'], ['Meu Bichinho', 'Meu Bichinho']],
    ],
    # frases: uma conversa só, cada nome respondendo ao anterior
    'frases': [
        ['Conversa', ['Alo Voce', 'Alô Você!'], ['Oi Cheguei', 'Oi, Cheguei'], ['To Careca de Saber', 'Tô Careca de Saber'], ['Fala Bar', 'Fala Bar'], ['Manda Bem', 'Manda Bem'],
         ['Vem Que Tem', 'Vem Que Tem'], ['Tem de Tudo', 'Tem de Tudo'], ['Esse Ja e Meu', 'Esse Já É Meu'],
         ['Te Peguei Modas', 'Te Peguei'], ['Passa Nada', 'Passa Nada'],
         ['Eita Sorvete Acai Lanches', 'Eita Sorvete'], ['Uai Salgados', 'Uai Salgados'], ['Sacou Bicho !!! Racoes', 'Sacou Bicho!!!'],
         ['Nos Ta Aki', 'Nós Tá Aki'], ['Aqui Conserta', 'Aqui Conserta'], ['Pipocou Doces', 'Pipocou'], ['Salgadou', 'Salgadou'],
         ['Lavou', 'Lavou'], ['Tudo de Bom', 'Tudo de Bom'], ['To Junto Bebidas', 'Tô Junto'], ['Bora Comer', 'Bora Comer']],
    ],
    'fe': [
        # fé: só o sagrado em negócio que não tem nada a ver com religião (nada de farmácia com nome de santo)
        ['Católico', ['Abrasivos Sao Joao', 'Abrasivos São João'],
         ['Bar Sao Jorge Guereiro da Capadocia Olaria', 'Bar São Jorge Guerreiro da Capadócia'],
         ['Casa de Racao Sao Lazaro', 'Casa de Ração São Lázaro'], ['Pet Shop Nossa Senhora de Fatima', 'Pet Shop N. Sra. de Fátima'],
         ['Parafusos Santa Clara', 'Parafusos Santa Clara']],
        ['Evangélico', ['Aleluia Ferragens', 'Aleluia Ferragens'], ['Gospel Hortifrutigranjeiros', 'Gospel Hortifrutigranjeiros'],
         ['El Shaddai Motors', 'El Shaddai Motors'], ['Jireh Pecas', 'Jireh Peças'], ['Cesta Basica Deus e Fiel', 'Cesta Básica Deus É Fiel']],
        ['Afro-brasileiro', ['Oxala Conveniencia', 'Oxalá Conveniência'], ['Cachacaria Axe', 'Cachaçaria Axé'],
         ['Ouro de Oxum', 'Ouro de Oxum'], ['Casa do Xango', 'Casa do Xangô'], ['Imperio da Maria Padilha', 'Império da Maria Padilha']],
        ['Cristão, sem igreja', ['Gelo Deus Todo Poderoso', 'Gelo Deus Todo Poderoso'], ['Bar Jesus', 'Bar Jesus'],
         ['Pasta So Bencao', 'Pasta Só Bênção'], ['Otica Jesus e Luz', 'Ótica Jesus É Luz'], ['Anjos Telecom Security', 'Anjos Telecom Security']],
    ],
    'culturas': [
        ['De Portugal', ['Pedacinho de Portugal', 'Pedacinho de Portugal'], ['Hortifruti Portuga', 'Hortifruti Portuga'],
         ['Cantina do Portuga', 'Cantina do Portuga'], ['Portuga Auto Pecas', 'Portuga Auto Peças']],
        ['Da Itália, do Oriente', ['Sapore d Italia', "Sapore d'Italia"], ['Feyzi Culinaria da Turquia', 'Feyzi Culinária da Turquia'],
         ['Pastel do Japa', 'Pastel do Japa'], ['Japa Nao', 'Japa Não']],
        ['Do Nordeste', ['Oxe e do Nordeste', 'Oxe É do Nordeste'], ['Jerimum do Nordeste', 'Jerimum do Nordeste'],
         ['Gigante Nordestino', 'Gigante Nordestino'], ['Xodo da Baiana', 'Xodó da Baiana']],
        ['De Minas e do Sul', ['Mineiro Uai', 'Mineiro Uai'], ['Cachorrao do Mineiro', 'Cachorrão do Mineiro'],
         ['Topa Tudo dos Mineiros', 'Topa Tudo dos Mineiros'], ['Esquina do Gaucho', 'Esquina do Gaúcho']],
        ['Da França', ['Madame Chica Salao de Beleza', 'Madame Chica'], ['Frango Chic', 'Frango Chic'], ['Hortifruti Monsieur', 'Hortifruti Monsieur'],
         ['Coiffeur Dog', 'Coiffeur Dog']],
        ['Dos Estados Unidos', ["The King's Barbers", "The King's Barbers"], ["Cretino's Pub", "Cretino's Pub"],
         ["Jm's das Pilhas", "JM's das Pilhas"], ['Oh My Dog! Pet Shop', 'Oh My Dog! Pet Shop']],
    ],
    'familia': [
        ['Avós', ['Empadinhas da Vo Fatinha', 'Empadinhas da Vó Fatinha'], ['Frigideira da Vovo', 'Frigideira da Vovó'],
         ['Coisas da Vo', 'Coisas da Vó'], ['Boleria d Avo', "Boleria d'Avó"]],
        ['Tios', ['Tio Chiquinho Cachaca Amarela', 'Tio Chiquinho Cachaça Amarela'], ['Deposito da Tia Zao', 'Depósito da Tia Zão'],
         ['Cachorro Quente da Tia', 'Cachorro-Quente da Tia'], ['Tio Cabeca Bar', 'Tio Cabeça Bar']],
        ['Pai e mãe', ['Borracharia do Pai', 'Borracharia do Pai'], ['Garagem do Papai', 'Garagem do Papai'],
         ['Mamae Cegonha', 'Mamãe Cegonha'], ['Comida de Mae em Casa', 'Comida de Mãe em Casa'], ['Tal Pai, Tal Fish', 'Tal Pai, Tal Fish']],
        ['Irmãos e primos', ['Irmao do Um Real', 'Irmão do Um Real'], ['Vidracaria Ii Irmaos Coragem', 'Vidraçaria II Irmãos Coragem'],
         ['Oficina dos Primo', 'Oficina dos Primo'], ['Irmas da Terra', 'Irmãs da Terra']],
        ['Agregados', ['Recanto da Sogra Restaurante', 'Recanto da Sogra'], ['Toca da Sogra', 'Toca da Sogra'],
         ['Di Comadre', 'Di Comadre'], ['Fada Madrinha', 'Fada Madrinha']],
        ['Filhos e netos', ['Os Filhos da Mae!', 'Os Filhos da Mãe!'], ['Tal Mae Tal Filha Biscuit', 'Tal Mãe, Tal Filha'],
         ['Casa Oito Netos', 'Casa Oito Netos'], ['Bar e Lanchonete Os Filhos de Francisco', 'Os Filhos de Francisco']],
    ],
}


def xy(lon, lat):
    return round((lon - LON0) * KX), round((LAT0 - lat) * KY)


gj = json.load(open(BAIRROS))
# a malha de bairros grafa dois nomes diferente da base geocodificada: fica a grafia da base
GRAFIA = {'Osvaldo Cruz': 'Oswaldo Cruz', 'Turiaçú': 'Turiaçu'}
for f in gj['features']:
    f['properties']['nome'] = GRAFIA.get(f['properties']['nome'], f['properties']['nome'])
RP ={f['properties']['nome']: f['properties']['rp'] for f in gj['features']}
APB = {f['properties']['nome']: f['properties']['area_plane'].strip() for f in gj['features']}


def regiao(b):
    ap = APB.get(b)
    if ap == '2':
        return 'Grande Tijuca' if RP[b] == 'Tijuca' else 'Zona Sul'
    return AP.get(ap)


rua = {r['cnpj']: r for r in csv.DictReader(open(COMERCIOS))}

# Comércio de bairro: pequenos negócios com fachada para a rua, fora redes, franquias, bancos, cinemas, hotéis e shoppings.
# Rede: a mesma raiz de CNPJ (a mesma empresa) em 3+ lojas. Franquia: o mesmo nome em 3+ empresas, com uma palavra que em
# 80%+ das vezes só aparece nesse nome, isto é, uma marca (Mega Matte, Mala Ingleza); nomes comuns que coincidem por
# acaso (Cantinho da Vila, Barbearia do Zé) ficam.
FORA_CNAE = ('6421', '6422', '5914', '5510', '5590601')


def fora_do_bairro(rua):
    raiz = Counter(c[:8] for c in rua)
    nome_de = {c: limpa(a['nome_fantasia']) for c, a in rua.items()}
    empresas, tok, tok_nome = defaultdict(set), Counter(), defaultdict(Counter)
    for c, n in nome_de.items():
        empresas[n].add(c[:8])
        for t in set(n.split()):
            tok[t] += 1
            tok_nome[t][n] += 1
    marcas = {}

    def marca(n):
        if n not in marcas:
            marcas[n] = len(empresas[n]) >= 3 and any(
                len(t) >= 4 and sum(k for m, k in tok_nome[t].items() if m == n or m.startswith(n + ' ')) >= .8 * tok[t]
                for t in set(n.split()))
        return marcas[n]
    motivo = {}
    for c, a in rua.items():
        if raiz[c[:8]] >= 3:
            motivo[c] = 'rede'
        elif a['cnae'].startswith(FORA_CNAE):
            motivo[c] = 'banco, cinema ou hotel'
        elif 'SHOPPING' in (a['logradouro'] + ' ' + a['nome_fantasia']).upper():
            motivo[c] = 'shopping'
        elif marca(nome_de[c]):
            motivo[c] = 'franquia'
    return motivo


fora = fora_do_bairro(rua)
print('fora do comércio de bairro:', len(fora), 'de', len(rua), dict(Counter(fora.values())))
rua = {c: a for c, a in rua.items() if c not in fora}
celulas = defaultdict(lambda: [0] * (1 + len(SUBS)))
cel_b = defaultdict(Counter)                    # quantos comércios de cada bairro caem em cada quadradinho
pool = defaultdict(lambda: defaultdict(dict))   # nomes reais por subcategoria e bairro, para explorar lugares
tot_b, tot_rp, sub_b, sub_rp = Counter(), Counter(), defaultdict(Counter), defaultdict(Counter)
xy_b, ap_xy, por_nome, cont = defaultdict(lambda: [0, 0, 0]), defaultdict(lambda: [0, 0, 0]), {}, Counter()
tot_ap, sub_ap = Counter(), defaultdict(Counter)
for r in csv.DictReader(open(GEO)):
    a = rua.get(r['cnpj'])
    if not a:
        continue
    nome = limpa(a['nome_fantasia'])
    if not nome or parece_pessoa(nome):
        continue
    x, y = xy(float(r['lon']), float(r['lat']))
    b = r['bairro_oficial']
    subs = classifica_conceitos(nome, a['nome_fantasia'])
    c = celulas[(x // GRADE, y // GRADE)]
    c[0] += 1
    cel_b[(x // GRADE, y // GRADE)][b] += 1
    tot_b[b] += 1
    xy_b[b][0] += x; xy_b[b][1] += y; xy_b[b][2] += 1
    rp = RP.get(b)
    if rp:
        tot_rp[rp] += 1
    ap = regiao(b)
    if ap:
        ap_xy[ap][0] += x; ap_xy[ap][1] += y; ap_xy[ap][2] += 1
        tot_ap[ap] += 1
    for s in subs:
        c[1 + SUBS.index(s)] += 1
        sub_b[s][b] += 1
        cont[s] += 1
        if rp:
            sub_rp[s][rp] += 1
        if ap:
            sub_ap[s][ap] += 1
        pool[s][b].setdefault(nome, (x, y, tipo_cnae(a["cnae"])))
    por_nome.setdefault(nome, (x, y, b, tipo_cnae(a["cnae"])))
N = sum(tot_b.values())
print('comércios', N, dict(cont))

# ranking por bairro (mín. 150 comércios e 5 casos; 3 nas subcategorias raras) e contraste entre regiões
ranking = {}
for s in SUBS:
    taxa, minimo = cont[s] / N, 5 if cont[s] >= 150 else 3
    bs = sorted(((sub_b[s][b] / tot_b[b]) / taxa, b) for b in sub_b[s] if tot_b[b] >= 150 and sub_b[s][b] >= minimo)[::-1]
    reg = {rp: sub_rp[s][rp] / n for rp, n in tot_rp.items() if n >= 600 and sub_rp[s][rp] >= 3}
    alto, baixo = max(reg, key=reg.get), min(reg, key=reg.get)
    ranking[s] = {'total': cont[s], 'umEm': round(1 / taxa),
                  'bairros': [[b, round(i, 1), sub_b[s][b], round(tot_b[b] / sub_b[s][b])] for i, b in bs[:5]],
                  'alto': [alto, round(1 / reg[alto])], 'baixo': [baixo, round(1 / reg[baixo])]}
    print(s, [(b[0], b[1]) for b in ranking[s]['bairros'][:3]], '| região', alto, '×', baixo)

centros = {b: [round(v[0] / v[2]), round(v[1] / v[2])] for b, v in xy_b.items()}

sequencias = {}
for conceito, caps in SEQUENCIAS.items():
    sequencias[conceito] = []
    for rotulo, *nomes in caps:
        itens = []
        for dado, exib in nomes:
            p = por_nome.get(limpa(dado))
            if p is None:
                print('não achado:', conceito, dado)
                continue
            subs = classifica_conceitos(limpa(dado), dado) & set(CONCEITOS[conceito])
            sub = next((x for x in PRIORIDADE.get(conceito, CONCEITOS[conceito]) if x in subs), CONCEITOS[conceito][0])
            itens.append([p[0], p[1], exib, p[2], sub, p[3]])
        sequencias[conceito].append([rotulo, itens])

# comparação entre as seis regiões: quantidade (absoluto) e peso (por comércio)
comparacao = {s: [[r, sub_ap[s][r], tot_ap[r]] for r in REGIOES] for s in SUBS}

grade = [[ix, iy] + c for (ix, iy), c in celulas.items()]
regioes = [[round(ap_xy[r][0] / ap_xy[r][2]), round(ap_xy[r][1] / ap_xy[r][2]), r] for r in REGIOES]

os.makedirs(OUT, exist_ok=True)
json.dump({'conceitos': CONCEITOS, 'subs': SUBS, 'grade_m': GRADE, 'grade': grade, 'regioes': regioes,
           'ranking': ranking, 'centros': centros, 'sequencias': sequencias,
           'comparacao': comparacao},
          open(OUT + 'dados.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('dados.json', round(os.path.getsize(OUT + 'dados.json') / 1e3), 'KB')

# Lugares (lugares.json), para aproximar o mapa numa região (os bairros contam, nomeiam e desenham a região):
# - bairros: região, total de comércios e contagem por subcategoria;
# - celula_bairro: o bairro que mais pesa em cada quadradinho (na mesma ordem de grade); dele saem a região de cada
#   quadradinho e os contornos em degraus, desenhados na própria grade;
# - nomes: até POR_BAIRRO nomes reais por subcategoria e bairro, os de tamanho mais legível primeiro, com o tipo do comércio.
POR_BAIRRO = 6
nomes_b = sorted(b for b in tot_b if b in APB)
idx_b = {b: i for i, b in enumerate(nomes_b)}
bairros = {b: [regiao(b) or '', tot_b[b], [sub_b[s][b] for s in SUBS]] for b in nomes_b}
celula_bairro = [idx_b.get(cel_b[k].most_common(1)[0][0], -1) for k in celulas]


def escolhe(cands):
    """Os mais legíveis primeiro, sem quase-repetidos (FABRICA / FRABRICA DE BOLO VO ALZIRA)."""
    out = []
    for n, (x, y, t) in sorted(cands.items(), key=lambda kv: (abs(len(kv[0]) - 16), kv[0])):
        if 4 <= len(n) <= 30 and not any(SequenceMatcher(None, n, o[0]).ratio() > .8 for o in out):
            out.append([n, x, y, t])
        if len(out) == POR_BAIRRO:
            break
    return out


nomes = {s: {b: escolhe(pool[s][b]) for b in pool[s] if b in idx_b} for s in SUBS}
json.dump({'bairros': bairros, 'celula_bairro': [nomes_b, celula_bairro], 'nomes': nomes},
          open(OUT + 'lugares.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('lugares.json', round(os.path.getsize(OUT + 'lugares.json') / 1e3), 'KB')
