"""Rótulos curtos, do jeito que se fala na rua, para os CNAEs do comércio de bairro (comercios_rua.csv).

O CNAE é a atividade principal declarada à Receita, não necessariamente o que a loja vende hoje.
Códigos genéricos ("outros produtos não especificados") ficam sem rótulo: melhor não dizer do que inventar.
"""

ROTULO = {
    '1091102': 'confeitaria',
    # veículos
    '4511101': 'revenda de carros', '4511102': 'carros usados', '4511103': 'revenda de carros', '4511104': 'caminhões',
    '4511105': 'reboques', '4511106': 'ônibus',
    '4520001': 'oficina mecânica', '4520002': 'lanternagem', '4520003': 'auto elétrica', '4520004': 'alinhamento',
    '4520005': 'lava-jato', '4520006': 'borracharia', '4520007': 'acessórios para carro', '4520008': 'capotaria',
    '4530701': 'autopeças', '4530702': 'pneus', '4530703': 'autopeças', '4530704': 'acessórios para carro',
    '4530705': 'pneus', '4530706': 'autopeças',
    '4541201': 'motos', '4541202': 'motos', '4541203': 'motos', '4541204': 'motos usadas', '4541206': 'peças de moto',
    '4541207': 'peças de moto', '4543900': 'oficina de moto',
    # mercados e comida
    '4711301': 'hipermercado', '4711302': 'supermercado', '4712100': 'mercadinho', '4713002': 'bazar',
    '4713004': 'loja de departamentos', '4713005': 'free shop',
    '4721102': 'padaria', '4721103': 'frios e laticínios', '4721104': 'doceria', '4722901': 'açougue', '4722902': 'peixaria',
    '4723700': 'depósito de bebidas', '4724500': 'hortifrúti', '4729601': 'tabacaria', '4729602': 'loja de conveniência',
    '4729699': 'empório',
    '4731800': 'posto de gasolina', '4732600': 'troca de óleo',
    # casa e construção
    '4741500': 'loja de tintas', '4742300': 'material elétrico', '4743100': 'vidraçaria', '4744001': 'ferragens',
    '4744002': 'madeireira', '4744003': 'material hidráulico', '4744004': 'areia e pedra', '4744005': 'material de construção',
    '4744006': 'marmoraria', '4744099': 'material de construção',
    '4751201': 'informática', '4751202': 'automação comercial', '4752100': 'celulares', '4753900': 'eletrodomésticos',
    '4754701': 'móveis', '4754702': 'colchões', '4754703': 'iluminação', '4755501': 'tecidos', '4755502': 'armarinho',
    '4755503': 'cama, mesa e banho', '4756300': 'instrumentos musicais', '4757100': 'peças de eletrônicos',
    '4759801': 'cortinas e tapetes', '4759899': 'utilidades domésticas',
    # cultura, lazer e esporte
    '4761001': 'livraria', '4761002': 'banca de jornal', '4761003': 'papelaria', '4762800': 'discos', '4763601': 'brinquedos',
    '4763602': 'artigos esportivos', '4763603': 'bicicletaria', '4763604': 'pesca e camping', '4763605': 'náutica',
    # saúde, beleza e roupa
    '4771701': 'farmácia', '4771702': 'farmácia de manipulação', '4771703': 'farmácia homeopática',
    '4771704': 'remédios veterinários', '4772500': 'perfumaria', '4773300': 'artigos ortopédicos', '4774100': 'ótica',
    '4781400': 'roupas', '4782201': 'calçados', '4782202': 'bolsas e malas', '4783101': 'joalheria', '4783102': 'relojoaria',
    # outros varejos
    '4784900': 'gás', '4785701': 'antiquário', '4785799': 'brechó', '4789001': 'bijuterias e artesanato',
    '4789002': 'floricultura', '4789003': 'galeria de arte', '4789004': 'pet shop', '4789005': 'produtos de limpeza',
    '4789006': 'fogos de artifício', '4789007': 'artigos de escritório', '4789008': 'artigos de fotografia',
    '4789099': '',
    # hospedagem, comida pronta e serviços
    '5510801': 'hotel', '5510802': 'apart-hotel', '5510803': 'motel', '5590601': 'hostel',
    '5611201': 'restaurante', '5611203': 'lanchonete', '5611204': 'bar', '5611205': 'bar com música',
    '5914600': 'cinema', '6421200': 'banco', '6422100': 'banco',
    '7500100': 'clínica veterinária', '8219901': 'copiadora', '8299706': 'lotérica', '9313100': 'academia',
    '9511800': 'conserto de computador', '9512600': 'conserto de celular', '9521500': 'conserto de eletrodomésticos',
    '9529101': 'sapateiro', '9529102': 'chaveiro', '9529103': 'conserto de relógio', '9529104': 'conserto de bicicleta',
    '9529105': 'conserto de móveis', '9529106': 'conserto de joias', '9529199': 'consertos',
    '9601701': 'lavanderia', '9601702': 'tinturaria', '9601703': 'lavanderia',
    '9602501': 'salão de beleza', '9602502': 'estética',
    '9603301': 'funerária', '9603302': 'funerária', '9603303': 'funerária', '9603304': 'funerária', '9603305': 'funerária',
    '9603399': 'funerária',
    '9609208': 'banho e tosa',
}


def rotulo(cnae):
    """O tipo do comércio em poucas palavras; vazio quando o código é genérico ou desconhecido."""
    return ROTULO.get(cnae, '')
