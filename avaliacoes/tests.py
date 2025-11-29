from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from servicos.models import Servico, CategoriaServico
from contratacoes.models import SolicitacaoContato
from avaliacoes.models import Avaliacao

User = get_user_model()

class AvaliacaoListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.cliente = User.objects.create_user(
            username='cliente', 
            email='cliente@example.com', 
            password='password123',
            nome_completo='Cliente Teste',
            tipo_usuario='cliente'
        )
        self.prestador = User.objects.create_user(
            username='prestador', 
            email='prestador@example.com', 
            password='password123',
            nome_completo='Prestador Teste',
            tipo_usuario='prestador'
        )
        
        # Create service
        self.categoria = CategoriaServico.objects.create(nome='Categoria Teste')
        self.servico = Servico.objects.create(
            nome='Servico Teste', 
            categoria=self.categoria
        )
        
        # Create solicitations and evaluations
        # 1x 5 stars
        solic1 = SolicitacaoContato.objects.create(cliente=self.cliente, prestador=self.prestador, servico=self.servico)
        Avaliacao.objects.create(solicitacao_contato=solic1, nota=5, comentario='Excelente')
        
        # 1x 4 stars
        solic2 = SolicitacaoContato.objects.create(cliente=self.cliente, prestador=self.prestador, servico=self.servico)
        Avaliacao.objects.create(solicitacao_contato=solic2, nota=4, comentario='Bom')
        
        self.url = reverse('listar-avaliacoes')

    def test_list_avaliacoes_stats(self):
        # Filter by prestador
        response = self.client.get(self.url, {'prestador': self.prestador.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        
        # Check structure
        self.assertIn('estatisticas', data)
        self.assertIn('avaliacoes', data)
        
        stats = data['estatisticas']
        self.assertEqual(stats['total_avaliacoes'], 2)
        self.assertEqual(stats['media_geral'], 4.5)
        
        dist = stats['distribuicao']
        self.assertEqual(dist['estrelas_5']['quantidade'], 1)
        self.assertEqual(dist['estrelas_5']['porcentagem'], 50.0)
        self.assertEqual(dist['estrelas_4']['quantidade'], 1)
        self.assertEqual(dist['estrelas_4']['porcentagem'], 50.0)
        self.assertEqual(dist['estrelas_1']['quantidade'], 0)
        
        # Check avaliacoes list
        self.assertEqual(len(data['avaliacoes']), 2)
        self.assertEqual(data['avaliacoes'][0]['cliente_nome'], 'Cliente Teste')
