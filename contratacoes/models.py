from django.db import models
from django.contrib.auth import get_user_model
from servicos.models import Servico
from accounts.models import ActiveManager
from django.utils import timezone

User = get_user_model()

class SolicitacaoContato(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contatos_iniciados')
    prestador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contatos_recebidos')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    
    servico_realizado = models.BooleanField(default=False)
    data_clique = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_solicitacao_deleted'),
        ]

    @property
    def avaliacao_realizada(self):
        return hasattr(self, 'avaliacao')

    def __str__(self):
        return f"Contato: {self.cliente.nome_completo} -> {self.prestador.nome_completo} ({self.servico.nome})"
