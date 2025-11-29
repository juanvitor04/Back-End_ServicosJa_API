from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import ClienteProfile, PrestadorProfile
from servicos.models import CategoriaServico, Servico
from contratacoes.models import SolicitacaoContato
from avaliacoes.models import Avaliacao

User = get_user_model()

class UserProfileTests(APITestCase):
    def setUp(self):
        # Setup common data
        self.categoria = CategoriaServico.objects.create(nome='Manutenção', descricao='Serviços de manutenção')
        self.servico = Servico.objects.create(nome='Encanador', categoria=self.categoria)

        # Create Cliente User
        self.cliente_data = {
            'email': 'cliente@test.com',
            'nome_completo': 'Cliente Teste',
            'password': 'password123',
            'tipo_usuario': 'cliente',
            'cpf': '11122233344'
        }
        # Explicitly pass username as email because AbstractUser requires it
        self.cliente_user = User.objects.create_user(username=self.cliente_data['email'], **self.cliente_data)
        ClienteProfile.objects.create(
            user=self.cliente_user,
            telefone_contato='11999999999',
            cep='01001000',
            rua='Praça da Sé',
            numero_casa='100',
            cidade='São Paulo',
            estado='SP'
        )
        
        # Create Prestador User
        self.prestador_data = {
            'email': 'prestador@test.com',
            'nome_completo': 'Prestador Teste',
            'password': 'password123',
            'tipo_usuario': 'prestador',
            'cpf': '55566677788'
        }
        # Explicitly pass username as email because AbstractUser requires it
        self.prestador_user = User.objects.create_user(username=self.prestador_data['email'], **self.prestador_data)
        PrestadorProfile.objects.create(
            user=self.prestador_user,
            telefone_publico='11888888888',
            cep='01001000',
            rua='Praça da Sé',
            numero_casa='200',
            cidade='São Paulo',
            estado='SP',
            servico=self.servico
        )

        # Get Tokens
        response = self.client.post('/api/auth/token/login/', {
            'email': 'cliente@test.com',
            'password': 'password123'
        })
        self.cliente_token = response.data['access']

        response = self.client.post('/api/auth/token/login/', {
            'email': 'prestador@test.com',
            'password': 'password123'
        })
        self.prestador_token = response.data['access']

    def test_get_own_profile_cliente(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cliente_token)
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.cliente_data['email'])
        self.assertIn('perfil_cliente', response.data)
        self.assertNotIn('perfil_prestador', response.data)
        self.assertEqual(response.data['perfil_cliente']['telefone_contato'], '11999999999')

    def test_update_own_profile_cliente(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.cliente_token)
        url = reverse('user-profile')
        data = {
            'nome_completo': 'Cliente Atualizado',
            'perfil_cliente': {
                'telefone_contato': '11777777777'
            }
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cliente_user.refresh_from_db()
        self.assertEqual(self.cliente_user.nome_completo, 'Cliente Atualizado')
        self.assertEqual(self.cliente_user.perfil_cliente.telefone_contato, '11777777777')

class PrestadorDetailStatsTests(APITestCase):
    def setUp(self):
        self.categoria = CategoriaServico.objects.create(nome='Manutenção', descricao='Serviços de manutenção')
        self.servico = Servico.objects.create(nome='Encanador', categoria=self.categoria)
        
        # Cliente
        self.cliente = User.objects.create_user(
            username='cliente@test.com',
            email='cliente@test.com',
            password='password123',
            tipo_usuario='cliente',
            nome_completo='Cliente Teste'
        )
        ClienteProfile.objects.create(user=self.cliente, cep='00000000', rua='Rua', numero_casa='1')
        
        # Prestador
        self.prestador = User.objects.create_user(
            username='prestador@test.com',
            email='prestador@test.com',
            password='password123',
            tipo_usuario='prestador',
            nome_completo='Prestador Teste'
        )
        self.prestador_profile = PrestadorProfile.objects.create(
            user=self.prestador, 
            cep='00000000', rua='Rua', numero_casa='1',
            servico=self.servico,
            telefone_publico='11999999999'
        )
        
        # Avaliações
        solic1 = SolicitacaoContato.objects.create(cliente=self.cliente, prestador=self.prestador, servico=self.servico)
        Avaliacao.objects.create(solicitacao_contato=solic1, nota=5, comentario='Excelente')
        
        solic2 = SolicitacaoContato.objects.create(cliente=self.cliente, prestador=self.prestador, servico=self.servico)
        Avaliacao.objects.create(solicitacao_contato=solic2, nota=4, comentario='Bom')
        
        # Update cache manually since signals might run differently in tests or we want to ensure
        # But wait, signals run in tests by default unless disabled.
        # But total_avaliacoes_cache relies on signal. I'll rely on it or update manually if needed.
        # The serializer uses cache for total, but calculate counts on fly.
        self.prestador_profile.total_avaliacoes_cache = 2
        self.prestador_profile.save()

    def test_prestador_detail_includes_stats(self):
        url = reverse('detalhe-prestador', kwargs={'pk': self.prestador_profile.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('estatisticas', data)
        self.assertIn('distribuicao', data['estatisticas'])
        
        dist = data['estatisticas']['distribuicao']
        self.assertEqual(dist['estrelas_5']['quantidade'], 1)
        self.assertEqual(dist['estrelas_4']['quantidade'], 1)
        self.assertEqual(dist['estrelas_1']['quantidade'], 0)
        
        # Verify percentages
        # Since total=2, 1 is 50%
        self.assertEqual(dist['estrelas_5']['porcentagem'], 50.0)
