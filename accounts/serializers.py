from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import ClienteProfile, PrestadorProfile
from servicos.models import Servico
from servicos.serializers import ServicoSerializer
from portfolio.serializers import PortfolioItemSerializer
from avaliacoes.models import Avaliacao

User = get_user_model() 

class ClienteRegistrationSerializer(serializers.ModelSerializer):
    telefone_contato = serializers.CharField(write_only=True)
    cep = serializers.CharField(write_only=True)
    rua = serializers.CharField(write_only=True)
    numero_casa = serializers.CharField(write_only=True)
    complemento = serializers.CharField(allow_blank=True, required=False, write_only=True)
    
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
            'complemento',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("As senhas precisam ser iguais.")
        return data

    @transaction.atomic
    def create(self, validated_data):
        profile_data = {
            'telefone_contato': validated_data.get('telefone_contato'),
            'cep': validated_data.get('cep'),
            'rua': validated_data.get('rua'),
            'numero_casa': validated_data.get('numero_casa'),
            'complemento': validated_data.get('complemento', '')
        }

        validated_data.pop('password2', None)
        validated_data.pop('telefone_contato', None)
        validated_data.pop('cep', None)
        validated_data.pop('rua', None)
        validated_data.pop('numero_casa', None)
        validated_data.pop('complemento', None)

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
    telefone_publico = serializers.CharField(write_only=True)
    cep = serializers.CharField(write_only=True)
    rua = serializers.CharField(write_only=True)
    numero_casa = serializers.CharField(write_only=True)
    
    disponibilidade = serializers.BooleanField(default=False, write_only=True) 
    possui_material_proprio = serializers.BooleanField(default=False, write_only=True)
    atende_fim_de_semana = serializers.BooleanField(default=False, write_only=True)

    servicos = serializers.PrimaryKeyRelatedField(
        queryset = Servico.objects.all(),
        many=True,
        allow_empty=False,
        write_only=True
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
            'servicos',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("As senhas não coincidem.")
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
        
        servicos_data = validated_data.get('servicos', [])

        validated_data.pop('password2', None)
        validated_data.pop('servicos', None)

        for key in profile_data:
            validated_data.pop(key, None)
        
        user_data = validated_data

     
        user = User.objects.create_user(
            username=user_data['email'],
            tipo_usuario='prestador',
            **user_data
        )

        profile = PrestadorProfile(user=user, **profile_data)
        profile.save()

        if servicos_data:
            profile.servicos.set(servicos_data)
            
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
    email = serializers.EmailField(source='user.email', read_only=True)
    
    servicos = ServicoSerializer(many=True, read_only=True)
    foto = serializers.ImageField(source='foto_perfil', read_only=True)
    distancia = serializers.FloatField(read_only=True, required=False)

    localizacao = serializers.SerializerMethodField()

    portfolio = PortfolioItemSerializer(source='portfolioitem_set', many=True, read_only=True)
    nota_media = serializers.DecimalField(source='nota_media_cache', max_digits=3, decimal_places=1, read_only=True)
    total_avaliacoes = serializers.IntegerField(source='total_avaliacoes_cache', read_only=True)
    ultimas_avaliacoes = serializers.SerializerMethodField()

    class Meta:
        model = PrestadorProfile
        fields = [
            'id',
            'user_id', 
            'nome', 
            'email',
            'foto',
            'localizacao',
            'biografia',
            'telefone_publico',
            'disponibilidade',
            'possui_material_proprio',
            'atende_fim_de_semana',
            'latitude',
            'longitude',
            'cidade', 'bairro', 'estado', 
            'servicos',
            'distancia',
            'portfolio',
            'nota_media',
            'total_avaliacoes',
            'ultimas_avaliacoes'
        ]

    def get_localizacao(self, obj):
        partes = []
        if obj.cidade: partes.append(obj.cidade)
        if obj.bairro: partes.append(obj.bairro)
        if obj.estado: partes.append(obj.estado)
        return ", ".join(partes) if partes else "Localização não informada"

    def get_ultimas_avaliacoes(self, obj):
        avaliacoes = Avaliacao.objects.filter(
            solicitacao_contato__prestador=obj.user
        ).order_by('-data_criacao')[:5]
        
        return AvaliacaoSimplesSerializer(avaliacoes, many=True).data

class PrestadorProfileEditSerializer(serializers.ModelSerializer):
    #Trocar depois para imageField para referenciar uma imagem.
    foto_perfil = serializers.CharField(required=False)
    biografia = serializers.CharField(required=False)
    
    class Meta:
        model = PrestadorProfile
        fields = ['foto_perfil', 'biografia']
