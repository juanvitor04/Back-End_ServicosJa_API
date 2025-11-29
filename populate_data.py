import os
import django
import random
from datetime import date, timedelta
from decimal import Decimal
from faker import Faker
from unittest.mock import patch

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from django.db import transaction
from django.contrib.auth import get_user_model

from accounts.models import ClienteProfile, PrestadorProfile
from servicos.models import CategoriaServico, Servico, PrestadorServicos
from contratacoes.models import SolicitacaoContato
from avaliacoes.models import Avaliacao
from portfolio.models import PortfolioItem

User = get_user_model()
fake = Faker('pt_BR')

MENU_DATA = [
    { 
        'label': 'Beleza e Bem-estar', 
        'subItems': [
            "Alongamento de unha", "Depilador/Epilador(a)", "Manicure/Pedicure",
            "Alongamento de cílios", "Especialista em megahair", "Massagista",
            "Barbeiro(a)", "Micropigmentador(a)", "Cabelereiro(a)",
            "Especialista em penteados", "Podólogo", "Colourista", "Esteticista",
            "Trancista", "Designer de sobrancelhas", "Lash designer",
            "Visagista", "Maquiador(a)"
        ]
    },
    { 
        'label': 'Cuidado Pessoal', 
        'subItems': [
            "Acupunturista", "Fisioterapeuta domiciliar", "Aromaterapeuta",
            "Personal trainer", "Auriculoterapeuta", "Quiropraxista",
            "Cuidador(a) de idosos", "Ventosaterapeuta", "Enfermeiro(a) particular"
        ] 
    },
    { 
        'label': 'Lazer e Eventos', 
        'subItems': [
            "Aluguel de brinquedos", "Decorador de festas", "Aluguel de equi. eletrônicos",
            "DJ/Músico", "Fotógrafo", "Aluguel de mesas e cadeiras", "Garçom/Barman",
            "Aluguel de fantasias", "Montador de eventos", "Animador/palhaço",
            "Sonoplastia/Téc. de som", "Buffet"
        ]
    },
    { 
        'label': 'Limpeza e Organização', 
        'subItems': [
            "Dedetizador", "Limpeza de estofados e colchões", "Diarista",
            "Enceramento de pisos", "Limpeza pós-obra", "Limpeza de ar-condicionado",
            "Limpeza de telhado", "Limpeza de caixa d'água", "Limpeza de vidro",
            "Limpeza de carpete", "Tratamento de pragas", "Zelador"
        ]
    },
    { 
        'label': 'Manutenção e Reparos', 
        'subItems': [
            "Borracheiro", "Eletricista", "Instalação de bomba e caixa d'água",
            "Chaveiro", "Encanador", "Conserto de armários", "Envernizador de móveis",
            "Manutenção de ventilador", "Conserto de eletrodomésticos",
            "Instalação de ar-condicionado", "Marceneiro", "Mecânico",
            "Conserto de fogões e fornos", "Instalação de câmeras",
            "Montador de móveis", "Instalação de TV e Home theater", "Pintor",
            "Conserto de máquina de lavar", "Téc. em refrigeração", "Vedação"
        ]
    },
    { 
        'label': 'Reforma e Construção', 
        'subItems': [
            "Aplicação de massa corrida", "Instalação de bancadas e pias", "Azulejista",
            "Instalação de Drywall", "Calheiro", "Instalação de portas e janelas",
            "Colocação de forro de PVC", "Instalação de telhados",
            "Fundação e alvenaria", "Pedreiro", "Gesseiro", "Reforma de fachadas",
            "Impermeabilização de lajes e paredes", "Reforma de pisos"
        ]
    },
    { 
        'label': 'Soluções Profissionais', 
        'subItems': [
            "Consultor de marketing", "Professor profisional", "Designer Gráfico",
            "Redator/Tradutor", "Editor de vídeo", "Téc. de informática e celular",
            "Social media", "Web designer", "Ilustrador digital"
        ]
    },
    { 
        'label': 'Transporte', 
        'subItems': [
            "Aluguel de caminhão", "Moto-boy", "Aluguel de carro/van",
            "Mudança comercial", "Frete", "Mudança residencial",
            "Guincho", "Transporte de animais"
        ]
    },
]

def mock_pegar_dados_endereco(cep, rua, numero):
    # Return random coordinates within Brazil (roughly)
    # Latitude: -33 to 5
    # Longitude: -74 to -34
    lat = Decimal(str(random.uniform(-30.0, -5.0))).quantize(Decimal("0.00000001"))
    lon = Decimal(str(random.uniform(-60.0, -35.0))).quantize(Decimal("0.00000001"))
    return {
        'latitude': lat,
        'longitude': lon,
        'cidade': fake.city(),
        'bairro': fake.bairro() if hasattr(fake, 'bairro') else 'Centro',
        'estado': fake.state_abbr()
    }

def create_services():
    print("Verificando/Criando Serviços e Categorias...")
    created_count = 0
    for item in MENU_DATA:
        categoria, _ = CategoriaServico.objects.get_or_create(
            nome=item['label'],
            defaults={'descricao': f"Serviços de {item['label']}"}
        )
        for serv_name in item['subItems']:
            _, created = Servico.objects.get_or_create(
                nome=serv_name,
                categoria=categoria,
                defaults={'descricao': f"Serviço de {serv_name}"}
            )
            if created:
                created_count += 1
    print(f"Serviços processados. Novos criados: {created_count}")

def create_users_and_profiles():
    print("Criando Usuários e Perfis...")
    
    clientes = []
    prestadores = []
    
    with patch('accounts.models.pegar_dados_endereco', side_effect=mock_pegar_dados_endereco):
        
        for _ in range(20):
            email = fake.unique.email()
            first_name = fake.first_name()
            last_name = fake.last_name()
            full_name = f"{first_name} {last_name}"
            
            user = User.objects.create_user(
                username=email,
                email=email,
                password='password123',
                nome_completo=full_name,
                tipo_usuario='cliente',
                dt_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=80),
                genero=random.choice(['M', 'F']),
                cpf=fake.cpf().replace('.', '').replace('-', '')
            )
            
            ClienteProfile.objects.create(
                user=user,
                telefone_contato=f"{random.randint(11, 99)}9{random.randint(10000000, 99999999)}",
                cep=fake.postcode().replace('-', ''),
                rua=fake.street_name(),
                numero_casa=str(fake.building_number()),
                complemento=f"Apto {random.randint(1, 100)}",
            )
            clientes.append(user)
            print(f"Cliente criado: {full_name}")

        all_services = list(Servico.objects.all())
        if not all_services:
            print("ERRO: Nenhum serviço encontrado. Execute a criação de serviços primeiro.")
            return [], []

        for _ in range(20):
            email = fake.unique.email()
            first_name = fake.first_name()
            last_name = fake.last_name()
            full_name = f"{first_name} {last_name}"
            
            user = User.objects.create_user(
                username=email,
                email=email,
                password='password123',
                nome_completo=full_name,
                tipo_usuario='prestador',
                dt_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=80),
                genero=random.choice(['M', 'F']),
                cpf=fake.cpf().replace('.', '').replace('-', '')
            )
            
            main_service = random.choice(all_services)
            
            prestador_profile = PrestadorProfile.objects.create(
                user=user,
                biografia=fake.text(max_nb_chars=200),
                telefone_publico=f"{random.randint(11, 99)}9{random.randint(10000000, 99999999)}",
                cep=fake.postcode().replace('-', ''),
                rua=fake.street_name(),
                numero_casa=str(fake.building_number()),
                disponibilidade=fake.boolean(),
                possui_material_proprio=fake.boolean(),
                atende_fim_de_semana=fake.boolean(),
                servico=main_service
            )
            
            PrestadorServicos.objects.create(
                prestador_profile=prestador_profile,
                servico=main_service
            )
            
            prestadores.append(user)
            print(f"Prestador criado: {full_name} ({main_service.nome})")
            
    return clientes, prestadores

def create_interactions(clientes, prestadores):
    print("Criando Interações (Contratações e Avaliações)...")
    
    if not clientes or not prestadores:
        print("Sem clientes ou prestadores para interagir.")
        return

    for _ in range(40):
        cliente = random.choice(clientes)
        prestador = random.choice(prestadores)
        
        try:
            prestador_profile = prestador.perfil_prestador
            servico = prestador_profile.servico
            if not servico:
                ps = PrestadorServicos.objects.filter(prestador_profile=prestador_profile).first()
                if ps:
                    servico = ps.servico
                else:
                    continue
        except Exception as e:
            print(f"Erro ao obter perfil prestador: {e}")
            continue

        solicitacao = SolicitacaoContato.objects.create(
            cliente=cliente,
            prestador=prestador,
            servico=servico
        )
        
        if random.random() < 0.7:
            Avaliacao.objects.create(
                solicitacao_contato=solicitacao,
                nota=random.randint(1, 5),
                comentario=fake.sentence(),
            )
            
    print("Interações criadas.")

def run():
    try:
        with transaction.atomic():
            create_services()
            clientes, prestadores = create_users_and_profiles()
            create_interactions(clientes, prestadores)
        print("População de dados concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a população de dados: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run()
