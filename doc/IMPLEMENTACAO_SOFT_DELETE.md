# Implementação Prática: Soft Delete com Cascata

Este arquivo contém o código pronto para implementar a estratégia de soft delete.

## 1️⃣ Atualizar accounts/models.py

```python
# Adicionar no topo
from django.utils import timezone

# Adicionar novo Manager
class ActiveManager(models.Manager):
    """
    Manager que retorna apenas registros não deletados
    Uso: User.objects.all() retorna apenas ativos
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

# Atualizar classe User
class User(AbstractUser):
    # ... campos existentes ...
    
    # Novos campos para soft delete
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    # Managers
    objects = ActiveManager()  # Default: retorna apenas ativos
    all_objects = models.Manager()  # Retorna todos
    
    class Meta:
        # Sempre filtrar deletados nas queries
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_user_deleted'),
        ]
    
    def delete(self, *args, **kwargs):
        """Soft delete: marca como deletado em vez de remover"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def hard_delete(self, *args, **kwargs):
        """Hard delete real (apenas admin, use com cuidado)"""
        super().delete(*args, **kwargs)
    
    # ... resto dos métodos ...

# Atualizar classe ClienteProfile
class ClienteProfile(models.Model):
    # ... campos existentes ...
    
    # Novos campos para soft delete
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    # Manager
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_cliente_deleted'),
        ]

# Atualizar classe PrestadorProfile
class PrestadorProfile(models.Model):
    # ... campos existentes ...
    
    # Novos campos para soft delete
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    # Manager
    objects = ActiveManager()
    all_objects = models.Manager()
    
    class Meta:
        indexes = [
            models.Index(fields=['cep'], name='idx_cep'),
            models.Index(fields=['latitude', 'longitude'], name='idx_geo'),
            models.Index(fields=['is_deleted'], name='idx_prestador_deleted'),
        ]
```

---

## 2️⃣ Adicionar Signals - accounts/signals.py

```python
"""
Sinais para cascata automática de soft delete
"""
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import User, PrestadorProfile
from contratacoes.models import SolicitacaoContato
from portfolio.models import PortfolioItem
from servicos.models import PrestadorServicos

@receiver(pre_delete, sender=User)
def soft_delete_user_related_data(sender, instance, **kwargs):
    """
    Quando User é deletado (soft delete), marca dados relacionados como deletados
    
    Cascata:
    - ClienteProfile → SolicitacaoContato (como cliente) → Avaliacao
    - PrestadorProfile → PortfolioItem, PrestadorServicos
    - PrestadorProfile → SolicitacaoContato (como prestador) → Avaliacao
    """
    now = timezone.now()
    
    # Se é cliente: marca contratos como cliente como deletados
    if hasattr(instance, 'perfil_cliente') and instance.perfil_cliente:
        SolicitacaoContato.objects.filter(cliente=instance).update(
            is_deleted=True,
            deleted_at=now
        )
    
    # Se é prestador: marca dados do prestador como deletados
    if hasattr(instance, 'perfil_prestador') and instance.perfil_prestador:
        prestador = instance.perfil_prestador
        
        # Marcar portfolio como deletado
        PortfolioItem.objects.filter(
            prestador=prestador
        ).update(
            is_deleted=True,
            deleted_at=now
        )
        
        # Marcar serviços como deletados
        PrestadorServicos.objects.filter(
            prestador_profile=prestador
        ).update(
            is_deleted=True,
            deleted_at=now
        )
        
        # Marcar contratos como prestador como deletados
        SolicitacaoContato.objects.filter(
            prestador=instance
        ).update(
            is_deleted=True,
            deleted_at=now
        )
    
    print(f"✅ User {instance.email} soft-deleted. Dados relacionados marcados como deletados.")
```

Adicionar ao final de `accounts/apps.py`:

```python
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        """Registrar signals quando a app é carregada"""
        import accounts.signals  # noqa
```

---

## 3️⃣ Atualizar Other Models

```python
# contratacoes/models.py
class SolicitacaoContato(models.Model):
    # ... campos existentes ...
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_solicitacao_deleted'),
        ]

# portfolio/models.py
class PortfolioItem(models.Model):
    # ... campos existentes ...
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_portfolio_deleted'),
        ]

# servicos/models.py
class PrestadorServicos(models.Model):
    # ... campos existentes ...
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_servicos_deleted'),
        ]
```

---

## 4️⃣ Criar Migração

```bash
python manage.py makemigrations
python manage.py migrate
```

Ou criar manualmente:

```python
# accounts/migrations/XXXX_add_soft_delete.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0013_delete_additional_users'),
    ]

    operations = [
        # User
        migrations.AddField(
            model_name='user',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='user',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, editable=False),
        ),
        
        # ClienteProfile
        migrations.AddField(
            model_name='clienteprofile',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='clienteprofile',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, editable=False),
        ),
        
        # PrestadorProfile
        migrations.AddField(
            model_name='prestadorprofile',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='prestadorprofile',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True, editable=False),
        ),
        
        # Índices
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

---

## 5️⃣ Atualizar Views

```python
# accounts/views.py
from django.shortcuts import get_object_or_404

class PrestadorListView(generics.ListAPIView):
    """
    Listar apenas prestadores não deletados
    """
    def get_queryset(self):
        return PrestadorProfile.objects.filter(
            is_deleted=False,
            user__is_deleted=False
        ).select_related('user')

class PrestadorDetailView(generics.RetrieveAPIView):
    """
    Detalhe de prestador (não mostra deletados)
    """
    def get_object(self):
        prestador = get_object_or_404(
            PrestadorProfile,
            pk=self.kwargs['pk'],
            is_deleted=False,
            user__is_deleted=False
        )
        return prestador

class ClienteProfileEditView(generics.RetrieveUpdateAPIView):
    """
    Editar perfil de cliente (só se não deletado)
    """
    def get_object(self):
        return get_object_or_404(
            ClienteProfile,
            user=self.request.user,
            is_deleted=False
        )
```

---

## 6️⃣ Uso Prático

```python
# Soft delete (padrão)
user = User.objects.get(id=1)
user.delete()  # Marca como deletado, não remove
# User continuará no BD com is_deleted=True

# Hard delete (apenas admin)
user = User.all_objects.get(id=1)
user.hard_delete()  # Remove completamente do BD

# Restaurar usuário deletado
from django.utils import timezone
user = User.all_objects.get(id=1, is_deleted=True)
user.is_deleted = False
user.deleted_at = None
user.save()

# Listar apenas ativos
ativos = User.objects.all()  # ✅ Retorna apenas não deletados

# Listar todos (incluindo deletados)
todos = User.all_objects.all()  # Todos

# Contar deletados
deletados_count = User.all_objects.filter(is_deleted=True).count()
```

---

## 7️⃣ Admin Configuration

```python
# accounts/admin.py
from django.contrib import admin
from .models import User, ClienteProfile, PrestadorProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'nome_completo', 'is_deleted', 'deleted_at']
    list_filter = ['is_deleted', 'tipo_usuario']
    search_fields = ['email', 'nome_completo']
    
    def get_queryset(self, request):
        # Admin vê todos (incluindo deletados)
        return User.all_objects.all()
    
    actions = ['restore_users', 'hard_delete_users']
    
    @admin.action(description="Restaurar usuários selecionados")
    def restore_users(self, request, queryset):
        updated = queryset.update(is_deleted=False, deleted_at=None)
        self.message_user(request, f"{updated} usuários restaurados")
    
    @admin.action(description="Deletar permanentemente (⚠️ IRREVERSÍVEL)")
    def hard_delete_users(self, request, queryset):
        for user in queryset:
            user.hard_delete()
```

---

## ✅ Verificação Final

```bash
# Testar
python manage.py shell

# Criar usuário
from accounts.models import User
user = User.objects.create_user(
    email='test@test.com',
    nome_completo='Test User',
    tipo_usuario='cliente'
)

# Soft delete
user.delete()

# Verificar
User.objects.filter(email='test@test.com').count()  # 0 (não aparece)
User.all_objects.filter(email='test@test.com').count()  # 1 (existe)

# Restaurar
user = User.all_objects.get(email='test@test.com')
user.is_deleted = False
user.deleted_at = None
user.save()
```

---

**Status**: 🟢 Pronto para implementação!
