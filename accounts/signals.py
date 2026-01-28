from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
from avaliacoes.models import Avaliacao
from contratacoes.models import SolicitacaoContato
from .models import PrestadorProfile, User
from portfolio.models import PortfolioItem
from servicos.models import PrestadorServicos


# ============================================================================
# SIGNAL 1: Atualizar cache de avaliação
# ============================================================================

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
        
        if media is None:
            media = 5.0
            
        profile.total_avaliacoes_cache = total
        profile.total_servicos_cache = total  
        profile.nota_media_cache = round(media, 2)
        
        profile.save(update_fields=['total_avaliacoes_cache', 'total_servicos_cache', 'nota_media_cache'])
        
        #print(f"Média atualizada para {prestador_user}: {media}")

    except Exception as e:
        #print(f"Erro ao atualizar média: {e}")
        pass


# ============================================================================
# SIGNAL 2: Cascata de soft delete
# ============================================================================

@receiver(post_save, sender=User)
def soft_delete_user_related_data(sender, instance, **kwargs):
    """
    Quando User é marcado como deletado (is_deleted=True),
    marca dados relacionados como deletados (CASCATA)
    
    Cascata:
    - User → ClienteProfile ou PrestadorProfile (soft delete)
    - ClienteProfile → SolicitacaoContato (como cliente)
    - PrestadorProfile → PortfolioItem, PrestadorServicos
    - PrestadorProfile → SolicitacaoContato (como prestador)
    
    Args:
        sender: Classe User
        instance: Instância do usuário
    """
    # Só executar se o user foi marcado como deletado
    if not instance.is_deleted:
        return
    
    now = timezone.now()
    
    # Marcar ClienteProfile como deletado
    if hasattr(instance, 'perfil_cliente') and instance.perfil_cliente:
        print(f"📝 Marcando ClienteProfile {instance.email} como deletado...")
        instance.perfil_cliente.is_deleted = True
        instance.perfil_cliente.deleted_at = now
        instance.perfil_cliente.save(update_fields=['is_deleted', 'deleted_at'])
        
        # Marcar contratos como cliente como deletados
        print("  └─ Solicitações contato (como cliente)...")
        SolicitacaoContato.all_objects.filter(cliente=instance, is_deleted=False).update(
            is_deleted=True,
            deleted_at=now
        )
    
    # Marcar PrestadorProfile como deletado
    if hasattr(instance, 'perfil_prestador') and instance.perfil_prestador:
        prestador = instance.perfil_prestador
        print(f"📝 Marcando PrestadorProfile {instance.email} como deletado...")
        prestador.is_deleted = True
        prestador.deleted_at = now
        prestador.save(update_fields=['is_deleted', 'deleted_at'])
        
        # Marcar portfolio como deletado
        print("  ├─ Portfolio items...")
        PortfolioItem.all_objects.filter(
            prestador=prestador,
            is_deleted=False
        ).update(
            is_deleted=True,
            deleted_at=now
        )
        
        # Marcar serviços como deletados
        print("  ├─ Prestador serviços...")
        PrestadorServicos.all_objects.filter(
            prestador_profile=prestador,
            is_deleted=False
        ).update(
            is_deleted=True,
            deleted_at=now
        )
        
        # Marcar contratos como prestador como deletados
        print("  └─ Solicitações contato (como prestador)...")
        SolicitacaoContato.all_objects.filter(
            prestador=instance,
            is_deleted=False
        ).update(
            is_deleted=True,
            deleted_at=now
        )
    
    print(f"✅ User {instance.email} soft-deleted. Todos os dados relacionados marcados como deletados.")
