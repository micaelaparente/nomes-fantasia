"""Quais nomes de cada tipo podem aparecer no site, um a um (METODOLOGIA.md, etapa 7).

O mapa conta todos os nomes de cada tipo; os nomes mostrados ficam com os curiosos. Nos tipos de Sotaques, curioso é a
mistura de línguas ou a fala regional, e não a fórmula ("Rio Store", "Fulano Coiffeur", "Sabor de Minas"). Nos outros
tipos, todos podem aparecer. Uso:
    from destaques import mostra
    mostra('frances', 'MERCADINHO DU FOGO')  -> True
"""
import re

from categorias import FRANCES, INGLES, TIPO_DE_LOJA, TIPO_DE_LOJA_EXPR
from pessoas import norm, PRENOMES, SOBRENOMES


def P(txt):
    return set(txt.split())


DO = P('DO DA DOS DAS')
FRANCES_ARTIGO = P('DU LE LES CHEZ')
FRANCES_SALAO = P('COIFFEUR COIFFEURS COIFEUR COIFFURE BEAUTE BELLE SALON')
# palavras inglesas de fórmula que, antes de "do/da", não fazem mistura ("Point do Sabor", "Shop dos Filtros")
INGLES_FORMULA = P('POINT SHOP SHOPS STORE STUDIO HAIR CAR CENTER')
# gentílicos que, depois de "do/da" ou antes de "do/da/dos/das", viram apelido de gente ("Bar do Mineiro",
# "Mineira das Baterias"); nomes de região ("de Minas", "do Nordeste") dizem a origem do produto e ficam de fora
GENTILICO = P('''MINEIRO MINEIRA MINEIROS MINEIRINHO BAIANO BAIANA BAIANOS GAUCHO GAUCHA GAUCHOS CEARA CEARENSE
PARAIBA PARAIBANO PARAIBANA PAULISTA PERNAMBUCANO PERNAMBUCANA POTIGUAR CAPIXABA GOIANO GOIANA PIAUI MARANHENSE
ALAGOANO ALAGOANA SERGIPANO PARAENSE NORDESTINO NORDESTINA SERTANEJO''')
FALA = P('UAI OXE OXENTE VIXI VIXE ARRETADO ARRETADA ARRETADOS TCHE')


def ingles(ws, cru):
    # o 's numa palavra portuguesa que não é nome de gente ("Nilza's Modas", "Casa Fruta's", "Budega's Brasa")
    s = re.findall(r"([A-Z]+)['’]S\b", cru.upper())
    if any(w not in INGLES and w not in PRENOMES and w not in SOBRENOMES and len(w) > 3 for w in s):
        return True
    # palavra inglesa costurada no português com do/da ("King do Gelo", "World dos Cabelos")
    return any(ws[i] in INGLES - INGLES_FORMULA and ws[i + 1] in DO and i + 2 < len(ws) and ws[i + 2] not in INGLES
               for i in range(len(ws) - 1))


def frances(ws):
    if set(ws) & FRANCES_SALAO:
        return False
    # artigo francês com palavra portuguesa ("Mercadinho du Fogo", "Pet du Rapha", "Chez Marizete")
    if any(w in FRANCES_ARTIGO and i + 1 < len(ws) and ws[i + 1] not in FRANCES for i, w in enumerate(ws)):
        return True
    return bool(set(ws) & P('MADAME MONSIEUR MADEMOISELLE'))       # Madame e Monsieur fora do salão


def migracao(ws):
    if set(ws) & FALA:
        return True
    pares = list(zip(ws, ws[1:]))
    return any((a in DO | P('O A') and b in GENTILICO) or (a in GENTILICO and b in DO) for a, b in pares)


REGRA = {'ingles': lambda ws, cru: ingles(ws, cru), 'frances': lambda ws, cru: frances(ws),
         'migracao': lambda ws, cru: migracao(ws)}


def mostra(tipo, nome):
    """Se o nome (cru, como está na Receita) pode aparecer no site como exemplo do tipo."""
    if tipo not in REGRA:
        return True
    ws = [w for w in TIPO_DE_LOJA_EXPR.sub(' ', norm(nome)).split() if w not in TIPO_DE_LOJA]
    return REGRA[tipo](ws, nome)
