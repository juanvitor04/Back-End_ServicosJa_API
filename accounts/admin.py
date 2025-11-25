from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ClienteProfile, PrestadorProfile, pegar_dados_endereco

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Atualizado para usar nome_completo
    list_display = ('email', 'nome_completo', 'tipo_usuario', 'cpf', 'genero', 'idade', 'is_active')

    def get_idade(self, obj):
        return obj.idade
    get_idade.short_description = 'Idade'

    list_filter = ('is_active', 'date_joined', 'tipo_usuario') 
    search_fields = ('email', 'nome_completo', 'cpf')
    ordering = ('email',) # Ordena por email já que username não é o foco
    
    # Atualiza o formulário de edição do Admin
    fieldsets = UserAdmin.fieldsets
    if fieldsets:
        fieldsets = list(fieldsets)
        # Substitui bloco de nomes
        fieldsets[1] = ('Informações Pessoais', {'fields': ('nome_completo', 'email', 'dt_nascimento', 'genero', 'cpf')})
        fieldsets = tuple(fieldsets)


@admin.register(ClienteProfile)
class ClienteProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone_contato', 'cidade', 'bairro', 'latitude', 'longitude')
    search_fields = ('user__email', 'cep', 'cidade')
    readonly_fields = ('cidade', 'bairro', 'estado', 'latitude', 'longitude', 'created_at', 'updated_at')

@admin.register(PrestadorProfile)
class PrestadorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone_publico', 'cidade', 'bairro', 'nota_media_cache', 'latitude')
    search_fields = ('user__email', 'cep', 'cidade')
    filter_horizontal = ('servicos',)
    
    readonly_fields = (
        'cidade', 'bairro', 'estado', # Campos automáticos são readonly
        'latitude', 'longitude',
        'nota_media_cache',
        'total_avaliacoes_cache',
        'acessos_perfil',
        'total_servicos_cache',
        'created_at',
        'updated_at',
    )
    
    # Forçar salvar a latitude e longitude ao editar pelo Admin
    def save_model(self, request, obj, form, change):
        # Se for uma edição e tiver cep, tenta recalcular se faltar dados
        if obj.cep and (not obj.latitude or not obj.cidade):
            dados = pegar_dados_endereco(obj.cep, obj.rua, obj.numero_casa)
            if dados:
                obj.latitude = dados['latitude']
                obj.longitude = dados['longitude']
                obj.cidade = dados['cidade']
                obj.bairro = dados['bairro']
                obj.estado = dados['estado']
        
        super().save_model(request, obj, form, change)
