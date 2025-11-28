from servicos.models import CategoriaServico, Servico

def criacao_servicos():
    menuData = [
        { 
            'label': 'Beleza e Bem-estar', 
            'subItems': [
                "Alongamento de unha",
                "Depilador/Epilador(a)",
                "Manicure/Pedicure",
                "Alongamento de cílios",
                "Especialista em megahair",
                "Massagista",
                "Barbeiro(a)",
                "Micropigmentador(a)",
                "Cabelereiro(a)",
                "Especialista em penteados",
                "Podólogo",
                "Colourista",
                "Esteticista",
                "Trancista",
                "Designer de sobrancelhas",
                "Lash designer",
                "Visagista",
                "Maquiador(a)"
            ]
        },
        { 
            'label': 'Cuidado Pessoal', 
            'subItems': [
                "Acupunturista",
                "Fisioterapeuta domiciliar",
                "Aromaterapeuta",
                "Personal trainer",
                "Auriculoterapeuta",
                "Quiropraxista",
                "Cuidador(a) de idosos",
                "Ventosaterapeuta",
                "Enfermeiro(a) particular"
            ] 
        },
        { 
            'label': 'Lazer e Eventos', 
            'subItems': [
                "Aluguel de brinquedos",
                "Decorador de festas",
                "Aluguel de equi. eletrônicos",
                "DJ/Músico",
                "Fotógrafo",
                "Aluguel de mesas e cadeiras",
                "Garçom/Barman",
                "Aluguel de fantasias",
                "Montador de eventos",
                "Animador/palhaço",
                "Sonoplastia/Téc. de som",
                "Buffet"
            ]
        },
        { 
            'label': 'Limpeza e Organização', 
            'subItems': [
                "Dedetizador",
                "Limpeza de estofados e colchões",
                "Diarista",
                "Enceramento de pisos",
                "Limpeza pós-obra",
                "Limpeza de ar-condicionado",
                "Limpeza de telhado",
                "Limpeza de caixa d'água",
                "Limpeza de vidro",
                "Limpeza de carpete",
                "Tratamento de pragas",
                "Zelador"
            ]
        },
        { 
            'label': 'Manutenção e Reparos', 
            'subItems': [
                "Borracheiro",
                "Eletricista",
                "Instalação de bomba e caixa d'água",
                "Chaveiro",
                "Encanador",
                "Conserto de armários",
                "Envernizador de móveis",
                "Manutenção de ventilador",
                "Conserto de eletrodomésticos",
                "Instalação de ar-condicionado",
                "Marceneiro",
                "Mecânico",
                "Conserto de fogões e fornos",
                "Instalação de câmeras",
                "Montador de móveis",
                "Instalação de TV e Home theater",
                "Pintor",
                "Conserto de máquina de lavar",
                "Téc. em refrigeração",
                "Vedação"
            ]
        },
        { 
            'label': 'Reforma e Construção', 
            'subItems': [
                "Aplicação de massa corrida",
                "Instalação de bancadas e pias",
                "Azulejista",
                "Instalação de Drywall",
                "Calheiro",
                "Instalação de portas e janelas",
                "Colocação de forro de PVC",
                "Instalação de telhados",
                "Fundação e alvenaria",
                "Pedreiro",
                "Gesseiro",
                "Reforma de fachadas",
                "Impermeabilização de lajes e paredes",
                "Reforma de pisos"
            ]
        },
        { 
            'label': 'Soluções Profissionais', 
            'subItems': [
                "Consultor de marketing",
                "Professor profisional",
                "Designer Gráfico",
                "Redator/Tradutor",
                "Editor de vídeo",
                "Téc. de informática e celular",
                "Social media",
                "Web designer",
                "Ilustrador digital"
            ]
        },
        { 
            'label': 'Transporte', 
            'subItems': [
                "Aluguel de caminhão",
                "Moto-boy",
                "Aluguel de carro/van",
                "Mudança comercial",
                "Frete",
                "Mudança residencial",
                "Guincho",
                "Transporte de animais"
            ]
        },
    ]

    for item in menuData:
        categoria_nome = item['label']
        servicos_lista = item['subItems']

        # Criar ou obter a categoria
        categoria, created = CategoriaServico.objects.get_or_create(
            nome=categoria_nome,
            defaults={'descricao': f'Serviços relacionados a {categoria_nome}'}
        )
        
        if created:
            print(f'Categoria criada: {categoria_nome}')
        else:
            print(f'Categoria já existente: {categoria_nome}')

        # Criar serviços para a categoria
        for servico_nome in servicos_lista:
            servico, created = Servico.objects.get_or_create(
                nome=servico_nome,
                categoria=categoria,
                defaults={'descricao': f'Serviço de {servico_nome}'}
            )
            
            if created:
                print(f'  - Serviço criado: {servico_nome}')
            else:
                print(f'  - Serviço já existente: {servico_nome}')

criacao_servicos()
