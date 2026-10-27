"""Quais nomes de cada tipo vêm primeiro no site, um a um (METODOLOGIA.md, etapa 7).

O mapa conta todos os nomes de cada tipo; entre os nomes mostrados, os curiosos vêm primeiro e os outros completam
onde faltam. Nos tipos de Sotaques, curioso é a
mistura de línguas, o francês de verdade ou a fala regional, e não a fórmula ("Rio Store", "Fulano Coiffeur", "Sabor de
Minas"). Nos outros tipos, todos são curiosos. Uso:
    from destaques import mostra
    mostra('frances', 'LE BLE NOIR CREPERIE')  -> True
"""
import re

from categorias import FRANCES, INGLES, TIPO_DE_LOJA, TIPO_DE_LOJA_EXPR
from pessoas import norm, PRENOMES, SOBRENOMES


def P(txt):
    return set(txt.split())


DO = P('DO DA DOS DAS')
# o francês de verdade conta palavras do léxico e mais estas (que no léxico do mapa viraram tipo de loja ou não fazem
# falta); não contam o salão, a beleza e a bijuteria, nem "de" e "la", que também são português
FRANCES_NOME = (FRANCES | P('''ET UN UNE D L SUR CAFE BISTRO BISTROT MARCHE CHOCOLAT CHOCOLATIER VIN PAIN BLE DOUX GRAND
GRANDE PETIT CHIC CARRE OR ICI TEMPS MOI TOI LUI CORPS CLINIQUE OPTIQUE URBAIN URBAINS ATELIER DEPANNEUR TABLEAU FIGUIER
BOISSONS CREPE CREPES CUISINE FROMAGE VERT ROSE BLEU JARDIN SAVON MONTAGNE VELO PLAGE AMI AMIS BONNE BON TOUJOURS CAVE
JOUR MARIEE CENTRE MACARON ENTRECOTE''')) - P('''COIFFEUR COIFFEURS COIFEUR COIFFURE BELLE BEAUTE BIJOU BIJOUX PARFUM
PARFUMS DE LA''')
FRANCES_SALAO = P('COIFFEUR COIFFEURS COIFEUR COIFFURE')
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


def frances(cru):
    # duas palavras francesas ou mais, fora do salão ("Le Blé Noir Creperie", "Chez la Mer", "Maison du Pet");
    # conta o nome inteiro, com o tipo de loja, porque "Café", "Bistrot" e "Creperie" são parte do francês
    ws = norm(cru).split()
    return not set(ws) & FRANCES_SALAO and sum(w in FRANCES_NOME for w in ws) >= 2


def migracao(ws):
    if set(ws) & FALA:
        return True
    pares = list(zip(ws, ws[1:]))
    return any((a in DO | P('O A') and b in GENTILICO) or (a in GENTILICO and b in DO) for a, b in pares)


REGRA = {'ingles': lambda ws, cru: ingles(ws, cru), 'frances': lambda ws, cru: frances(cru),
         'migracao': lambda ws, cru: migracao(ws)}


def mostra(tipo, nome):
    """Se o nome (cru, como está na Receita) pode aparecer no site como exemplo do tipo."""
    if tipo not in REGRA:
        return True
    ws = [w for w in TIPO_DE_LOJA_EXPR.sub(' ', norm(nome)).split() if w not in TIPO_DE_LOJA]
    return REGRA[tipo](ws, nome)
