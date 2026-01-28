# COMENTÁRIOS DETALHADOS - APPS: CONTRATACOES, AVALIACOES, PORTFOLIO
# Arquivo de referência com explicações sobre models, views e serializers

## ============================================================================
## CONTRATACOES APP
## ============================================================================

### Models (contratacoes/models.py)

#### SolicitacaoContato
```python
# Modelo que representa uma solicitação de contato entre cliente e prestador

Atributos:
- cliente: ForeignKey para User (quem solicitou)
- prestador: ForeignKey para User (quem vai fazer o serviço)
- servico: ForeignKey para Servico (tipo de serviço solicitado)
- servico_realizado: Boolean (True = concluído, False = não realizado, None = em aberto)
- data_clique: DateTime (quando foi criada a solicitação)
- data_conclusao: DateTime (quando o prestador marcou como concluído/não realizado)

Property:
- avaliacao_realizada: Verifica se existe uma Avaliacao relacionada

Relacionamentos Reversos:
- cliente.contatos_iniciados: Todos os contatos iniciados por este cliente
- prestador.contatos_recebidos: Todos os contatos recebidos por este prestador

Lógica de Negócio:
1. Cliente vê prestador e inicia contato
2. Sistema cria SolicitacaoContato
3. Gera URL de WhatsApp pré-preenchida
4. Prestador realiza o trabalho
5. Prestador marca como "concluído" e envia link de avaliação
6. Cliente avalia (cria Avaliacao com FK para SolicitacaoContato)
```

### Views (contratacoes/views.py)

#### IniciarContatoWhatsAppView
```python
# POST /api/contratacoes/iniciar/

Processo:
1. Recebe prestador_id e servico_id
2. Valida se cliente não está tentando contatar a si mesmo
3. Cria SolicitacaoContato no BD
4. Extrai telefone do prestador
5. Gera mensagem pré-preenchida
6. Retorna URL de WhatsApp pronta para usar

Entrada:
{
  "prestador_id": 1,
  "servico_id": 5
}

Resposta (201):
{
  "sucesso": true,
  "whatsapp_url": "https://api.whatsapp.com/send?phone=55..."
}

URL de WhatsApp:
- Encodeada com a mensagem pré-preenchida
- Formato de telefone: +55 + DDD + 9 dígitos
- Mensagem apresenta cliente e tipo de serviço
```

#### SolicitacaoPrestadorListView
```python
# GET /api/contratacoes/prestador/solicitacoes/

Retorna todas as solicitações recebidas pelo prestador logado

Query Params:
- ?status=pendente/concluido/nao_realizado

Retorna Paginado (20 por página):
[
  {
    "id": 1,
    "cliente": { "id": 1, "nome_completo": "João" },
    "prestador": { "id": 2, "nome_completo": "Maria" },
    "servico": { "id": 5, "nome": "Limpeza" },
    "status": "pendente",
    "data_clique": "2026-01-28T10:00:00Z",
    "data_conclusao": null,
    "avaliacao_realizada": false
  }
]

Útil para:
- Prestador ver seus contatos recebidos
- Gerenciar lista de trabalhos
- Saber qual não foi avaliado ainda
```

#### SolicitacaoClienteListView
```python
# GET /api/contratacoes/cliente/solicitacoes/

Retorna todas as solicitações iniciadas pelo cliente logado

Mesma lógica de SolicitacaoPrestadorListView

Útil para:
- Cliente acompanhar seus contatos
- Ver se prestador concluiu ou não
- Decidir se avalia ou não
```

#### ConcluirServicoView
```python
# POST /api/contratacoes/solicitacoes/<id>/concluir/

Apenas para o prestador proprietário da solicitação

Processo:
1. Marca servico_realizado = True
2. Preenche data_conclusao = now()
3. Gera mensagem de conclusão com link de avaliação
4. Retorna URL de WhatsApp para enviar mensagem ao cliente

Resposta (200):
{
  "sucesso": true,
  "servico_realizado": true,
  "whatsapp_url": "https://api.whatsapp.com/send?phone=..."
}

Mensagem Enviada:
"Olá João! O serviço de Limpeza foi concluído com sucesso.
Poderia avaliar meu atendimento? Isso é muito importante para mim!
Link: [link_avaliacao]"
```

#### NaoRealizarServicoView
```python
# POST /api/contratacoes/solicitacoes/<id>/nao-realizado/

Marca o serviço como não realizado pelo prestador

Processo:
1. Verifica se não foi finalizado antes
2. Marca servico_realizado = False
3. Preenche data_conclusao = now()
4. Incrementa servicos_nao_realizados_cache no perfil do prestador

Resposta (200):
{
  "sucesso": true,
  "servico_realizado": false,
  "mensagem": "Serviço marcado como não realizado."
}

Consequências:
- Não pode criar avaliação após marcar como não realizado
- Contador aumenta (impacta reputação do prestador)
- Histórico de atividades registrado
```

### Serializers (contratacoes/serializers.py)

#### ContatoSerializer
```python
# Valida dados para iniciar contato

Campos de Entrada:
- prestador_id: ID do prestador (campo write_only)
- servico_id: ID do serviço

Validações:
- Prestador deve existir e ser do tipo 'prestador'
- Serviço deve existir
- Cliente não pode contatar a si mesmo

Lógica:
- source='prestador' mapeia prestador_id para o campo prestador
```

#### SolicitacaoContatoDetailSerializer
```python
# Serializa SolicitacaoContato com dados relacionados em read_only

Campos de Saída:
- id, cliente, cliente_nome, prestador, prestador_nome
- servico, servico_nome
- servico_realizado (Boolean)
- avaliacao_realizada (Property do model)
- data_clique, data_conclusao

Permite Ler:
- Nomes do cliente e prestador (sem fetches extras)
- Nome do serviço
- Status de conclusão e avaliação
```

## ============================================================================
## AVALIACOES APP
## ============================================================================

### Models (avaliacoes/models.py)

#### Avaliacao
```python
# Modelo que representa uma avaliação/review de um serviço

Atributos:
- solicitacao_contato: OneToOneField (uma avaliação por contato)
- nota: IntegerField 1-5 (com validadores MinValueValidator, MaxValueValidator)
- comentario: TextField opcional
- data_criacao: DateTime auto_now_add
- data_atualizacao: DateTime auto_now

Validações:
- nota deve estar entre 1 e 5 (validadores no field)
- Apenas uma avaliação por SolicitacaoContato (unique_together)

Meta Options:
- unique_together = ('solicitacao_contato',)
- ordering = ['-data_criacao'] (mais recentes primeiro)

Lógica:
- Criada apenas APÓS serviço ser concluído
- Criada apenas pelo cliente que contratou
- Não pode ser editada (apenas criada)
```

### Views (avaliacoes/views.py)

#### CriarAvaliacaoView
```python
# POST /api/avaliacoes/

Cria uma nova avaliação

Entrada:
{
  "solicitacao_contato_id": 1,
  "nota": 5,
  "comentario": "Excelente serviço!"
}

Validações (no Serializer):
- SolicitacaoContato deve existir
- Cliente logado deve ser quem contratou
- Serviço deve estar marcado como concluído
- Não pode haver avaliação prévia

Resposta (201):
{
  "id": 1,
  "nota": 5,
  "comentario": "Excelente...",
  "data_criacao": "2026-01-28T10:00:00Z"
}

Efeitos Colaterais (Signal):
- Atualiza cache em PrestadorProfile
  - nota_media_cache
  - total_avaliacoes_cache
  - total_servicos_cache
```

#### AvaliacaoListView
```python
# GET /api/avaliacoes/listar/

Lista avaliações com filtros, busca e estatísticas

Filtros:
- ?prestador=1: Avaliações de um prestador específico
- ?minhas=true: Apenas avaliações do usuário logado (cliente)
- ?nota_minima=4: Apenas notas >= 4
- ?ordenar=maior_nota: Ordena por maior nota
- ?ordenar=menor_nota: Ordena por menor nota
- (padrão): Ordena por mais recentes

Retorna com Estatísticas:
{
  "estatisticas": {
    "media_geral": 4.8,
    "total_avaliacoes": 10,
    "distribuicao": {
      "estrelas_1": { "quantidade": 0, "porcentagem": 0 },
      "estrelas_2": { "quantidade": 0, "porcentagem": 0 },
      "estrelas_3": { "quantidade": 0, "porcentagem": 0 },
      "estrelas_4": { "quantidade": 2, "porcentagem": 20 },
      "estrelas_5": { "quantidade": 8, "porcentagem": 80 }
    }
  },
  "results": [...]
}

Paginado:
- 20 itens por página
- Inclui "next" e "previous" URLs
```

#### AvaliacaoDetailView
```python
# GET /api/avaliacoes/<id>/

Retorna avaliação específica com dados relacionados

Exemplo:
{
  "id": 1,
  "cliente_nome": "João Silva",
  "prestador_nome": "Maria Santos",
  "prestador_id": 2,
  "prestador_foto": "https://...",
  "nota": 5,
  "comentario": "Excelente!",
  "data": "28/01/2026"
}
```

### Serializers (avaliacoes/serializers.py)

#### CriarAvaliacaoSerializer
```python
# Serializa criação de avaliação com validações

Campos:
- solicitacao_contato_id (write_only)
- nota (1-5)
- comentario (opcional)

Validações Customizadas:
- validate_solicitacao_contato_id():
  1. Verifica se cliente logado é quem contratou
  2. Verifica se serviço foi marcado como concluído
  3. Verifica se não há avaliação prévia
  4. Levanta ValidationError se algo falhar
```

#### AvaliacaoSerializer
```python
# Serializa avaliação para leitura (com dados relacionados)

Campos:
- id, cliente_nome, prestador_nome, prestador_id
- prestador_foto (URL build com build_absolute_uri)
- nota, comentario, data (formatada como dd/mm/yyyy)

Métodos:
- get_prestador_foto(): Obtém foto do prestador (PrestadorProfile.foto_perfil)

Read-Only: Tudo é apenas leitura
```

## ============================================================================
## PORTFOLIO APP
## ============================================================================

### Models (portfolio/models.py)

#### PortfolioItem
```python
# Modelo que representa uma foto/item do portfólio do prestador

Atributos:
- prestador: ForeignKey para PrestadorProfile
- imagem: ImageField armazenado em Cloudinary (null e blank permitido)
- descricao: CharField até 255 caracteres (opcional)
- created_at: DateTime auto_now_add

Uso:
- Prestador faz upload de fotos seus trabalhos anteriores
- Cliente vê no perfil do prestador
- Ajuda a confiança e decisão de contrato

Upload:
- Armazenado em Cloudinary (nuvem)
- URL retornada nos serializers
- Sem limite de quantidade
```

### Views (portfolio/views.py)

#### PortfolioViewSet
```python
# ViewSet completo (CRUD) para itens do portfólio

Endpoints:
- GET    /api/portfolio/itens/
  Lista itens do portfólio do prestador logado

- POST   /api/portfolio/itens/
  Cria novo item (auto-vinculado ao prestador)
  Requer multipart/form-data (upload de arquivo)

- GET    /api/portfolio/itens/<id>/
  Detalhes de um item específico

- PUT    /api/portfolio/itens/<id>/
  Edita item (apenas proprietário)

- DELETE /api/portfolio/itens/<id>/
  Deleta item (apenas proprietário)

Permissões: IsAuthenticated (apenas prestadores logados)

Método get_queryset():
- Se usuário é prestador: retorna seus itens
- Se usuário é cliente: retorna QuerySet vazio

Método perform_create():
- Auto-vincula item ao prestador logado
- Não precisa enviar prestador_id na requisição
```

### Serializers (portfolio/serializers.py)

#### PortfolioItemSerializer
```python
# Serializa itens do portfólio

Campos:
- id (read_only)
- imagem (ImageField para upload)
- descricao (CharField)
- created_at (read_only, DateTime)

Entrada (POST/PUT):
{
  "imagem": <arquivo>,
  "descricao": "Descrição do projeto"
}

Saída (GET):
{
  "id": 1,
  "imagem": "https://cloudinary.com/...",
  "descricao": "Descrição...",
  "created_at": "2026-01-28T10:00:00Z"
}

Upload:
- Content-Type: multipart/form-data
- Campo "imagem" é obrigatório
- Descricao é opcional
```

## ============================================================================
## FLUXOS DE DADOS COMPLETOS
## ============================================================================

### Fluxo 1: Cliente Contrata Prestador e Avalia

```
1. POST /api/accounts/registro/cliente/
   → Cria User + ClienteProfile
   → Retorna access token

2. GET /api/accounts/prestadores/
   → Lista prestadores disponíveis
   → Cliente vê perfil de Maria (nota 4.8, avaliações, portfólio)

3. POST /api/contratacoes/iniciar/
   → Cria SolicitacaoContato
   → Retorna WhatsApp URL
   → Cliente clica e conversa com Maria no WhatsApp

4. POST /api/contratacoes/solicitacoes/<id>/concluir/
   → Maria marca como concluído
   → Retorna WhatsApp URL
   → Maria envia link de avaliação ao cliente

5. POST /api/avaliacoes/
   → Cliente cria avaliação (nota 5, comentário "Ótimo!")
   → Signal atualiza cache de Maria
   → Maria vê sua nova nota média (4.81)

6. GET /api/avaliacoes/listar/?prestador=2
   → Busca vê todas as avaliações de Maria
   → Vê estatísticas: 50 avaliações, média 4.81, 90% cinco estrelas
```

### Fluxo 2: Prestador Gerencia Portfólio

```
1. POST /api/portfolio/itens/
   → Maria faz upload de foto de um trabalho
   → Descricao: "Limpeza de apartamento 100m2"
   → Auto-vinculado ao perfil de Maria

2. PUT /api/portfolio/itens/1/
   → Maria edita descricao de um item

3. GET /api/portfolio/itens/
   → Maria vê suas 10 fotos de portfólio

4. GET /api/accounts/prestadores/1/
   → Cliente vê portfólio de Maria no perfil público
   → Vê as fotos de trabalhos anteriores
   → Decide contratar por confiança
```

## ============================================================================
## VALIDAÇÕES E REGRAS DE NEGÓCIO
## ============================================================================

### Contratações
- Cliente não pode contatar a si mesmo
- Apenas SolicitacaoContato concluída pode ter Avaliacao
- Cada SolicitacaoContato pode ter no máximo 1 Avaliacao

### Avaliações
- Nota deve estar entre 1 e 5
- Cliente só pode avaliar serviço que contratou
- Prestador não pode avaliar sua própria avaliação
- Avaliação não pode ser editada (apenas criada)
- Signal atualiza cache imediatamente

### Portfólio
- Apenas prestador logado pode ver/editar seus itens
- Cliente vê portfólio no perfil público
- Sem limite de itens
- Imagem deve ser <= 5MB (padrão Cloudinary)
