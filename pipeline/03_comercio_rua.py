"""CNPJs do Rio -> comércio de rua ativo, com nome fantasia, sem nomes de pessoa (dados/intermediarios/comercios_rua.csv).

Uso: python pipeline/03_comercio_rua.py
"""
import re, sys
import pandas as pd

from caminhos import CNPJ_RIO, COMERCIOS
SRC, OUT = str(CNPJ_RIO), str(COMERCIOS)

# CNAEs de comércio/serviço com fachada voltada para a rua (prefixo -> casa com startswith)
CNAE_INCLUI = [
    "47",                                   # todo o varejo
    "4511", "4520", "4530", "4541", "4543", # veículos: revendas, oficinas, lava-jato, autopeças, motos
    "5611",                                 # restaurantes, lanchonetes, bares
    "5510", "5590601",                      # hotéis, albergues
    "1091102",                              # padarias/confeitarias
    "9602",                                 # cabeleireiros, estética
    "9601",                                 # lavanderias
    "9603",                                 # funerárias
    "9609208",                              # banho e tosa
    "9313",                                 # academias
    "7500",                                 # veterinárias
    "6421", "6422",                         # agências bancárias
    "8299706",                              # lotéricas
    "8219901",                              # copiadoras
    "9511", "9512", "9521", "9529",         # assistência técnica, sapateiro, chaveiro, bicicletas
    "5914",                                 # cinemas
]

CONECTIVOS = {"DE", "DA", "DO", "DOS", "DAS", "E", "D"}

PRENOMES = set("""
ADRIANA ADRIANO AGATHA ALAN ALESSANDRA ALESSANDRO ALEX ALEXANDRE ALEXANDRA ALICE ALINE ALLAN ALVARO AMANDA ANA ANDERSON
ANDRE ANDREA ANDRESSA ANGELA ANGELICA ANTONIO ANTONIA ARTHUR AUGUSTO BARBARA BEATRIZ BERNARDO BIANCA BRENDA BRENO BRUNA BRUNO
CAIO CAMILA CAMILLA CARLA CARLOS CARMEN CAROLINA CAROLINE CASSIA CATARINA CECILIA CELIA CESAR CHRISTIAN CLARA CLARICE CLAUDIA
CLAUDIO CRISTIANE CRISTIANO CRISTINA DAIANE DANIEL DANIELA DANIELE DANIELLE DANILO DAVI DAVID DEBORA DENISE DIEGO DIOGO DOUGLAS
EDSON EDUARDO ELAINE ELIANE ELISA ELIZABETH EMANUEL EMANUELE EMERSON ERICA ERIKA ERICK EVELYN FABIANA FABIANO FABIO FABRICIO
FATIMA FELIPE FERNANDA FERNANDO FILIPE FLAVIA FLAVIO FRANCISCA FRANCISCO GABRIEL GABRIELA GABRIELLE GILBERTO GIOVANNA GISELE
GISELLE GLAUCIA GRAZIELA GUILHERME GUSTAVO HELENA HELIO HENRIQUE HUGO IGOR INGRID ISABEL ISABELA ISABELLA ISABELLE ISADORA IVAN
IVONE JANAINA JEFFERSON JESSICA JOANA JOAO JONATHAN JORGE JOSE JOSEFA JOSIANE JULIA JULIANA JULIANO JULIO KAREN KARINA KATIA
KELLY LAIS LARA LARISSA LAURA LEANDRO LEILA LEONARDO LETICIA LIDIA LIGIA LILIAN LUANA LUCAS LUCIA LUCIANA LUCIANO LUIZ LUIS
LUIZA LUISA MARCELA MARCELLA MARCELO MARCIA MARCIO MARCO MARCOS MARCUS MARIA MARIANA MARINA MARIO MARLENE MATEUS MATHEUS MAURICIO
MAURO MAYARA MICHELE MICHELLE MIGUEL MILENA MIRIAM MONICA NATALIA NATHALIA NICOLE NILTON NUBIA OSVALDO PABLO PAMELA PATRICIA
PAULA PAULO PEDRO PRISCILA PRISCILLA RAFAEL RAFAELA RAFAELLA RAQUEL REGINA REGINALDO RENATA RENATO RICARDO RITA ROBERTA ROBERTO
ROBSON RODRIGO ROGERIO ROSA ROSANA ROSANGELA RUBENS SABRINA SAMANTHA SAMUEL SANDRA SANDRO SARA SARAH SERGIO SHEILA SILVIA SIMONE
SONIA SUELI SUELEN TAINA TAIS TAMIRES TATIANA TATIANE THAIS THIAGO TIAGO VALERIA VANESSA VERA VICTOR VINICIUS VITOR VITORIA
VIVIANE WAGNER WALLACE WANDERSON WELLINGTON WESLEY WILLIAM WILSON YASMIN
""".split())

SOBRENOMES = set("""
ABREU AGUIAR ALBUQUERQUE ALMEIDA ALVES AMARAL ANDRADE ARAUJO ASSIS AZEVEDO BAPTISTA BARBOSA BARROS BASTOS BATISTA BEZERRA BORGES
BRAGA BRANDAO BRITO CABRAL CAMPOS CARDOSO CARNEIRO CARVALHO CASTRO CAVALCANTI CORREA CORREIA COSTA COUTINHO CRUZ CUNHA DIAS
DUARTE ESTEVES FARIA FARIAS FERNANDES FERREIRA FIGUEIREDO FONSECA FRANCA FRANCO FREITAS GOMES GONCALVES GUIMARAES JESUS LEAL
LEITE LIMA LOPES MACEDO MACHADO MAGALHAES MARQUES MARTINS MATOS MATTOS MEDEIROS MELLO MELO MENDES MENEZES MIRANDA MONTEIRO MORAES
MORAIS MOREIRA MOTA MOURA NASCIMENTO NEVES NOGUEIRA NUNES OLIVEIRA PACHECO PAIVA PEREIRA PERES PESSOA PINHEIRO PINTO PIRES
QUEIROZ RAMOS REIS RESENDE REZENDE RIBEIRO ROCHA RODRIGUES SALES SAMPAIO SANTANA SANTOS SANTOS SILVA SILVEIRA SIQUEIRA SOARES
SOUSA SOUZA TAVARES TEIXEIRA TORRES VALENTE VASCONCELOS VAZ VIANA VIEIRA XAVIER JUNIOR JR FILHO FILHA NETO NETA SOBRINHO
""".split())


def eh_pessoa(nome, prenomes, vocab):
    if re.search(r"\d{11}", nome):          # MEI com CPF no nome
        return True
    toks = [t for t in re.sub(r"[^A-Z ]", " ", nome).split() if t not in CONECTIVOS and len(t) > 1]
    if not toks or toks[0] not in prenomes:
        return False
    return all(t in vocab for t in toks)


df = pd.read_csv(SRC, dtype=str, keep_default_na=False)
df = df[(df.situacao_cadastral == "2") & (df.nome_fantasia.str.strip() != "")]
df = df[df.cnae.str.startswith(tuple(CNAE_INCLUI))].copy()

nomes = df.nome_fantasia.str.upper().str.strip()

# Rótulos internos de rede ("FILIAL 449", "LOJA 12") não são o nome da fachada
generico = nomes.str.fullmatch(r"(FILIAL|LOJA|MATRIZ|UNIDADE|LJ)\s*\W*\s*\d+.*")
print("rótulos genéricos removidos:", generico.sum())
df, nomes = df[~generico].copy(), nomes[~generico]

# Amplia o vocabulário com os nomes de MEIs que trazem CPF no nome fantasia
mei = nomes[nomes.str.contains(r"\d{11}")].str.replace(r"[^A-Z ]", " ", regex=True).str.split()
prenomes = PRENOMES | {t[0] for t in mei if t}
vocab = prenomes | SOBRENOMES | {x for t in mei for x in t}

df["eh_pessoa"] = [eh_pessoa(n, prenomes, vocab) for n in nomes]
print("comércio de rua ativo c/ nome fantasia:", len(df))
print("classificados como nome de pessoa:", df.eh_pessoa.sum())
df[~df.eh_pessoa].drop(columns="eh_pessoa").to_csv(OUT, index=False)
df[df.eh_pessoa].to_csv(OUT.replace(".csv", "_excluidos_pessoa.csv"), index=False)
print("salvo:", OUT, len(df) - df.eh_pessoa.sum())
