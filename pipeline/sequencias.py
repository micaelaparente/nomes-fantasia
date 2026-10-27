"""Nomes de destaque de cada capítulo, escolhidos à mão, em grupos com rótulo.

Cada nome é [como está nos dados, como aparece no site]; o 07_exporta.py procura o nome nos dados e avisa o que não achou.
"""

# Sequências: grupos com rótulo e nomes [como está nos dados, como aparece]. A página alterna entre os grupos
# (um de cada por vez), para mostrar variedade com fio condutor; frases e sotaques são uma lista só, em ordem.
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
    'poder': [
        # poder: o pequeno comércio que se coroa, se faz império ou vira repartição
        ['Reis e rainhas', ['Rei do Joelho', 'Rei do Joelho'], ['Rainha do Bacalhau', 'Rainha do Bacalhau'],
         ['O Rei do Velocimetro', 'O Rei do Velocímetro'], ['Princesa do Gas', 'Princesa do Gás'], ['Rei do Latao', 'Rei do Latão']],
        ['Impérios e palácios', ['Imperio do Ovo Mc', 'Império do Ovo'], ['Palacio das Racoes', 'Palácio das Rações'],
         ['Castelo do Frio', 'Castelo do Frio'], ['Reino do Biscoito Areal', 'Reino do Biscoito'], ['Nobreza Canina', 'Nobreza Canina']],
        ['República e patentes', ['Ministerio da Pizza', 'Ministério da Pizza'], ['Republica do Crepe', 'República do Crepe'],
         ['Loterica Adeus Patrao', 'Lotérica Adeus Patrão'], ['Mestre do Amassado', 'Mestre do Amassado'],
         ['Tribunal Restaurante', 'Tribunal Restaurante']],
    ],
    'culturas': [
        # sotaques: uma lista só, do mais inusitado ao menos, alternando as línguas
        ['Sotaques', ['Oxe e do Nordeste', 'Oxe É do Nordeste'], ['King do Gelo', 'King do Gelo'],
         ['Arretado Bom Demais', 'Arretado Bom Demais'], ['Le Petit Recreio', 'Le Petit Recreio'],
         ['World dos Cabelos', 'World dos Cabelos'], ['Pet Uai', 'Pet Uai'], ['Le Pain Carioca', 'Le Pain Carioca'],
         ["Casa Fruta's", "Casa Fruta's"], ['Mineira das Baterias', 'Mineira das Baterias'],
         ['Le Crepe Carioca', 'Le Crêpe Carioca'], ['Phone do Gabriel', 'Phone do Gabriel'],
         ['Radiadores O Paraiba', 'Radiadores O Paraíba'], ['Cafe du Recanto', 'Café du Recanto'],
         ["Budega's Brasa", "Budega's Brasa"], ['Mineiro dos Passaros', 'Mineiro dos Pássaros'],
         ['Make do Isaias', 'Make do Isaías'], ['Le Figuier et Lolivier', "Le Figuier et l'Olivier"],
         ["Terapia dos Cachos's", "Terapia dos Cachos's"], ['Vixi Restaurante Nordestino', 'Vixi Restaurante Nordestino'],
         ["Nilza's Modas", "Nilza's Modas"], ['Chez la Mer', 'Chez la Mer'],
         ['Barbearia e Tattoo do Mineiro', 'Barbearia e Tattoo do Mineiro'], ['Le Petit Macaron', 'Le Petit Macaron'],
         ['Maison de Fromage', 'Maison de Fromage'], ['Le Cafe d Ici', "Le Café d'Ici"],
         ['Amelie Creperie et Bistrot', 'Amélie Creperie et Bistrot'], ["Chez l'Ami Brasserie", "Chez l'Ami Brasserie"],
         ['Le Ble Noir Creperie', 'Le Blé Noir Creperie']],
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
