from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Avaliacao
from .serializers import CriarAvaliacaoSerializer, AvaliacaoSerializer

class CriarAvaliacaoView(generics.CreateAPIView):
    """
    Endpoint para criar uma avaliação.
    O usuário precisa estar logado
    """
    queryset = Avaliacao.objects.all()
    serializer_class = CriarAvaliacaoSerializer
    permission_classes = [permissions.IsAuthenticated]

class AvaliacaoListView(generics.ListAPIView):
    """
    Lista avaliações. Permite filtrar por prestador (user ID).
    Retorna também estatísticas das avaliações.
    """
    serializer_class = AvaliacaoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Avaliacao.objects.all()
        prestador_id = self.request.query_params.get('prestador')
        
        if prestador_id:
            queryset = queryset.filter(solicitacao_contato__prestador__id=prestador_id)

        # Filtro por nota mínima (ex: pegar só as 5 estrelas)
        nota_minima = self.request.query_params.get('nota_minima')
        if nota_minima:
            queryset = queryset.filter(nota__gte=nota_minima)

        # Ordenação
        ordenar = self.request.query_params.get('ordenar')
        if ordenar == 'maior_nota':
            queryset = queryset.order_by('-nota', '-data_criacao')
        elif ordenar == 'menor_nota':
            queryset = queryset.order_by('nota', '-data_criacao')
        else:
            # Padrão: Mais recentes primeiro
            queryset = queryset.order_by('-data_criacao')
            
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Estatísticas
        stats = queryset.aggregate(
            media=Avg('nota'),
            total=Count('id')
        )
        
        counts = queryset.values('nota').annotate(count=Count('nota')).order_by('nota')
        
        # Inicializa contadores
        distribuicao = {i: 0 for i in range(1, 6)}
        total = stats['total'] or 0
        
        for item in counts:
            distribuicao[item['nota']] = item['count']
            
        # Calcula porcentagens e formata resposta da distribuição
        stats_distribuicao = {}
        for nota, count in distribuicao.items():
            stats_distribuicao[f"estrelas_{nota}"] = {
                "quantidade": count,
                "porcentagem": round((count / total * 100), 2) if total > 0 else 0
            }

        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            "estatisticas": {
                "media_geral": round(stats['media'], 2) if stats['media'] else 0,
                "total_avaliacoes": total,
                "distribuicao": stats_distribuicao
            },
            "avaliacoes": serializer.data
        })

class AvaliacaoDetailView(generics.RetrieveAPIView):
    """
    Recupera uma avaliação específica pelo ID.
    """
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [permissions.AllowAny]
