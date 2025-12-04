from django.urls import path
from .views import (
    ClienteRegistrationView, 
    PrestadorRegistrationView, 
    PrestadorListView, 
    PrestadorProfileEditView, 
    PrestadorDetailView,
    UserProfileView,
    FavoritoManageView
)

urlpatterns = [
    #Urls de cadastro
    path('registro/cliente/', ClienteRegistrationView.as_view(), name='registrar-cliente'),
    path('registro/prestador/', PrestadorRegistrationView.as_view(), name='registrar-prestador'),

    #Urls de filtro público
    path('prestadores/', PrestadorListView.as_view(), name='lista-prestadores'),
    path('prestadores/<int:pk>/', PrestadorDetailView.as_view(), name='detalhe-prestador'),

    # Urls autenticadas
    path('perfil/prestador/editar/', PrestadorProfileEditView.as_view(), name='editar-perfil-prestador'),
    
    # User Profile endpoints
    path('me/', UserProfileView.as_view(), name='user-profile'), # Retorna e edita perfil do usuário logado

    # Favoritos
    path('favoritos/', FavoritoManageView.as_view(), name='gerenciar-favoritos'),
]
