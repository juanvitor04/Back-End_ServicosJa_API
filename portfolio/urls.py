from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PortfolioViewSet

router = DefaultRouter()
router.register(r'itens', PortfolioViewSet, basename='portfolio-itens')

urlpatterns = [
    path('', include(router.urls)),
]
