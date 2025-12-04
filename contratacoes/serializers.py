from rest_framework import serializers
from .models import SolicitacaoContato
from django.contrib.auth import get_user_model

User = get_user_model()
class ContatoSerializer(serializers.ModelSerializer):
    prestador_id = serializers.PrimaryKeyRelatedField(
        source='prestador', 
        queryset=User.objects.filter(tipo_usuario='prestador')
    )
    
    class Meta:
        model = SolicitacaoContato
        fields = ['prestador_id', 'servico']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user == data['prestador']:
            raise serializers.ValidationError("Você não pode iniciar contato consigo mesmo.")
        return data

class SolicitacaoContatoDetailSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome_completo', read_only=True)
    prestador_nome = serializers.CharField(source='prestador.nome_completo', read_only=True)
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    
    avaliacao_realizada = serializers.BooleanField(read_only=True)

    class Meta:
        model = SolicitacaoContato
        fields = [
            'id', 
            'cliente', 'cliente_nome',
            'prestador', 'prestador_nome',
            'servico', 'servico_nome',
            'servico_realizado',
            'avaliacao_realizada',
            'data_clique',
            'data_conclusao'
        ]
