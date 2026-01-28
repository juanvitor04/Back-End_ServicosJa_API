import requests
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from datetime import date
from django.forms import ValidationError
from django.core.exceptions import ValidationError as ModelValidationError
from geopy.geocoders import Nominatim
from time import sleep
from decimal import Decimal
from django.utils import timezone


def _sanitize_telefone(phone):
    if not phone:
        return ""
    return ''.join(filter(str.isdigit, str(phone)))


class ActiveManager(models.Manager):
    """
    Manager que retorna apenas registros não deletados.
    Uso padrão: Model.objects.all() retorna apenas ativos
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


def pegar_dados_endereco(cep: str | int, rua: str, numero: str | int) -> dict:    
    cep_str = str(cep)
    cep_limpo = ''.join(filter(str.isdigit, cep_str))
    
    if len(cep_limpo) != 8:
        return None

    def to_decimal(val):
        if val is None: return None
        return Decimal(f"{float(val):.8f}")

    dados = {
        'latitude': None, 
        'longitude': None,
        'cidade': '', 
        'bairro': '', 
        'estado': ''
    }
    try:
        print("Tentando BrasilAPI...")
        response = requests.get(f'https://brasilapi.com.br/api/cep/v2/{cep_limpo}', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            dados['cidade'] = data.get('city', '')
            dados['bairro'] = data.get('neighborhood', '')
            dados['estado'] = data.get('state', '')
            
            loc = data.get('location', {})
            coords = loc.get('coordinates', {})
            
            if isinstance(coords, dict):
                dados['latitude'] = to_decimal(coords.get('latitude'))
                dados['longitude'] = to_decimal(coords.get('longitude'))
            elif isinstance(coords, (list, tuple)) and len(coords) >= 2:
                dados['longitude'] = to_decimal(coords[0])
                dados['latitude'] = to_decimal(coords[1])
            
            if dados['latitude'] is not None and dados['longitude'] is not None:
                print(f"BrasilAPI deu certo: {dados['cidade']} - {dados['bairro']}")
                return dados
            else:
                 print("BrasilAPI retornou endereço sem coordenadas.")
            
    except Exception as e:
        print(f"BrasilAPI falhou: {e}")

    print("Iniciando Fallback (ViaCEP + Nominatim)...")
    try:
        viacep = requests.get(f'https://viacep.com.br/ws/{cep_limpo}/json/', timeout=5).json()
        if not "erro" in viacep:
            dados['cidade'] = viacep.get('localidade', '')
            dados['bairro'] = viacep.get('bairro', '')
            dados['estado'] = viacep.get('uf', '')
            nome_rua = rua if rua else viacep.get('logradouro', '')

            geolocator = Nominatim(user_agent="ServicoJa_App_Final/1.0", timeout=10)
            
            queries = [
                f"{nome_rua}, {numero}, {dados['cidade']} - {dados['estado']}, Brasil",
                f"{nome_rua}, {dados['cidade']} - {dados['estado']}, Brasil",
                f"{dados['cidade']} - {dados['estado']}, Brasil"
            ]

            for i, query in enumerate(queries):
                try:
                    if i > 0: sleep(1)
                    print(f"Tentativa Nominatim {i+1}: {query}")
                    loc = geolocator.geocode(query)
                    if loc:
                        dados['latitude'] = to_decimal(loc.latitude)
                        dados['longitude'] = to_decimal(loc.longitude)
                        print(f"Nominatim deu certo: {dados['latitude']}, {dados['longitude']}")
                        break
                except Exception as e:
                    print(f"Erro Nominatim {i+1}: {e}")
                
            return dados
    except Exception:
        pass

    return None


class User(AbstractUser):
    TIPO_USUARIO_ESCOLHA = [
        ('cliente', 'Cliente'),
        ('prestador', 'Prestador de Serviço'),
    ]
    ESCOLHA_GENERO = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('T', 'Trans'),
        ('N', 'Não binário'),
        ('O', 'Outro'),
        ('P', 'Prefiro não informar'),
    ]

    first_name = None
    last_name = None
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_ESCOLHA, null=True, blank=True)
    email = models.EmailField(unique=True)
    dt_nascimento = models.DateField(null=True)
    genero = models.CharField(max_length=1, choices=ESCOLHA_GENERO, null=True)
    cpf = models.CharField(max_length=11, null=True, help_text='CPF sem pontuação')
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome_completo']

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_user_deleted'),
        ]

    @property
    def idade(self) -> int:
        if not self.dt_nascimento:
            return 0
        hoje = date.today()
        return hoje.year - self.dt_nascimento.year - ((hoje.month, hoje.day) < (self.dt_nascimento.month, self.dt_nascimento.day))

    def delete(self, *args, **kwargs):
        """Soft delete: marca como deletado em vez de remover"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def hard_delete(self, *args, **kwargs):
        """Hard delete real (apenas admin, use com cuidado)"""
        super().delete(*args, **kwargs)

    def clean(self):
        if self.tipo_usuario == 'cliente' and hasattr(self, 'perfil_prestador'):
            raise ValidationError("Este usuário já é prestador.")
        if self.tipo_usuario == 'prestador' and hasattr(self, 'perfil_cliente'):
            raise ValidationError("Este usuário já é cliente.")
    
    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
    
    def get_full_name(self):
        return self.nome_completo

    def get_short_name(self):
        return self.nome_completo.split(' ')[0] if self.nome_completo else self.email


class ClienteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    telefone_contato = models.CharField(max_length=11, null=True)
    cep = models.CharField(max_length=9)
    rua = models.CharField(max_length=150)
    numero_casa = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    favoritos = models.ManyToManyField('PrestadorProfile', related_name='favoritado_por', blank=True)
    foto_perfil = models.ImageField(upload_to='perfil_clientes/', null=True, blank=True)
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['is_deleted'], name='idx_cliente_deleted'),
        ]

    def save(self, *args, **kwargs):
        run_geocode = False
        if self.pk:
            try:
                antigo = ClienteProfile.objects.get(pk=self.pk)
                if antigo.cep != self.cep or antigo.rua != self.rua or antigo.numero_casa != self.numero_casa:
                    run_geocode = True
                if not self.latitude or not self.cidade:
                    run_geocode = True
            except ClienteProfile.DoesNotExist:
                run_geocode = True
        else:
            run_geocode = True

        if run_geocode and self.cep:
            dados = pegar_dados_endereco(self.cep, self.rua, self.numero_casa)
            if dados:
                self.latitude = dados['latitude']
                self.longitude = dados['longitude']
                self.cidade = dados['cidade']
                self.bairro = dados['bairro']
                self.estado = dados['estado']
            
        if self.telefone_contato:
            self.telefone_contato = _sanitize_telefone(self.telefone_contato)

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.email} (Cliente)"


class PrestadorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_prestador')
    biografia = models.TextField(blank=True)
    telefone_publico = models.CharField(max_length=11, null=True)
    cep = models.CharField(max_length=8)
    rua = models.CharField(max_length=150)
    numero_casa = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    disponibilidade = models.BooleanField(default=False, help_text='Disponibilidade de horário 24 horas?')
    possui_material_proprio = models.BooleanField(default=False)
    atende_fim_de_semana = models.BooleanField(default=False)
    foto_perfil = models.ImageField(upload_to='perfil_prestadores/', null=True, blank=True)
    nota_media_cache = models.DecimalField(max_digits=3, decimal_places=2, default=5)
    total_avaliacoes_cache = models.PositiveIntegerField(default=0)
    acessos_perfil = models.PositiveIntegerField(default=0)
    total_servicos_cache = models.PositiveIntegerField(default=0)
    servicos_nao_realizados_cache = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    servico = models.ForeignKey('servicos.Servico', on_delete=models.SET_NULL, null=True, blank=True, related_name='prestadores')
    is_deleted = models.BooleanField(default=False, editable=False)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['cep'], name='idx_cep'),
            models.Index(fields=['latitude', 'longitude'], name='idx_geo'),
            models.Index(fields=['is_deleted'], name='idx_prestador_deleted'),
        ]
    
    def save(self, *args, **kwargs):
        run_geocode = False
        if self.pk:
            try:
                antigo = PrestadorProfile.objects.get(pk=self.pk)
                
                if antigo.cep != self.cep or antigo.rua != self.rua or antigo.numero_casa != self.numero_casa:
                    run_geocode = True
                
                if not self.latitude or not self.cidade:
                    run_geocode = True

            except PrestadorProfile.DoesNotExist:
                run_geocode = True
        else:
            run_geocode = True

        if run_geocode and self.cep:
            dados = pegar_dados_endereco(self.cep, self.rua, self.numero_casa)
            if dados:
                self.latitude = dados['latitude']
                self.longitude = dados['longitude']
                self.cidade = dados['cidade']
                self.bairro = dados['bairro']
                self.estado = dados['estado']
            
        if self.telefone_publico:
            self.telefone_publico = _sanitize_telefone(self.telefone_publico)

        try:
            self.full_clean()
        except ModelValidationError:
            raise
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"
