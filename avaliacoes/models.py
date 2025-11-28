from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator 

User = get_user_model()

class Avaliacao(models.Model):
    solicitacao_contato = models.OneToOneField(
        'contratacoes.SolicitacaoContato',
        on_delete=models.CASCADE,
        related_name='avaliacao'
    )
    
    # Nota de 1 a 5
    nota = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)] 
    )
    
    comentario = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('solicitacao_contato',)
        ordering = ['-data_criacao']
    
    def __str__(self):
        try:
            return f'Avaliação de {self.solicitacao_contato.cliente.first_name} (Nota: {self.nota})'
        except:
            return f'Avaliação (ID: {self.id})'
        