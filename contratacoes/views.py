from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import quote
from drf_spectacular.utils import extend_schema
from .models import SolicitacaoContato
from .serializers import ContatoSerializer, SolicitacaoContatoDetailSerializer

class IniciarContatoWhatsAppView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ContatoSerializer,
        responses={201: dict, 400: dict},
        description="Inicia o contato via WhatsApp. Requer 'prestador_id' e 'servico'."
    )
    def post(self, request):
        serializer = ContatoSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            prestador_user = serializer.validated_data['prestador']
            servico = serializer.validated_data['servico']
            cliente_user = request.user

            SolicitacaoContato.objects.create(
                cliente=cliente_user,
                prestador=prestador_user,
                servico=servico
            )

            telefone = prestador_user.perfil_prestador.telefone_publico
            
            if not telefone:
                return Response(
                    {"erro": "Este prestador não possui telefone cadastrado."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            telefone_formatado = f"55{telefone}" 

            mensagem = (
                f"Olá {prestador_user.first_name}! "
                f"Me chamo {cliente_user.first_name}. "
                f"Encontrei seu perfil no *ServiçoJá* e gostaria de um orçamento para *{servico.nome}*."
            )
            
            mensagem_encoded = quote(mensagem)

            whatsapp_url = f"https://api.whatsapp.com/send?phone={telefone_formatado}&text={mensagem_encoded}"

            return Response({
                "sucesso": True,
                "whatsapp_url": whatsapp_url
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SolicitacaoPrestadorListView(generics.ListAPIView):
    """
    Lista as solicitações recebidas pelo prestador logado.
    """
    serializer_class = SolicitacaoContatoDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SolicitacaoContato.objects.filter(prestador=self.request.user).order_by('-data_clique')


class SolicitacaoClienteListView(generics.ListAPIView):
    serializer_class = SolicitacaoContatoDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SolicitacaoContato.objects.filter(cliente=self.request.user).order_by('-data_clique')


class ConcluirServicoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            solicitacao = SolicitacaoContato.objects.get(pk=pk, prestador=request.user)
        except SolicitacaoContato.DoesNotExist:
            return Response({"erro": "Solicitação não encontrada ou não pertence a este prestador."}, status=status.HTTP_404_NOT_FOUND)

        solicitacao.servico_realizado = True
        solicitacao.save()

        cliente_user = solicitacao.cliente
        prestador_user = request.user
        servico = solicitacao.servico
        #Lembrar de colocar o link de avaliacao
        link_avaliacao = "LinkAvaliacao" 

        if cliente_user.perfil_cliente.telefone_contato:
             telefone_cliente = f"55{cliente_user.perfil_cliente.telefone_contato}"
        else:
             telefone_cliente = ""

        mensagem = (
            f"Olá {cliente_user.first_name}! "
            f"O serviço de *{servico.nome}* foi concluído com sucesso. "
            f"Poderia avaliar meu atendimento? Isso é muito importante para mim! "
            f"Link: {link_avaliacao}"
        )
        
        mensagem_encoded = quote(mensagem)
        
        if telefone_cliente:
            whatsapp_url = f"https://api.whatsapp.com/send?phone={telefone_cliente}&text={mensagem_encoded}"
        else:
            whatsapp_url = f"https://api.whatsapp.com/send?text={mensagem_encoded}"

        return Response({
            "sucesso": True,
            "servico_realizado": True,
            "whatsapp_url": whatsapp_url
        }, status=status.HTTP_200_OK)
