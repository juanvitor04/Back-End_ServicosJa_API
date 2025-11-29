from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from avaliacoes.models import Avaliacao
from contratacoes.models import SolicitacaoContato
from .models import PrestadorProfile

#Isso aqui é para atualizar notas e não ficar preso ao cache.
@receiver([post_save, post_delete], sender=Avaliacao)
def atualizar_cache_avaliacao(sender, instance, **kwargs):
    try:
        prestador_user = instance.solicitacao_contato.prestador
        profile = PrestadorProfile.objects.get(user=prestador_user)
        
        todas_avaliacoes = Avaliacao.objects.filter(
            solicitacao_contato__prestador=prestador_user
        )
    
        total = todas_avaliacoes.count()
        media = todas_avaliacoes.aggregate(avg=models.Avg('nota'))['avg']
        
        # Se não houver avaliações, mantém a nota 5
        if media is None:
            media = 5.0
            
        profile.total_avaliacoes_cache = total
        profile.nota_media_cache = round(media, 2)
        
        profile.save(update_fields=['total_avaliacoes_cache', 'nota_media_cache'])
        
        #print(f"Média atualizada para {prestador_user}: {media}")

    except Exception as e:
        #print(f"Erro ao atualizar média: {e}")
        pass
