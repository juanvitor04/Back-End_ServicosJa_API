from django.db import models
from accounts.models import PrestadorProfile

class PortfolioItem(models.Model):
    prestador = models.ForeignKey(
        PrestadorProfile, 
        on_delete=models.CASCADE, 
        related_name='portfolioitem_set'
    )
    
    imagem = models.ImageField(upload_to='portfolio/')
    descricao = models.CharField(max_length=255, blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.prestador.user.nome_completo}"