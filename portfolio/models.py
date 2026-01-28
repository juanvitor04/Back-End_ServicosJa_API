from django.db import models
from accounts.models import PrestadorProfile, ActiveManager
from django.utils import timezone

class PortfolioItem(models.Model):
    prestador = models.ForeignKey(
        PrestadorProfile, 
        on_delete=models.CASCADE, 
        related_name='portfolioitem_set'
    )
    
    imagem = models.ImageField(upload_to='portfolio/', null=True, blank=True)
    descricao = models.CharField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_portfolio_deleted'),
        ]

    def __str__(self):
        return f"Foto de {self.prestador.user.nome_completo}"
