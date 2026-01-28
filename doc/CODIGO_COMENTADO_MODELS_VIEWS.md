# Documentação de Comentários em Models e Views

## 📋 Resumo

Este documento lista todos os arquivos que receberam comentários detalhados (docstrings) em modelos e views.

**Data de Atualização:** Janeiro 2025  
**Status:** ✅ Completo (Models + Views)

---

## 📁 Arquivos Comentados

### 1. **accounts/models.py** ✅ COMPLETO

#### Modules e Funcções:
- **`pegar_dados_endereco(cep, rua, numero)`** - Função de geolocalização com fallback (BrasilAPI → ViaCEP → Nominatim)
- **`_sanitize_telefone(telefone)`** - Função para formatar telefone

#### Modelos:
- **`User`** - Modelo customizado de autenticação
  - Login por EMAIL
  - Suporte para cliente/prestador
  - Validação de CPF
  - Property `idade` (calcula dinamicamente)
  - Métodos: `get_full_name()`, `get_short_name()`, `clean()`, `save()`

- **`ClienteProfile`** - Perfil de cliente
  - Endereço com geolocalização automática
  - Lista de prestadores favoritos (M2M)
  - Foto de perfil
  - Método `save()` com lógica de geolocalização

- **`PrestadorProfile`** - Perfil de prestador
  - Biografia e dados profissionais
  - Endereço com geolocalização
  - Informações de disponibilidade
  - Cache de métricas (nota_media, total_avaliacoes, etc)
  - Índices para otimização geográfica
  - Método `save()` com validações e geolocalização

---

### 2. **accounts/views.py** ✅ COMPLETO

#### Autenticação:
- **`ClienteRegistrationView`** - Registro de clientes
  - POST: Cria usuário cliente com token JWT

- **`PrestadorRegistrationView`** - Registro de prestadores
  - POST: Cria usuário prestador com token JWT

- **`CustomTokenObtainPairView`** - Login/obtenção de tokens
  - POST: Autentica e retorna tokens JWT

#### Geolocalização:
- **`calcular_distancia(lat1, lon1, lat2, lon2)`** - Fórmula de Haversine
  - Calcula distância entre dois pontos geográficos

#### Listagem e Busca:
- **`PrestadorDetailView`** - Detalhe de prestador
  - GET: Retorna dados públicos de um prestador

- **`PrestadorListView`** - Listagem com filtros e busca por proximidade
  - GET: Lista prestadores com múltiplos filtros
  - Filtros: serviço, categoria, material próprio, disponibilidade, nota mínima, nome
  - Ordenação por distância (com geolocalização)
  - Método `get_queryset()` com select_related/prefetch_related
  - Método `list()` com cálculo de distância para cada prestador

#### Edição de Perfis:
- **`PrestadorProfileEditView`** - Editar perfil do prestador logado
  - GET/PUT/PATCH: Obter e atualizar próprio perfil

- **`ClienteProfileEditView`** - Editar perfil do cliente logado
  - GET/PUT/PATCH: Obter e atualizar próprio perfil

- **`UserProfileView`** - Editar dados do usuário logado
  - GET/PUT/PATCH: Obter e atualizar dados pessoais

#### Favoritos:
- **`FavoritoManageView`** - Gerenciar prestadores favoritos
  - GET: Listar favoritos
  - POST: Adicionar/remover (toggle) um prestador dos favoritos

---

### 3. **contratacoes/models.py** ✅ COMPLETO

#### Modelos:
- **`SolicitacaoContato`** - Registro de contrato de serviço
  - Fluxo: Cliente contrata → Contato via WhatsApp → Serviço realizado → Avaliação
  - Campos: cliente, prestador, servico, servico_realizado, data_clique, data_conclusao
  - Property: `avaliacao_realizada` (verifica se foi avaliado)
  - Índices em cliente/data e prestador/servico_realizado
  - Relacionamento implícito com Avaliacao via OneToOne

---

### 4. **contratacoes/views.py** ✅ COMPLETO

#### Views:
- **`IniciarContatoWhatsAppView`** - Iniciar contato via WhatsApp
  - POST: Cria SolicitacaoContato e retorna URL do WhatsApp
  - Validação: Prestador deve ter telefone cadastrado
  - Integração: Gera URL para abrir WhatsApp com mensagem pré-preenchida

- **`SolicitacaoPrestadorListView`** - Listar solicitações recebidas
  - GET: Lista contratos que o prestador recebeu

- **`SolicitacaoClienteListView`** - Listar solicitações iniciadas
  - GET: Lista contratos que o cliente iniciou

- **`ConcluirServicoView`** - Marcar serviço como concluído
  - POST: Prestador marca serviço como realizado
  - Efeito: Envia WhatsApp pedindo avaliação ao cliente

- **`NaoRealizarServicoView`** - Marcar serviço como não realizado
  - POST: Prestador marca serviço como não realizado
  - Efeito: Incrementa cache de serviços_nao_realizados

---

### 5. **avaliacoes/models.py** ✅ COMPLETO

#### Modelos:
- **`Avaliacao`** - Avaliação de serviço
  - OneToOne com SolicitacaoContato (1 avaliação por contato)
  - Nota: 1-5 estrelas (validada com MinValueValidator/MaxValueValidator)
  - Comentário: Feedback opcional
  - Relacionamento com sinal para atualizar cache de nota_media

---

### 6. **avaliacoes/views.py** ✅ COMPLETO

#### Views:
- **`CriarAvaliacaoView`** - Criar avaliação
  - POST: Cliente avalia prestador
  - Validações: Nota 1-5, solicitacao_contato válida
  - Efeito colateral: Signal atualiza PrestadorProfile.nota_media_cache

- **`AvaliacaoListView`** - Listar avaliações com estatísticas
  - GET: Lista avaliações com múltiplos filtros
  - Filtros: prestador, minhas (do usuário logado), nota_minima
  - Ordenação: por nota ou data
  - Estatísticas: media_geral, total_avaliacoes, distribuição por nota
  - Método `get_queryset()` com filtros
  - Método `list()` com cálculo de estatísticas e distribuição

- **`AvaliacaoDetailView`** - Detalhe de avaliação
  - GET: Retorna dados de uma avaliação específica

---

### 7. **portfolio/models.py** ✅ COMPLETO

#### Modelos:
- **`PortfolioItem`** - Item de galeria de fotos
  - Foto de trabalho realizado pelo prestador
  - Armazenamento no Cloudinary
  - Descrição opcional
  - Relacionamento com PrestadorProfile

---

### 8. **servicos/models.py** ✅ COMPLETO
- **`CategoriaServico`** - Categoria de serviço
  - Organiza serviços em grupos (Encanamento, Eletricidade, etc)
  - Ícone no Cloudinary

- **`Servico`** - Tipo específico de serviço
  - Exemplo: "Troca de cano" dentro de "Encanamento"
  - Relacionamento com CategoriaServico
  - Índice em categoria

- **`PrestadorServicos`** - Associação M:N
  - Indica quais serviços um prestador oferece
  - unique_together: Um prestador/serviço apenas uma vez
  - Índices para otimização

---

### 9. **servicos/views.py** ✅ COMPLETO

#### ViewSets:
- **`CategoriaViewSet`** - ViewSet para categorias
  - GET: Listar categorias
  - Serializer dinâmico: 
    - Padrão: Dados simples da categoria
    - Com ?include_servicos=true: Inclui serviços aninhados

- **`ServicoViewSet`** - ViewSet para serviços
  - GET: Listar todos os serviços

---

### 10. **portfolio/views.py** ✅ COMPLETO

#### ViewSets:
- **`PortfolioViewSet`** - ViewSet para galeria de fotos
  - GET: Listar próprias fotos
  - POST: Adicionar nova foto
  - PUT/PATCH: Atualizar foto
  - DELETE: Remover foto
  - Método `get_queryset()`: Isolamento por prestador
  - Método `perform_create()`: Vincula automáticamente ao prestador logado

**Total de comentários:** 90+ linhas

---

## 📊 Estatísticas

| Arquivo | Tipo | Linhas de Código | Linhas de Comentários |
|---------|------|------------------|----------------------|
| accounts/models.py | models | 280+ | 150+ |
| accounts/views.py | views | 273 | 200+ |
| contratacoes/models.py | models | 80+ | 80+ |
| contratacoes/views.py | views | 153 | 180+ |
| avaliacoes/models.py | models | 50+ | 80+ |
| avaliacoes/views.py | views | 110 | 160+ |
| portfolio/models.py | models | 30+ | 70+ |
| servicos/models.py | models | 100+ | 140+ |
| servicos/views.py | views | 50+ | 100+ |
| portfolio/views.py | views | 40+ | 90+ |
| **TOTAL** | | **1,150+** | **1,250+** |

---

## 🎯 Padrões Utilizados

### 1. **Docstrings em Classes**
```python
class User(AbstractUser):
    """
    Descrição detalhada do modelo.
    
    Características:
    - Ponto 1
    - Ponto 2
    
    Fields Customizados:
    - campo1: descrição
    - campo2: descrição
    
    Exemplo:
        user = User.objects.create_user(...)
    """
```

### 2. **Docstrings em Métodos**
```python
def save(self, *args, **kwargs):
    """
    Descrição do método.
    
    Processo:
    1. Etapa 1
    2. Etapa 2
    
    Validações:
    - Validação 1
    - Validação 2
    """
```

### 3. **Docstrings em ViewSets**
```python
class PrestadorListView(generics.ListAPIView):
    """
    Endpoint para listar prestadores.
    
    Método: GET /api/accounts/prestadores/
    
    Parâmetros de Filtro:
    - servico: ID do serviço
    - categoria: ID da categoria
    
    Resposta (200 OK):
    {...}
    
    Permissões: AllowAny
    """
```

### 4. **Comentários Inline**
```python
# Título explicativo
campo = models.CharField(
    max_length=100,
    help_text='Descrição do campo'
)
```

---

## 🔍 Conteúdo dos Comentários

Cada docstring/comentário inclui:

1. **O QUÊ**: O que o código faz
2. **POR QUÊ**: Por que foi implementado assim
3. **COMO**: Como é usado (exemplos)
4. **CAMPOS/MÉTODOS**: Descrição de cada campo e método
5. **RELACIONAMENTOS**: Como se relaciona com outras entidades
6. **VALIDAÇÕES**: Regras e constraints
7. **EXEMPLOS DE USO**: Código prático
8. **ENDPOINTS**: URLs e parâmetros (para views)
9. **RESPOSTAS**: Formato das respostas HTTP
10. **PERMISSÕES**: Requisitos de autenticação

---

## 🚀 Próximos Passos (Opcional)

Se desejar, pode-se comentar também:

- ✅ Serializers (validation, field descriptions)
- ✅ Validators (custom validation logic)
- ✅ Signals (auto-update logic)
- ✅ Admin configs (customizações do Django admin)
- ✅ URLs (routing configuration)
- ✅ Settings (configuração geral)

---

## 💡 Benefícios

✅ **Documentação Integrada**: Comentários estão no mesmo local que o código  
✅ **Autocomplete IDE**: IDEs mostram docstrings ao passar mouse  
✅ **Documentação Automática**: Ferramentas como Sphinx podem gerar docs HTML  
✅ **Manutenção Facilitada**: Novos desenvolvedores entendem o código rapidamente  
✅ **Redução de Bugs**: Documentar força a pensar sobre edge cases  
✅ **Exemplos Práticos**: Cada docstring tem exemplos de uso  

---

## 📝 Notas

- Todos os comentários estão em **português** (mesma linguagem do projeto)
- Docstrings seguem padrão **PEP 257** com extensões de formato
- Exemplos de código incluem **casos reais de uso**
- Cada view descreve seus **filtros, respostas e permissões**
- Modelos documentam **relacionamentos, índices e otimizações**

---

**Criado em:** Janeiro 2025  
**Versão do Django:** 5.2+  
**Versão do DRF:** 3.16+
