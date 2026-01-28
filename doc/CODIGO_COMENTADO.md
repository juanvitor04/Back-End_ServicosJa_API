# Documentação de Código - ServiçoJá API

Este documento fornece uma visão geral comentada de todos os arquivos principais do projeto.

---

## 📋 Tabela de Conteúdos

1. [Estrutura do Projeto](#estrutura-do-projeto)
2. [Arquivos de Configuração](#arquivos-de-configuração)
3. [Apps do Projeto](#apps-do-projeto)
4. [Guia de Desenvolvimento](#guia-de-desenvolvimento)

---

## Estrutura do Projeto

```
Back-End_ServicosJa_API/
├── config/                 # Configurações centrais do Django
│   ├── settings.py        # Configurações da aplicação (BD, apps, JWT, etc)
│   ├── urls.py            # Roteamento principal de URLs
│   ├── asgi.py            # Interface ASGI (async support)
│   └── wsgi.py            # Interface WSGI (production)
│
├── accounts/              # App de gerenciamento de usuários
│   ├── models.py          # Modelos: User, ClienteProfile, PrestadorProfile
│   ├── views.py           # Views REST para registro, perfil, favoritos
│   ├── serializers.py     # Serializers para validação/serialização
│   ├── urls.py            # Rotas do app
│   ├── validators.py      # Validadores customizados (CPF, CEP, etc)
│   ├── signals.py         # Sinais do Django (atualização de cache)
│   ├── admin.py           # Configuração do painel admin
│   └── migrations/        # Histórico de mudanças no BD
│
├── servicos/              # App de gerenciamento de serviços
│   ├── models.py          # Modelos: CategoriaServico, Servico
│   ├── views.py           # ViewSets para listar categorias e serviços
│   ├── serializers.py     # Serializers para categorias e serviços
│   ├── urls.py            # Rotas do app
│   ├── admin.py           # Configuração do painel admin
│   └── migrations/        # Histórico de mudanças
│
├── contratacoes/          # App de gerenciamento de contratos
│   ├── models.py          # Modelo: SolicitacaoContato
│   ├── views.py           # Views para iniciar contato, listar, concluir
│   ├── serializers.py     # Serializers para contatos
│   ├── urls.py            # Rotas do app
│   ├── admin.py           # Configuração do painel admin
│   └── migrations/        # Histórico de mudanças
│
├── avaliacoes/            # App de avaliações e reviews
│   ├── models.py          # Modelo: Avaliacao (1-5 estrelas)
│   ├── views.py           # Views para criar, listar avaliações
│   ├── serializers.py     # Serializers para avaliações
│   ├── urls.py            # Rotas do app
│   ├── admin.py           # Configuração do painel admin
│   └── migrations/        # Histórico de mudanças
│
├── portfolio/             # App de galeria de fotos
│   ├── models.py          # Modelo: PortfolioItem (fotos dos prestadores)
│   ├── views.py           # ViewSet para gerenciar fotos
│   ├── serializers.py     # Serializer para itens de portfólio
│   ├── urls.py            # Rotas do app
│   ├── admin.py           # Configuração do painel admin
│   └── migrations/        # Histórico de mudanças
│
├── manage.py              # Gerenciador de linha de comando do Django
├── requirements.txt       # Dependências Python do projeto
├── .env                   # Variáveis de ambiente (SECRET_KEY, DEBUG)
├── .gitignore             # Arquivos ignorados pelo Git
├── build.sh               # Script de build para produção (Render)
├── start.sh               # Script para iniciar a aplicação
└── README.md              # Documentação do projeto
```

---

## Arquivos de Configuração

### `config/settings.py`
**Arquivo central de configurações do Django**

```python
# Principais seções:

1. IMPORTAÇÕES E PATHS
   - Carrega variáveis do arquivo .env
   - Define o diretório base do projeto

2. SEGURANÇA
   - SECRET_KEY: Chave secreta (nunca compartilhar!)
   - DEBUG: Modo desenvolvimento (False em produção)
   - ALLOWED_HOSTS: Hosts permitidos
   - HTTPS/SSL: Configurações de segurança para produção

3. APPS INSTALADOS
   - Apps padrão do Django (admin, auth, sessions, etc)
   - Apps terceirizados (DRF, JWT, CORS, Cloudinary, etc)
   - Apps customizados (accounts, servicos, avaliacoes, etc)

4. BANCO DE DADOS
   - Suporta SQLite (desenvolvimento) e PostgreSQL (produção)
   - Usa dj_database_url para ler DATABASE_URL do ambiente

5. AUTENTICAÇÃO
   - Modelo customizado: accounts.User
   - Método: JWT (JSON Web Tokens)
   - Validadores de senha: Similaridade, comprimento mínimo, etc

6. REST FRAMEWORK (DRF)
   - Autenticação: JWT
   - Permissões: AllowAny (por padrão)
   - Paginação: 20 items por página
   - Throttling: Limite de 30 req/min (anônimos), 300 (autenticados)
   - Documentação: DRF Spectacular (OpenAPI/Swagger)

7. ARMAZENAMENTO DE MÍDIA
   - Backend padrão: Cloudinary (nuvem)
   - Estáticos: WhiteNoise com compressão
   - Upload de fotos: perfil, portfólio, ícones

8. JWT
   - Access token: Expira em 60 minutos
   - Refresh token: Expira em 1 dia

9. CORS
   - Permite requisições de qualquer origem
   - Origens confiáveis: localhost:5173 (Vite), Firebase
```

### `config/urls.py`
**Roteamento principal da API**

```python
# Rotas principais:

/admin/                                    # Painel administrativo

# Autenticação JWT
/api/auth/token/                          # Obter token (POST com username/password)
/api/auth/token/login/                    # Obter token customizado (POST com CPF/password)
/api/auth/token/refresh/                  # Renovar token expirado (POST)

# Apps
/api/accounts/                            # Usuários e perfis
/api/servicos/                            # Categorias e serviços
/api/contratacoes/                        # Solicitações de contrato
/api/avaliacoes/                          # Avaliações e reviews
/api/portfolio/                           # Galeria de fotos

# Documentação
/api/schema/                              # Schema OpenAPI (JSON)
/api/docs/                                # Swagger UI (interativo)
/api/redoc/                               # ReDoc (alternativa, melhor para ler)
```

---

## Apps do Projeto

### 1. **accounts** - Gerenciamento de Usuários

#### `models.py`
```
User (customizado)
├── Atributos básicos: email, nome_completo, cpf, dt_nascimento, genero
├── tipos: cliente ou prestador
└── Métodos: idade (calculada), get_full_name(), get_short_name()

ClienteProfile (OneToOne com User)
├── Dados de contato: telefone, CEP, endereço
├── Geolocalização: latitude, longitude (preenchidas automaticamente)
├── favoritos: ManyToMany com PrestadorProfile
└── foto_perfil: Imagem armazenada no Cloudinary

PrestadorProfile (OneToOne com User)
├── Dados profissionais: bio, telefone público, serviço
├── Endereço: CEP, rua, número, complemento, cidade, bairro, estado
├── Geolocalização: latitude, longitude (preenchidas automaticamente)
├── Disponibilidade: disponibilidade 24h, material próprio, atende fim de semana
├── Cache de avaliações: nota_media_cache, total_avaliacoes_cache
└── foto_perfil: Imagem armazenada no Cloudinary

Geolocalização:
- BrasilAPI: Primeira tentativa (mais rápida e confiável)
- Fallback: ViaCEP + Nominatim (se BrasilAPI falhar)
- Converte CEP/endereço em coordenadas (latitude, longitude)
```

#### `views.py`
```
Endpoints:

POST   /api/accounts/registro/cliente/
       Registra novo cliente com validação de dados

POST   /api/accounts/registro/prestador/
       Registra novo prestador com validação de dados

GET    /api/accounts/prestadores/
       Lista prestadores com filtros:
       - ?servico=ID
       - ?categoria=ID
       - ?disponibilidade=true
       - ?atende_fim_de_semana=true
       - ?nota_minima=4.0
       - ?ordenar_por_distancia=true (requer latitude/longitude)

GET    /api/accounts/prestadores/<id>/
       Detalhes de um prestador (público)

GET    /api/accounts/me/
       Perfil do usuário logado

PUT    /api/accounts/perfil/prestador/editar/
       Edita perfil do prestador (autenticado)

PUT    /api/accounts/perfil/cliente/editar/
       Edita perfil do cliente (autenticado)

GET/POST /api/accounts/favoritos/
         GET: Lista favoritos do cliente
         POST: Adiciona/remove prestador dos favoritos
```

#### `serializers.py`
```
Serializers de Registro:
- ClienteRegistrationSerializer: Validação de registro de cliente
- PrestadorRegistrationSerializer: Validação de registro de prestador
- CustomTokenObtainPairSerializer: Retorna dados adicionais no login

Serializers de Perfil:
- UserProfileSerializer: Visualiza/edita dados do usuário logado
- ClienteProfileEditSerializer: Edita perfil do cliente
- PrestadorProfileEditSerializer: Edita perfil do prestador

Serializers Públicos:
- PrestadorPublicoSerializer: Dados públicos do prestador (com estatísticas)
- PrestadorListSerializer: Versão simplificada para listas

Validações Customizadas:
- validar_cpf(): Valida CPF com dígito verificador
- validar_telefone(): Valida telefone 11 dígitos
- validar_cep(): Valida CEP 8 dígitos
- validar_data_nascimento(): Verifica se não é data futura
```

---

### 2. **servicos** - Categorias e Serviços

#### `models.py`
```
CategoriaServico
├── nome: Categoria (ex: "Limpeza", "Reformas")
├── descricao: Descrição breve
└── icone: Ícone da categoria

Servico
├── nome: Nome do serviço (ex: "Limpeza Residencial")
├── categoria: ForeignKey para CategoriaServico
└── descricao: Descrição do serviço

PrestadorServicos
└── Relação M2M entre Prestador e Serviço (para histórico)
```

#### `views.py`
```
CategoriaViewSet
├── GET /api/servicos/categorias/
│   Retorna lista de categorias (simples)
│
└── GET /api/servicos/categorias/?include_servicos=true
    Retorna categorias COM lista de serviços

ServicoViewSet
├── GET /api/servicos/servicos/
│   Lista todos os serviços
│
└── GET /api/servicos/servicos/<id>/
    Detalhes de um serviço específico
```

---

### 3. **contratacoes** - Gerenciamento de Contratos

#### `models.py`
```
SolicitacaoContato
├── cliente: FK para User
├── prestador: FK para User
├── servico: FK para Servico
├── data_clique: Quando foi criada
├── data_conclusao: Quando o serviço foi marcado como concluído
├── servico_realizado: Boolean (True = concluído, False = não realizado)
└── avaliacao_realizada: Property que verifica se existe Avaliacao relacionada
```

#### `views.py`
```
Endpoints:

POST /api/contratacoes/iniciar/
     Cria solicitação de contato e retorna URL de WhatsApp

GET  /api/contratacoes/prestador/solicitacoes/
     Lista solicitações recebidas pelo prestador logado

GET  /api/contratacoes/cliente/solicitacoes/
     Lista solicitações enviadas pelo cliente logado

POST /api/contratacoes/solicitacoes/<id>/concluir/
     Marca o serviço como concluído e envia mensagem WhatsApp

POST /api/contratacoes/solicitacoes/<id>/nao-realizado/
     Marca o serviço como não realizado
```

---

### 4. **avaliacoes** - Sistema de Reviews

#### `models.py`
```
Avaliacao
├── solicitacao_contato: OneToOne (garantir uma avaliação por contato)
├── nota: Integer 1-5 (com validadores)
├── comentario: TextField opcional
├── data_criacao: Auto preenchido
└── data_atualizacao: Auto atualizado
```

#### `views.py`
```
Endpoints:

POST /api/avaliacoes/
     Cria avaliação (apenas cliente que contratou pode avaliar)

GET  /api/avaliacoes/listar/
     Lista avaliações com filtros:
     - ?prestador=ID
     - ?nota_minima=4
     - ?minhas=true (avaliações do usuário logado)
     - ?ordenar=maior_nota
     
     Retorna estatísticas:
     - média de notas
     - total de avaliações
     - distribuição por estrelas

GET  /api/avaliacoes/<id>/
     Detalhes de uma avaliação específica
```

#### Signals
```
atualizar_cache_avaliacao()
├── Dispara quando: Avaliacao é criada ou deletada
├── Atualiza em PrestadorProfile:
│   ├── nota_media_cache: Média das notas
│   ├── total_avaliacoes_cache: Total de avaliações
│   └── total_servicos_cache: Usado para cálculos
└── Propósito: Manter cache atualizado para performance
```

---

### 5. **portfolio** - Galeria de Fotos

#### `models.py`
```
PortfolioItem
├── prestador: FK para PrestadorProfile
├── imagem: ImageField armazenado em Cloudinary
├── descricao: CharField com texto do projeto
└── created_at: Data de criação
```

#### `views.py`
```
Endpoints:

GET    /api/portfolio/itens/
       Lista itens do portfólio (de todos os prestadores)

POST   /api/portfolio/itens/
       Cria novo item (apenas prestador logado)
       Anexa automaticamente ao perfil do prestador

PUT    /api/portfolio/itens/<id>/
       Edita item (apenas proprietário)

DELETE /api/portfolio/itens/<id>/
       Deleta item (apenas proprietário)
```

---

## Fluxos Principais de Dados

### 1. Registro de Prestador
```
POST /api/accounts/registro/prestador/
├── Validação: CPF, telefone, CEP, datas
├── Criação: User (tipo='prestador')
├── Criação: PrestadorProfile com dados de endereço
├── Geolocalização: Preenche latitude/longitude automaticamente
└── Resposta: Tokens JWT (access + refresh), user_id, profile_id
```

### 2. Busca de Prestadores
```
GET /api/accounts/prestadores/?servico=1&ordenar_por_distancia=true
├── Aplicar filtros (serviço, categoria, disponibilidade, nota)
├── Calcular distância cliente-prestador (Haversine formula)
├── Ordenar por distância (se solicitado)
├── Retornar com dados públicos (sem telefone se não autenticado)
└── Paginar (20 por página por padrão)
```

### 3. Iniciar Contato
```
POST /api/contratacoes/iniciar/ (com token JWT)
├── Validar: Cliente pode contatar prestador?
├── Criar: SolicitacaoContato
├── Gerar: URL de WhatsApp pré-preenchida
└── Resposta: whatsapp_url (redireciona para WhatsApp)
```

### 4. Avaliar Prestador
```
POST /api/avaliacoes/ (com token JWT)
├── Validar: SolicitacaoContato pertence ao cliente?
├── Validar: Serviço foi marcado como concluído?
├── Validar: Avaliação já não existe?
├── Criar: Avaliacao com nota e comentário
├── Signal: Atualiza cache em PrestadorProfile
└── Resposta: ID da avaliação criada
```

---

## Segurança e Boas Práticas

### Autenticação JWT
```
Flow:
1. POST /api/auth/token/login/ com CPF e senha
2. Receber: access_token (60 min) + refresh_token (1 dia)
3. Incluir: Authorization: Bearer <access_token> em requests
4. Expirada? POST /api/auth/token/refresh/ com refresh_token
5. Receber: novo access_token
```

### Validações Importantes
```
- CPF: Validação com dígito verificador
- Telefone: 11 dígitos brasileiros
- CEP: 8 dígitos
- Senha: Mínimo 8 caracteres, não repetida
- Data: Não pode ser no futuro
```

### Proteção de Dados
```
- Telefone pública do prestador:
  - Visível apenas para clientes autenticados
  - Oculto para usuários anônimos

- Senhas:
  - Hash com PBKDF2 (padrão Django)
  - Nunca transmitir em texto plano

- Mídia:
  - Armazenada em Cloudinary (nuvem)
  - URLs com token de acesso

- CORS:
  - Apenas origens confiáveis podem fazer requisições
```

---

## Deployment (Render.yaml)

```yaml
Banco de Dados:
- PostgreSQL (free tier)
- Database: servicosja_db_7ohi
- User: servicosja_db_7ohi_user
- Region: Oregon

Aplicação:
- Service: servicosja-api
- Linguagem: Python 3.11.9
- Build: ./build.sh (pip install, collectstatic, migrate)
- Start: ./start.sh (migrate, create superuser, gunicorn)

Variáveis de Ambiente:
- DATABASE_URL: Fornecido automaticamente
- SECRET_KEY: Gerado automaticamente
- DEBUG: false
- CLOUDINARY_*: Fornecido externamente
```

---

## Extensões Futuras

1. **Notificações em Tempo Real**: WebSockets com Django Channels
2. **Pagamentos**: Integração com Stripe ou PagSeguro
3. **Chat**: Sistema de mensagens entre cliente e prestador
4. **Avaliações de Clientes**: Prestadores também avaliarem clientes
5. **Histórico de Atividades**: Log de todas as ações
6. **Sistema de Badges**: Prestadores ganharem badges por desempenho
7. **Busca Avançada**: ElasticSearch para buscas mais eficientes

---

## Contato e Suporte

- **Repositório**: [Link do GitHub]
- **Documentação API**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Desenvolvedor**: [Nome do desenvolvedor]
- **Projeto**: Integrador SENAC - ServiçoJá
