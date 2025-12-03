from django.db import models
from django.contrib.auth import get_user_model
from servicos.models import Servico

User = get_user_model()

class SolicitacaoContato(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contatos_iniciados')
    prestador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contatos_recebidos')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    
    servico_realizado = models.BooleanField(default=False)
    data_clique = models.DateTimeField(auto_now_add=True)

    @property
    def avaliacao_realizada(self):
        return hasattr(self, 'avaliacao')

    def __str__(self):
        return f"Contato: {self.cliente.first_name} -> {self.prestador.first_name} ({self.servico.nome})"
