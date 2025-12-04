from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ClienteRegistrationSerializer, PrestadorRegistrationSerializer, PrestadorProfileEditSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserProfileSerializer
from .models import PrestadorProfile, User
from .serializers import PrestadorPublicoSerializer
import math

class ClienteRegistrationView(generics.CreateAPIView):
    #Endpoint da API Cliente. Aceita apenas requisições POST.
    serializer_class = ClienteRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        data = serializer.data
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user_id'] = user.id 
        
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

class PrestadorRegistrationView(generics.CreateAPIView):
    #Endpoint da API Cliente. Aceita apenas requisições POST.
    serializer_class = PrestadorRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        data = serializer.data
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user_id'] = user.id
        data['profile_id'] = user.perfil_prestador.id
        
        if hasattr(user, 'perfil_prestador'):
            data['profile_id'] = user.perfil_prestador.id
        elif hasattr(user, 'perfil_cliente'):
            data['profile_id'] = user.perfil_cliente.id

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

class CustomTokenObtainPairView(TokenObtainPairView):
    #View personalizada para obtenção de token JWT
    serializer_class = CustomTokenObtainPairSerializer

# Fórmula matemática para cálculo de distância entre dois pontos (latitude/longitude)
def calcular_distancia(lat1, lon1, lat2, lon2):
    if not lat1 or not lon1 or not lat2 or not lon2:
        return None

    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
    except ValueError:
        return None

    R = 6371.0

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return round(distance, 2)

class PrestadorDetailView(generics.RetrieveAPIView):
    queryset = PrestadorProfile.objects.all()
    serializer_class = PrestadorPublicoSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk' # Busca pelo ID do PrestadorProfile, não do User

class PrestadorListView(generics.ListAPIView):
    """
    
    /api/accounts/prestadores/numero_do_id_do_prestador/

    Filtros:
    ?servico=ID
    ?categoria=ID
    ?possui_material_proprio=true/false
    ?disponibilidade=true/false
    ?atende_fim_de_semana=true/false
    ?melhor_avaliado=true
    ?nota_minima=ID
    ?nome=nome_prestador
    ?nome_servico=nome_servico
    
    ?ordenar_por_distancia=true (latitude/longitude do cliente logado ou na URL)

    """
    serializer_class = PrestadorPublicoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = PrestadorProfile.objects.all()

        servico_id = self.request.query_params.get('servico')
        categoria_id = self.request.query_params.get('categoria')
        tem_material = self.request.query_params.get('possui_material_proprio')
        disponibilidade = self.request.query_params.get('disponibilidade')
        fim_de_semana = self.request.query_params.get('atende_fim_de_semana')
        nome = self.request.query_params.get('nome')
        nome_servico = self.request.query_params.get('nome_servico')

        # Filtro por nome (case-insensitive)
        if nome:
            queryset = queryset.filter(user__nome_completo__icontains=nome)

        # Filtro por nome do serviço (case-insensitive)
        if nome_servico:
            queryset = queryset.filter(servico__nome__icontains=nome_servico)

        # Filtro por ID do Serviço
        if servico_id:
            queryset = queryset.filter(servico__id=servico_id)

        # Filtro por ID da Categoria
        if categoria_id:
            queryset = queryset.filter(servico__categoria__id=categoria_id)

        # Filtros de material, disponibilidade e fim de semana
        if tem_material is not None:
            valor = tem_material.lower() == 'true'
            queryset = queryset.filter(possui_material_proprio=valor)
            
        if disponibilidade is not None:
            valor = disponibilidade.lower() == 'true'
            queryset = queryset.filter(disponibilidade=valor)
            
        if fim_de_semana is not None:
            valor = fim_de_semana.lower() == 'true'
            queryset = queryset.filter(atende_fim_de_semana=valor)
            
        # Filtro por avaliação mínima
        nota_minima = self.request.query_params.get('nota_minima')
        if nota_minima:
             try:
                 nota = float(nota_minima)
                 queryset = queryset.filter(nota_media_cache__gte=nota)
             except ValueError:
                 pass
        
        # Filtro para mostrar os mais bem avaliados (ordenação)
        melhor_avaliado = self.request.query_params.get('melhor_avaliado')
        if melhor_avaliado and melhor_avaliado.lower() == 'true':
            queryset = queryset.order_by('-nota_media_cache')

        # Evita duplicatas
        return queryset.distinct()
    
    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        
        cliente_lat = request.query_params.get('latitude')
        cliente_lon = request.query_params.get('longitude')

        #Tenta pegar do usuário logado (se for cliente)
        if not cliente_lat and request.user.is_authenticated and hasattr(request.user, 'perfil_cliente'):
             cliente_lat = request.user.perfil_cliente.latitude
             cliente_lon = request.user.perfil_cliente.longitude

        prestadores_lista = []
        
        for prestador in queryset:
            dist = None
            
            # Só calcula se tivermos as coordenadas dos DOIS lados
            if cliente_lat and cliente_lon and prestador.latitude and prestador.longitude:
                dist = calcular_distancia(
                    cliente_lat, cliente_lon, 
                    prestador.latitude, prestador.longitude
                )
            
            prestador.distancia = dist 
            prestadores_lista.append(prestador)

        # Só ordena se o front-end pedir explicitamente com ?ordenar_por_distancia=true
        ordenar = request.query_params.get('ordenar_por_distancia')

        if ordenar == 'true' and cliente_lat and cliente_lon:
            # Ordena do menor para o maior
            prestadores_lista.sort(key=lambda x: x.distancia if x.distancia is not None else float('inf'))

        serializer = self.get_serializer(prestadores_lista, many=True)
        return Response(serializer.data)

class PrestadorProfileEditView(generics.RetrieveUpdateAPIView):
    serializer_class = PrestadorProfileEditSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user.perfil_prestador

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class FavoritoManageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'perfil_cliente'):
             return Response({"detail": "Apenas clientes podem ter favoritos."}, status=status.HTTP_403_FORBIDDEN)
        
        favoritos = request.user.perfil_cliente.favoritos.all()
        serializer = PrestadorPublicoSerializer(favoritos, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not hasattr(request.user, 'perfil_cliente'):
             return Response({"detail": "Apenas clientes podem adicionar favoritos."}, status=status.HTTP_403_FORBIDDEN)
             
        prestador_id = request.data.get('prestador_id')
        if not prestador_id:
            return Response({"detail": "ID do prestador não fornecido."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            prestador = PrestadorProfile.objects.get(id=prestador_id)
        except PrestadorProfile.DoesNotExist:
            return Response({"detail": "Prestador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
            
        cliente_profile = request.user.perfil_cliente
        
        if prestador in cliente_profile.favoritos.all():
            cliente_profile.favoritos.remove(prestador)
            return Response({"detail": "Prestador removido dos favoritos.", "favoritado": False}, status=status.HTTP_200_OK)
        else:
            cliente_profile.favoritos.add(prestador)
            return Response({"detail": "Prestador adicionado aos favoritos.", "favoritado": True}, status=status.HTTP_201_CREATED)
