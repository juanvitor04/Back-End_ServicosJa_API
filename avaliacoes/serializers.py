from rest_framework import serializers
from .models import Avaliacao
from contratacoes.models import SolicitacaoContato

class CriarAvaliacaoSerializer(serializers.ModelSerializer):
    solicitacao_contato_id = serializers.PrimaryKeyRelatedField(
        queryset=SolicitacaoContato.objects.all(),
        source='solicitacao_contato'
    )

    class Meta:
        model = Avaliacao
        fields = ['solicitacao_contato_id', 'nota', 'comentario']

    def validate_solicitacao_contato_id(self, value):
        user = self.context['request'].user
        
        if value.cliente != user:
            raise serializers.ValidationError("Você só pode avaliar contatos que você iniciou.")
        
        if not value.servico_realizado:
            raise serializers.ValidationError("Este serviço ainda não foi marcado como concluído pelo prestador.")

        if hasattr(value, 'avaliacao'):
             raise serializers.ValidationError("Este serviço já foi avaliado.")

        return value

class AvaliacaoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='solicitacao_contato.cliente.nome_completo', read_only=True)
    data = serializers.DateTimeField(source='data_criacao', format="%d/%m/%Y", read_only=True)
    
    class Meta:
        model = Avaliacao
        fields = ['id', 'cliente_nome', 'nota', 'comentario', 'data']
