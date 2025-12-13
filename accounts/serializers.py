from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import ClienteProfile, PrestadorProfile
from .validators import validar_cpf, validar_telefone, validar_cep, validar_data_nascimento
from servicos.models import Servico, CategoriaServico
from servicos.serializers import ServicoSerializer
from portfolio.serializers import PortfolioItemSerializer
from avaliacoes.models import Avaliacao

User = get_user_model() 

class ClienteRegistrationSerializer(serializers.ModelSerializer):
    dt_nascimento = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    telefone_contato = serializers.CharField(write_only=True, validators=[validar_telefone], required=True)
    cep = serializers.CharField(write_only=True, validators=[validar_cep], required=True)
    cpf = serializers.CharField(required=True)
    rua = serializers.CharField(write_only=True, required=True)
    numero_casa = serializers.CharField(write_only=True, required=True)
    
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 
            'nome_completo',
            'dt_nascimento',
            'genero',
            'cpf',
            'password', 
            'password2',
            'telefone_contato', 
            'cep', 
            'rua', 
            'numero_casa', 
            'tipo_usuario',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'dt_nascimento': {'required': True},
            'genero': {'required': True},
            'tipo_usuario': {'read_only': True},
        }

    def validate_dt_nascimento(self, value):
        return validar_data_nascimento(value)

    def validate_cpf(self, value):
        cleaned_cpf = validar_cpf(value)
        return cleaned_cpf

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "As senhas precisam ser iguais."})
        return data

    @transaction.atomic
    def create(self, validated_data):
        profile_data = {
            'telefone_contato': validated_data.get('telefone_contato'),
            'cep': validated_data.get('cep'),
            'rua': validated_data.get('rua'),
            'numero_casa': validated_data.get('numero_casa'),
        }

        validated_data.pop('password2', None)
        validated_data.pop('telefone_contato', None)
        validated_data.pop('cep', None)
        validated_data.pop('rua', None)
        validated_data.pop('numero_casa', None)

        user_data = validated_data

        user = User.objects.create_user(
            username=user_data['email'], 
            tipo_usuario='cliente',
            **user_data 
        )
        
        profile = ClienteProfile(user=user, **profile_data)
        profile.save() 

        return user

class PrestadorRegistrationSerializer(serializers.ModelSerializer):
    dt_nascimento = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    telefone_publico = serializers.CharField(write_only=True, validators=[validar_telefone], required=True)
    cep = serializers.CharField(write_only=True, validators=[validar_cep], required=True)
    cpf = serializers.CharField(required=True)
    rua = serializers.CharField(write_only=True, required=True)
    numero_casa = serializers.CharField(write_only=True, required=True)
    
    disponibilidade = serializers.BooleanField(write_only=True) 
    possui_material_proprio = serializers.BooleanField(default=False, write_only=True)
    atende_fim_de_semana = serializers.BooleanField(default=False, write_only=True)

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaServico.objects.all(),
        write_only=True,
        required=True
    )

    servico = serializers.PrimaryKeyRelatedField(
        queryset = Servico.objects.all(),
        write_only=True,
        required=True
    )

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 
            'nome_completo',
            'dt_nascimento',
            'genero',
            'cpf',
            'password', 
            'password2',
            'telefone_publico', 
            'cep', 
            'rua', 
            'numero_casa', 
            'disponibilidade',
            'possui_material_proprio',
            'atende_fim_de_semana',
            'categoria',
            'servico',
            'tipo_usuario',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'dt_nascimento': {'required': True},
            'genero': {'required': True},
            'tipo_usuario': {'read_only': True},
        }

    def validate_dt_nascimento(self, value):
        return validar_data_nascimento(value)

    def validate_cpf(self, value):
        cleaned_cpf = validar_cpf(value)
        return cleaned_cpf

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "As senhas não coincidem."})
        
        categoria = data.get('categoria')
        servico = data.get('servico')
        
        if servico and servico.categoria != categoria:
            raise serializers.ValidationError({"servico": f"O serviço '{servico.nome}' não pertence à categoria '{categoria.nome}'."})
        
        return data

    @transaction.atomic
    def create(self, validated_data):
        profile_data = {
            'telefone_publico': validated_data.get('telefone_publico'),
            'cep': validated_data.get('cep'),                     
            'rua': validated_data.get('rua'),                        
            'numero_casa': validated_data.get('numero_casa'),       
            'disponibilidade': validated_data.get('disponibilidade', False),
            'possui_material_proprio': validated_data.get('possui_material_proprio', False),
            'atende_fim_de_semana': validated_data.get('atende_fim_de_semana', False),
        }
        
        servico_data = validated_data.get('servico')

        validated_data.pop('password2', None)
        validated_data.pop('servico', None)
        validated_data.pop('categoria', None)

        for key in profile_data:
            validated_data.pop(key, None)
        
        user_data = validated_data

     
        user = User.objects.create_user(
            username=user_data['email'],
            tipo_usuario='prestador',
            **user_data
        )

        profile = PrestadorProfile(user=user, **profile_data)
        if servico_data:
            profile.servico = servico_data
        profile.save()
            
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        data['nome'] = self.user.nome_completo
        data['email'] = self.user.email
        data['tipo_usuario'] = self.user.tipo_usuario

        if self.user.tipo_usuario == 'cliente':
            try:
                data['profile_id'] = self.user.perfil_cliente.id
            except ClienteProfile.DoesNotExist:
                data['profile_id'] = None
        elif self.user.tipo_usuario == 'prestador':
            try:
                data['profile_id'] = self.user.perfil_prestador.id
            except PrestadorProfile.DoesNotExist:
                data['profile_id'] = None
        
        return data

class AvaliacaoSimplesSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='solicitacao_contato.cliente.nome_completo', read_only=True)
    data = serializers.DateTimeField(source='data_criacao', format="%d/%m/%Y", read_only=True)
    
    class Meta:
        model = Avaliacao
        fields = ['cliente_nome', 'nota', 'comentario', 'data']

class PrestadorPublicoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    nome = serializers.CharField(source='user.nome_completo', read_only=True)
    
    servico = ServicoSerializer(read_only=True)
    categoria = serializers.CharField(source='servico.categoria.nome', read_only=True)
    foto = serializers.ImageField(source='foto_perfil', read_only=True)

    portfolio = PortfolioItemSerializer(source='portfolioitem_set', many=True, read_only=True)
    nota_media = serializers.DecimalField(source='nota_media_cache', max_digits=3, decimal_places=1, read_only=True)
    total_avaliacoes = serializers.IntegerField(source='total_avaliacoes_cache', read_only=True)
    estatisticas = serializers.SerializerMethodField()
    ultimas_avaliacoes = serializers.SerializerMethodField()

    class Meta:
        model = PrestadorProfile
        fields = [
            'id',
            'user_id', 
            'nome', 
            'foto',
            'biografia',
            'telefone_publico',
            'cidade', 'bairro', 'estado',
            'latitude', 'longitude',
            'servico',
            'categoria',
            'portfolio',
            'nota_media',
            'total_avaliacoes',
            'estatisticas',
            'ultimas_avaliacoes',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        if not (request and request.user.is_authenticated and request.user.tipo_usuario == 'cliente'):
             data.pop('telefone_publico', None)
             
        return data

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_estatisticas(self, obj):
        queryset = Avaliacao.objects.filter(solicitacao_contato__prestador=obj.user)
        
        counts = queryset.values('nota').annotate(count=Count('nota')).order_by('nota')
        
        # Inicializa contadores
        distribuicao = {i: 0 for i in range(1, 6)}
        total = obj.total_avaliacoes_cache # Usando cache para performance
        
        for item in counts:
            distribuicao[item['nota']] = item['count']
            
        # Calcula porcentagens
        stats_distribuicao = {}
        for nota, count in distribuicao.items():
            stats_distribuicao[f"estrelas_{nota}"] = {
                "quantidade": count,
                "porcentagem": round((count / total * 100), 2) if total > 0 else 0
            }
            
        return {
            "distribuicao": stats_distribuicao
        }

    @extend_schema_field(AvaliacaoSimplesSerializer(many=True))
    def get_ultimas_avaliacoes(self, obj):
        avaliacoes = Avaliacao.objects.filter(
            solicitacao_contato__prestador=obj.user
        ).order_by('-data_criacao')[:5]
        
        return AvaliacaoSimplesSerializer(avaliacoes, many=True).data

class PrestadorListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    nome = serializers.CharField(source='user.nome_completo', read_only=True)
    
    servico = ServicoSerializer(read_only=True)
    categoria = serializers.CharField(source='servico.categoria.nome', read_only=True)
    foto = serializers.ImageField(source='foto_perfil', read_only=True)

    portfolio = PortfolioItemSerializer(source='portfolioitem_set', many=True, read_only=True)

    nota_media = serializers.DecimalField(source='nota_media_cache', max_digits=3, decimal_places=1, read_only=True)
    total_avaliacoes = serializers.IntegerField(source='total_avaliacoes_cache', read_only=True)
    
    distancia = serializers.FloatField(read_only=True)
    class Meta:
        model = PrestadorProfile
        fields = [
            'id',
            'user_id', 
            'nome', 
            'foto',
            'biografia',
            'telefone_publico',
            'cidade', 'bairro', 'estado',
            'servico',
            'categoria',
            'portfolio',
            'nota_media',
            'total_avaliacoes',
            'distancia',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if not (request and request.user.is_authenticated and request.user.tipo_usuario == 'cliente'):
             data.pop('telefone_publico', None)
             
        return data

class PrestadorProfileEditSerializer(serializers.ModelSerializer):
    foto_perfil = serializers.ImageField(required=False)
    biografia = serializers.CharField(required=False)
    
    class Meta:
        model = PrestadorProfile
        fields = ['foto_perfil', 'biografia']

class ClienteProfileEditSerializer(serializers.ModelSerializer):
    foto_perfil = serializers.ImageField(required=False)
    telefone_contato = serializers.CharField(validators=[validar_telefone], required=True)
    cep = serializers.CharField(validators=[validar_cep], required=True)
    
    class Meta:
        model = ClienteProfile
        fields = ['foto_perfil', 'telefone_contato', 'cep', 'rua', 'numero_casa', 'complemento', 'cidade', 'bairro', 'estado']
        read_only_fields = ['latitude', 'longitude']

class ClienteProfileSerializer(serializers.ModelSerializer):
    foto_perfil = serializers.ImageField(required=False)
    data_registro = serializers.DateTimeField(source='created_at', format="%d/%m/%Y", read_only=True)
    telefone_contato = serializers.CharField(validators=[validar_telefone], required=True)
    cep = serializers.CharField(validators=[validar_cep], required=True)

    class Meta:
        model = ClienteProfile
        fields = ['telefone_contato', 'cep', 'rua', 'numero_casa', 'complemento', 'cidade', 'bairro', 'estado', 'latitude', 'longitude', 'foto_perfil', 'data_registro']
        read_only_fields = [
            'latitude', 
            'longitude'
        ]

class PrestadorProfileSerializer(serializers.ModelSerializer):
    servico = serializers.PrimaryKeyRelatedField(queryset=Servico.objects.all(), required=False)
    categoria = serializers.IntegerField(source='servico.categoria.id', read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaServico.objects.all(),
        write_only=True, 
        required=False
    )
    telefone_publico = serializers.CharField(validators=[validar_telefone], required=True)
    cep = serializers.CharField(validators=[validar_cep], required=True)
    data_registro = serializers.DateTimeField(source='created_at', format="%d/%m/%Y", read_only=True)

    class Meta:
        model = PrestadorProfile
        fields = [
            'biografia', 'telefone_publico', 'cep', 'rua', 'numero_casa', 'complemento', 
            'cidade', 'bairro', 'estado', 'latitude', 'longitude', 
            'disponibilidade', 'possui_material_proprio', 'atende_fim_de_semana', 
            'foto_perfil', 'servico', 'categoria', 'categoria_id', 'data_registro'
        ]
        read_only_fields = [
            'latitude',
            'longitude',
        ]

    def validate(self, data):
        servico = data.get('servico')
        categoria = data.get('categoria_id')

        if servico and categoria:
            if servico.categoria != categoria:
                raise serializers.ValidationError({"servico": f"O serviço '{servico.nome}' não pertence à categoria '{categoria.nome}'."})
            
        return data
    


class UserProfileSerializer(serializers.ModelSerializer):
    #Serializer para o endpoint /me/. Permite ver e editar dados do usuário e do seu perfil específico.

    dt_nascimento = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"], required=False)
    
    # Campos aninhados para edição
    perfil_cliente = ClienteProfileSerializer(required=False)
    perfil_prestador = PrestadorProfileSerializer(required=False)
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'email', 'nome_completo', 'dt_nascimento', 'genero', 'cpf', 'tipo_usuario',
            'perfil_cliente', 'perfil_prestador'
        ]
        read_only_fields = ['id', 'email', 'cpf', 'tipo_usuario']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.tipo_usuario == 'cliente':
            ret.pop('perfil_prestador', None)
        elif instance.tipo_usuario == 'prestador':
            ret.pop('perfil_cliente', None)
        return ret

    def update(self, instance, validated_data):
        instance.nome_completo = validated_data.get('nome_completo', instance.nome_completo)
        instance.dt_nascimento = validated_data.get('dt_nascimento', instance.dt_nascimento)
        instance.genero = validated_data.get('genero', instance.genero)
        instance.save()

        if instance.tipo_usuario == 'cliente':
            profile_data = validated_data.get('perfil_cliente')
            if profile_data:
                profile = instance.perfil_cliente
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()
        
        elif instance.tipo_usuario == 'prestador':
            profile_data = validated_data.get('perfil_prestador')
            if profile_data:
                profile = instance.perfil_prestador
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()

        return instance

class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer simples para listagem de usuários.
    """
    class Meta:
        model = User
        fields = ['id', 'nome_completo', 'email', 'tipo_usuario']
