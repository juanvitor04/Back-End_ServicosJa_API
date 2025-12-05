import os
import random
import requests
from decimal import Decimal
from faker import Faker
from unittest.mock import patch
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

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
    lat = Decimal(str(random.uniform(-30.0, -5.0))).quantize(Decimal("0.00000001"))
    lon = Decimal(str(random.uniform(-60.0, -35.0))).quantize(Decimal("0.00000001"))
    return {
        'latitude': lat,
        'longitude': lon,
        'cidade': fake.city(),
        'bairro': fake.bairro() if hasattr(fake, 'bairro') else 'Centro',
        'estado': fake.state_abbr()
    }

def download_image(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return ContentFile(response.content, name=url.split("/")[-1])
    except Exception as e:
        print(f"Erro ao baixar imagem {url}: {e}")
    return None

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def handle(self, *args, **options):
        # Verifica se já existem usuários para evitar duplicação
        if User.objects.filter(tipo_usuario__in=['cliente', 'prestador']).exists():
            self.stdout.write(self.style.WARNING("Banco de dados já contém usuários. Pulando população."))
            return

        try:
            with transaction.atomic():
                self.create_services()
                clientes, prestadores = self.create_users_and_profiles()
                self.create_interactions(clientes, prestadores)
            self.stdout.write(self.style.SUCCESS("População de dados concluída com sucesso!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro durante a população de dados: {e}"))
            import traceback
            traceback.print_exc()
            raise e

    def create_services(self):
        self.stdout.write("Verificando/Criando Serviços e Categorias...")
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
        self.stdout.write(f"Serviços processados. Novos criados: {created_count}")

    def create_users_and_profiles(self):
        self.stdout.write("Criando Usuários e Perfis...")
        
        clientes = []
        prestadores = []
        
        with patch('accounts.models.pegar_dados_endereco', side_effect=mock_pegar_dados_endereco):
            
            # Criar 10 Clientes
            for i in range(10):
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
                
                profile = ClienteProfile.objects.create(
                    user=user,
                    telefone_contato=f"{random.randint(11, 99)}9{random.randint(10000000, 99999999)}",
                    cep=fake.postcode().replace('-', ''),
                    rua=fake.street_name(),
                    numero_casa=str(fake.building_number()),
                    complemento=f"Apto {random.randint(1, 100)}",
                )
                
                # Baixar foto de perfil (opcional para cliente, mas bom ter)
                gender = 'men' if user.genero == 'M' else 'women'
                img_url = f"https://randomuser.me/api/portraits/{gender}/{i+1}.jpg"
                img_file = download_image(img_url)
                if img_file:
                    profile.foto_perfil.save(f"cliente_{user.id}.jpg", img_file, save=True)

                clientes.append(user)
                self.stdout.write(f"Cliente criado: {full_name}")

            all_services = list(Servico.objects.all())
            if not all_services:
                self.stdout.write(self.style.ERROR("ERRO: Nenhum serviço encontrado."))
                return [], []

            # Criar 30 Prestadores
            for i in range(30):
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
                
                # Foto de Perfil
                gender = 'men' if user.genero == 'M' else 'women'
                # Usar IDs diferentes ou randomicos para variar
                img_id = random.randint(1, 99)
                img_url = f"https://randomuser.me/api/portraits/{gender}/{img_id}.jpg"
                img_file = download_image(img_url)
                if img_file:
                    prestador_profile.foto_perfil.save(f"prestador_{user.id}.jpg", img_file, save=True)
                
                # Criar 2 Itens de Portfólio
                for p_idx in range(2):
                    # Imagem aleatória do Picsum
                    portfolio_url = f"https://picsum.photos/seed/{user.id}_{p_idx}/400/300"
                    pf_file = download_image(portfolio_url)
                    
                    item = PortfolioItem.objects.create(
                        prestador=prestador_profile,
                        descricao=fake.sentence()
                    )
                    if pf_file:
                        item.imagem.save(f"portfolio_{user.id}_{p_idx}.jpg", pf_file, save=True)

                prestadores.append(user)
                self.stdout.write(f"Prestador criado: {full_name} ({main_service.nome})")
                
        return clientes, prestadores

    def create_interactions(self, clientes, prestadores):
        self.stdout.write("Criando Interações (Contratações e Avaliações)...")
        
        if not clientes or not prestadores:
            self.stdout.write("Sem clientes ou prestadores para interagir.")
            return

        # Para cada um dos 30 prestadores, garantir 3 serviços e 3 avaliações
        for prestador in prestadores:
            prestador_profile = prestador.perfil_prestador
            servico = prestador_profile.servico
            if not servico:
                # Tenta pegar do PrestadorServicos
                ps = PrestadorServicos.objects.filter(prestador_profile=prestador_profile).first()
                if ps:
                    servico = ps.servico
                else:
                    self.stdout.write(f"Prestador {prestador} sem serviço, pulando interações.")
                    continue

            # Selecionar 3 clientes aleatórios (pode repetir cliente se necessário, mas temos 10, então ok)
            selected_clientes = random.sample(clientes, 3)

            for cliente in selected_clientes:
                # Criar Solicitação (Serviço Realizado)
                solicitacao = SolicitacaoContato.objects.create(
                    cliente=cliente,
                    prestador=prestador,
                    servico=servico,
                    servico_realizado=True, # Assumindo que tem esse campo ou status
                    # Se tiver status, defina como concluído. Vou verificar models se der erro.
                    # O migration 0002_solicitacaocontato_servico_realizado.py sugere que o campo existe.
                )
                
                # Criar Avaliação
                Avaliacao.objects.create(
                    solicitacao_contato=solicitacao,
                    nota=random.randint(3, 5), # Notas boas para o exemplo
                    comentario=fake.sentence(),
                )
        
        self.stdout.write("Interações criadas com sucesso (3 por prestador).")
