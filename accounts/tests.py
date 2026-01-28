from django.test import TestCase
from django.utils import timezone
from accounts.models import User, ClienteProfile, PrestadorProfile
from servicos.models import CategoriaServico, Servico, PrestadorServicos
from portfolio.models import PortfolioItem
from contratacoes.models import SolicitacaoContato
from avaliacoes.models import Avaliacao


class SoftDeleteCascataTest(TestCase):
    """
    Testes para verificar soft delete e cascata de exclusão
    """

    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar categoria e serviço
        self.cat = CategoriaServico.objects.create(nome='Beleza')
        self.servico = Servico.objects.create(nome='Corte', categoria=self.cat)

        # Criar cliente
        self.cliente = User.objects.create(
            username='cliente_test',
            email='cliente@test.com',
            nome_completo='Cliente Teste',
            tipo_usuario='cliente'
        )
        self.cliente.set_password('pass')
        self.cliente.save()
        self.perfil_cliente = ClienteProfile.objects.create(
            user=self.cliente,
            cep='01001000',
            rua='Praça',
            numero_casa='1'
        )

        # Criar prestador
        self.prestador = User.objects.create(
            username='prestador_test',
            email='prestador@test.com',
            nome_completo='Prestador Teste',
            tipo_usuario='prestador'
        )
        self.prestador.set_password('pass')
        self.prestador.save()
        self.perfil_prestador = PrestadorProfile.objects.create(
            user=self.prestador,
            cep='01001000',
            rua='Praça',
            numero_casa='2',
            telefone_publico='11999990000'
        )

        # Criar dados relacionados
        self.portfolio = PortfolioItem.objects.create(
            prestador=self.perfil_prestador,
            descricao='Trabalho Teste'
        )
        self.prestador_servico = PrestadorServicos.objects.create(
            prestador_profile=self.perfil_prestador,
            servico=self.servico
        )
        self.solicitacao = SolicitacaoContato.objects.create(
            cliente=self.cliente,
            prestador=self.prestador,
            servico=self.servico
        )
        self.avaliacao = Avaliacao.objects.create(
            solicitacao_contato=self.solicitacao,
            nota=4,
            comentario='Teste'
        )

    def test_soft_delete_user_marca_is_deleted_true(self):
        """Testa se soft delete marca is_deleted=True"""
        self.prestador.delete()
        
        prestador_recarregado = User.all_objects.get(pk=self.prestador.pk)
        self.assertTrue(prestador_recarregado.is_deleted)
        self.assertIsNotNone(prestador_recarregado.deleted_at)

    def test_soft_delete_usuario_nao_aparece_em_objects(self):
        """Testa se usuário deletado não aparece em objects.all()"""
        self.prestador.delete()
        
        # Deve estar em all_objects (todos os registros)
        self.assertTrue(User.all_objects.filter(pk=self.prestador.pk).exists())
        
        # Não deve estar em objects (apenas ativos)
        self.assertFalse(User.objects.filter(pk=self.prestador.pk).exists())

    def test_cascata_soft_delete_prestador_profile(self):
        """Testa se PrestadorProfile é marcado como deletado"""
        self.prestador.delete()
        
        perfil_recarregado = PrestadorProfile.all_objects.get(pk=self.perfil_prestador.pk)
        self.assertTrue(perfil_recarregado.is_deleted)
        self.assertIsNotNone(perfil_recarregado.deleted_at)

    def test_cascata_soft_delete_portfolio(self):
        """Testa se PortfolioItem é marcado como deletado"""
        self.prestador.delete()
        
        portfolio_recarregado = PortfolioItem.all_objects.get(pk=self.portfolio.pk)
        self.assertTrue(portfolio_recarregado.is_deleted)
        self.assertIsNotNone(portfolio_recarregado.deleted_at)

    def test_cascata_soft_delete_prestador_servicos(self):
        """Testa se PrestadorServicos é marcado como deletado"""
        self.prestador.delete()
        
        ps_recarregado = PrestadorServicos.all_objects.get(pk=self.prestador_servico.pk)
        self.assertTrue(ps_recarregado.is_deleted)
        self.assertIsNotNone(ps_recarregado.deleted_at)

    def test_cascata_soft_delete_solicitacao_contato(self):
        """Testa se SolicitacaoContato é marcada como deletada"""
        self.prestador.delete()
        
        sol_recarregado = SolicitacaoContato.all_objects.get(pk=self.solicitacao.pk)
        self.assertTrue(sol_recarregado.is_deleted)
        self.assertIsNotNone(sol_recarregado.deleted_at)

    def test_cascata_completa(self):
        """Testa se toda a cascata funciona corretamente"""
        # Antes do delete
        self.assertFalse(User.all_objects.get(pk=self.prestador.pk).is_deleted)
        self.assertFalse(PrestadorProfile.all_objects.get(pk=self.perfil_prestador.pk).is_deleted)
        self.assertFalse(PortfolioItem.all_objects.get(pk=self.portfolio.pk).is_deleted)
        self.assertFalse(PrestadorServicos.all_objects.get(pk=self.prestador_servico.pk).is_deleted)
        self.assertFalse(SolicitacaoContato.all_objects.get(pk=self.solicitacao.pk).is_deleted)

        # Executar delete
        self.prestador.delete()

        # Depois do delete - todos devem estar marcados
        self.assertTrue(User.all_objects.get(pk=self.prestador.pk).is_deleted)
        self.assertTrue(PrestadorProfile.all_objects.get(pk=self.perfil_prestador.pk).is_deleted)
        self.assertTrue(PortfolioItem.all_objects.get(pk=self.portfolio.pk).is_deleted)
        self.assertTrue(PrestadorServicos.all_objects.get(pk=self.prestador_servico.pk).is_deleted)
        self.assertTrue(SolicitacaoContato.all_objects.get(pk=self.solicitacao.pk).is_deleted)

    def test_hard_delete_remove_fisicamente(self):
        """Testa se hard_delete remove o registro fisicamente"""
        pk_prestador = self.prestador.pk
        
        # Soft delete primeiro
        self.prestador.delete()
        self.assertTrue(User.all_objects.filter(pk=pk_prestador).exists())
        
        # Depois hard delete
        User.all_objects.get(pk=pk_prestador).hard_delete()
        self.assertFalse(User.all_objects.filter(pk=pk_prestador).exists())

    def test_filtro_objects_exclui_deletados(self):
        """Testa se objects.filter() exclui registros deletados"""
        self.prestador.delete()
        
        # objects não deve retornar
        self.assertEqual(User.objects.filter(pk=self.prestador.pk).count(), 0)
        
        # all_objects deve retornar
        self.assertEqual(User.all_objects.filter(pk=self.prestador.pk).count(), 1)

    def test_portfolio_objects_filtra_deletados(self):
        """Testa se PortfolioItem.objects também filtra deletados"""
        self.prestador.delete()
        
        # objects não deve retornar o portfolio deletado
        self.assertEqual(PortfolioItem.objects.filter(pk=self.portfolio.pk).count(), 0)
        
        # all_objects deve retornar
        self.assertEqual(PortfolioItem.all_objects.filter(pk=self.portfolio.pk).count(), 1)

    def test_cliente_delete_cascata(self):
        """Testa cascata de delete para cliente"""
        self.cliente.delete()
        
        # Cliente deve estar marcado como deletado
        self.assertTrue(User.all_objects.get(pk=self.cliente.pk).is_deleted)
        
        # ClienteProfile deve estar marcado como deletado
        self.assertTrue(ClienteProfile.all_objects.get(pk=self.perfil_cliente.pk).is_deleted)
        
        # SolicitacaoContato (como cliente) deve estar deletada
        self.assertTrue(SolicitacaoContato.all_objects.get(pk=self.solicitacao.pk).is_deleted)

    def test_timestamps_deleted_at_preenchidos(self):
        """Testa se deleted_at é preenchido corretamente"""
        before = timezone.now()
        self.prestador.delete()
        after = timezone.now()
        
        prestador = User.all_objects.get(pk=self.prestador.pk)
        self.assertIsNotNone(prestador.deleted_at)
        self.assertGreaterEqual(prestador.deleted_at, before)
        self.assertLessEqual(prestador.deleted_at, after)
