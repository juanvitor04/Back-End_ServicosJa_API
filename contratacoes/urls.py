from django.urls import path
from .views import (
    IniciarContatoWhatsAppView,
    SolicitacaoPrestadorListView,
    SolicitacaoClienteListView,
    ConcluirServicoView,
    NaoRealizarServicoView
)

urlpatterns = [
    path('iniciar/', IniciarContatoWhatsAppView.as_view(), name='iniciar-contato-whatsapp'),
    path('prestador/solicitacoes/', SolicitacaoPrestadorListView.as_view(), name='prestador-solicitacoes'),
    path('cliente/solicitacoes/', SolicitacaoClienteListView.as_view(), name='cliente-solicitacoes'),
    path('solicitacoes/<int:pk>/concluir/', ConcluirServicoView.as_view(), name='concluir-servico'),
    path('solicitacoes/<int:pk>/nao-realizado/', NaoRealizarServicoView.as_view(), name='nao-realizar-servico'),
]
