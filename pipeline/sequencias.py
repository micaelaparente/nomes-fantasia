"""Nomes de destaque de cada capítulo, escolhidos à mão, em grupos com rótulo.

Cada nome é [como está nos dados, como aparece no site]; o 07_exporta.py procura o nome nos dados e avisa o que não achou.
"""

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
        ['De Portugal', ['Bigode do Portuga', 'Bigode do Portuga'], ['Lava Jato do Portuga', 'Lava-Jato do Portuga'],
         ['Tasquinha do Portuga', 'Tasquinha do Portuga'], ['Luso Carioca', 'Luso Carioca']],
        ['Da Itália, do Oriente', ['Inverno d Italia', "Inverno d'Itália"], ['Botekim do Japa', 'Botekim do Japa'],
         ['Japa da Hora', 'Japa da Hora'], ['China Armacoes', 'China Armações']],
        ['Do Nordeste', ['Pernambucana da Gema', 'Pernambucana da Gema'], ['Quebra Cangalha do Sertao', 'Quebra Cangalha do Sertão'],
         ['Arretado Bom Demais', 'Arretado Bom Demais'], ['Radiadores O Paraiba', 'Radiadores O Paraíba']],
        ['De Minas e do Sul', ['Jeitim Mineiro', 'Jeitim Mineiro'], ['Pet Uai', 'Pet Uai'],
         ['Mineira das Baterias', 'Mineira das Baterias'], ['Gaucho Reciclagem', 'Gaúcho Reciclagem']],
        ['Da França', ['Madame Chica Salao de Beleza', 'Madame Chica'], ['Frango Chic', 'Frango Chic'], ['Hortifruti Monsieur', 'Hortifruti Monsieur'],
         ['Mercadinho du Fogo', 'Mercadinho du Fogo']],
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
