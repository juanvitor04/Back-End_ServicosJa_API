from rest_framework import serializers
from .models import PortfolioItem

class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['id', 'imagem', 'descricao', 'created_at']
        read_only_fields = ['id', 'created_at']