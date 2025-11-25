from rest_framework import viewsets, permissions
from .models import PortfolioItem
from .serializers import PortfolioItemSerializer

class PortfolioViewSet(viewsets.ModelViewSet):
    # ViewSet para gerenciar o portfólio de fotos dos prestadores de serviço.
    #- Listar: Mostra só as minhas fotos.
    #- Criar: Salva a foto vinculada ao meu perfil.
    
    serializer_class = PortfolioItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil_prestador'):
            return PortfolioItem.objects.filter(prestador=self.request.user.perfil_prestador)
        return PortfolioItem.objects.none()

    def perform_create(self, serializer):
        serializer.save(prestador=self.request.user.perfil_prestador)