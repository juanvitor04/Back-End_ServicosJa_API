# 🗑️ Estratégia de Deleção em Cascata

## Problema Atual

Quando um usuário é deletado, nem todos os dados relacionados são removidos automaticamente, deixando dados órfãos na base.

---

## Análise de Relacionamentos

### ✅ Já com CASCADE (Automático)

```python
# accounts/models.py
class ClienteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ✅ Delete automático
    
class PrestadorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # ✅ Delete automático

# portfolio/models.py
class PortfolioItem(models.Model):
    prestador = models.ForeignKey(PrestadorProfile, on_delete=models.CASCADE)  # ✅ Delete automático
```

### 🔴 Faltando CASCADE (Dados Órfãos)

```python
# contratacoes/models.py
class SolicitacaoContato(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, ...)  # ✅ OK
    prestador = models.ForeignKey(User, on_delete=models.CASCADE, ...)  # ✅ OK
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)  # ✅ OK

# avaliacoes/models.py
class Avaliacao(models.Model):
    solicitacao_contato = models.OneToOneField(
        'contratacoes.SolicitacaoContato',
        on_delete=models.CASCADE  # ✅ OK
    )

# servicos/models.py
class PrestadorServicos(models.Model):
    prestador_profile = models.ForeignKey('accounts.PrestadorProfile', on_delete=models.CASCADE)  # ✅ OK
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)  # ✅ OK

# ⚠️ PROBLEMA: ClienteProfile.favoritos (ManyToMany) pode ter inconsistências
class ClienteProfile(models.Model):
    favoritos = models.ManyToManyField('PrestadorProfile', ...)
    # Quando PrestadorProfile é deletada, a relação M2M é removida automaticamente ✅
```

---

## Fluxo de Deleção Completo

```
DELETE User (cliente)
    ├─ CASCADE → ClienteProfile
    │   ├─ CASCADE → SolicitacaoContato (como cliente)
    │   │   └─ CASCADE → Avaliacao
    │   └─ ManyToMany → Remover de favoritos
    │
DELETE User (prestador)
    ├─ CASCADE → PrestadorProfile
    │   ├─ CASCADE → PortfolioItem
    │   ├─ CASCADE → PrestadorServicos
    │   └─ CASCADE → SolicitacaoContato (como prestador)
    │       └─ CASCADE → Avaliacao
    │
DELETE Servico
    └─ CASCADE → PrestadorServicos
```

---

## Problema: Dados Históricos

**Situação:** Deletar um usuário que tem histórico de contratos?

### Opção 1: Hard Delete (Atual)
```python
# Deleta tudo
User.delete()  # Remove USER + PROFILES + CONTRATOS + AVALIAÇÕES
# ❌ Problema: Perde histórico, auditoria, relatórios
```

### Opção 2: Soft Delete (Recomendado) 🟢
```python
# Marca como deletado, não remove dados
class User(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        # Sempre filtrar deletados
        indexes = [models.Index(fields=['is_deleted'])]

class ClienteProfile(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

class PrestadorProfile(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
```

---

## Implementação Recomendada

### **Passo 1: Adicionar Soft Delete**

```python
# accounts/models.py
from django.utils import timezone

class User(AbstractUser):
    # ... campos existentes ...
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    def delete(self, *args, **kwargs):
        """Soft delete: marca como deletado"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self, *args, **kwargs):
        """Hard delete real (admin only)"""
        super().delete(*args, **kwargs)

class ClienteProfile(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)

class PrestadorProfile(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
```

### **Passo 2: Manager com Filtro Automático**

```python
# accounts/models.py
class ActiveUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class User(AbstractUser):
    objects = ActiveUserManager()  # Default: só usuários ativos
    all_objects = models.Manager()  # Acesso a todos (incluindo deletados)
    
    # ... resto do código ...

# Uso:
User.objects.all()        # Retorna apenas usuários ativos
User.all_objects.all()    # Retorna todos (incluindo deletados)
```

### **Passo 3: Migração**

```python
# accounts/migrations/XXXX_add_soft_delete.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0013_delete_additional_users'),
    ]

    operations = [
        # Adicionar campos soft delete
        migrations.AddField(
            model_name='user',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, editable=False),
        ),
        migrations.AddField(
            model_name='clienteprofile',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='clienteprofile',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, editable=False),
        ),
        migrations.AddField(
            model_name='prestadorprofile',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='prestadorprofile',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, editable=False),
        ),
        
        # Criar índices
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['is_deleted'], name='idx_user_deleted'),
        ),
        migrations.AddIndex(
            model_name='clienteprofile',
            index=models.Index(fields=['is_deleted'], name='idx_cliente_deleted'),
        ),
        migrations.AddIndex(
            model_name='prestadorprofile',
            index=models.Index(fields=['is_deleted'], name='idx_prestador_deleted'),
        ),
    ]
```

### **Passo 4: Signal para Cascata Automática**

```python
# accounts/signals.py
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import User, ClienteProfile, PrestadorProfile
from contratacoes.models import SolicitacaoContato
from portfolio.models import PortfolioItem
from servicos.models import PrestadorServicos

@receiver(pre_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Quando um User é deletado, marca todos os dados relacionados como deletados
    Mantém histórico para auditoria
    """
    now = timezone.now()
    
    # Se é cliente: marca ContratosContato como deletado
    if hasattr(instance, 'perfil_cliente'):
        SolicitacaoContato.objects.filter(cliente=instance).update(
            is_deleted=True,
            deleted_at=now
        )
    
    # Se é prestador: marca dados relacionados como deletados
    if hasattr(instance, 'perfil_prestador'):
        # Delete portfolio
        PortfolioItem.objects.filter(
            prestador=instance.perfil_prestador
        ).update(is_deleted=True, deleted_at=now)
        
        # Delete servicos
        PrestadorServicos.objects.filter(
            prestador_profile=instance.perfil_prestador
        ).update(is_deleted=True, deleted_at=now)
        
        # Delete contratos como prestador
        SolicitacaoContato.objects.filter(prestador=instance).update(
            is_deleted=True,
            deleted_at=now
        )

# Registrar signal
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        import accounts.signals
```

### **Passo 5: Filtrar em Views**

```python
# accounts/views.py
from django.shortcuts import get_object_or_404

class PrestadorListView(generics.ListAPIView):
    def get_queryset(self):
        # Só retorna prestadores não deletados
        return PrestadorProfile.objects.filter(
            is_deleted=False,
            user__is_deleted=False
        ).select_related('user')

class PrestadorDetailView(generics.RetrieveAPIView):
    def get_object(self):
        prestador = get_object_or_404(
            PrestadorProfile,
            pk=self.kwargs['pk'],
            is_deleted=False,  # Não pode acessar deletados
            user__is_deleted=False
        )
        return prestador
```

---

## Comparação: Hard vs Soft Delete

| Aspecto | Hard Delete | Soft Delete |
|--------|------------|-----------|
| **Remoção Física** | Sim | Não |
| **Recuperação** | ❌ Impossível | ✅ Fácil |
| **Auditoria** | ❌ Perdida | ✅ Preservada |
| **Relatórios Históricos** | ❌ Impactados | ✅ Intactos | 
| **Performance** | ✅ Mais rápido | 🟡 Precisa índices |
| **LGPD/GDPR** | ❌ Problema | ✅ Melhor |
| **Complexidade** | Simples | Média |

---

## Checklist de Implementação

- [ ] Adicionar campos `is_deleted` e `deleted_at` em User, ClienteProfile, PrestadorProfile
- [ ] Adicionar campos `is_deleted` em SolicitacaoContato, PortfolioItem, PrestadorServicos
- [ ] Criar ActiveManager para filtrar automaticamente deletados
- [ ] Implementar signal para cascata automática
- [ ] Criar migração
- [ ] Atualizar views para filtrar deletados
- [ ] Adicionar índices em `is_deleted`
- [ ] Adicionar testes
- [ ] Documentar no README

---

## Benefícios

✅ **Histórico Preservado** - Auditoria completa  
✅ **Recuperação Possível** - Admin pode restaurar  
✅ **Conformidade GDPR** - Melhor documentação de deleção  
✅ **Relatórios** - Dados históricos intactos  
✅ **Segurança** - Menos risco de perda acidental  

---

**Recomendação**: Implementar Soft Delete agora, com opção de Hard Delete para admin em casos extremos.
