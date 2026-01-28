# COMENTÁRIOS DETALHADOS - ACCOUNTS APP
# Arquivo de referência com explicações sobre models.py, views.py e serializers.py

## ============================================================================
## MODELS (accounts/models.py)
## ============================================================================

### User (Modelo Customizado)
```python
# Estende o AbstractUser padrão do Django com campos customizados

Atributos:
- email: Usado como USERNAME_FIELD (login por email, não por username)
- nome_completo: Nome completo do usuário
- cpf: CPF único (validado com dígito verificador)
- dt_nascimento: Data de nascimento (permite calcular idade)
- genero: Escolha entre 6 opções (M, F, T, N, O, P)
- tipo_usuario: 'cliente' ou 'prestador'
- idade: Property que calcula a idade dinamicamente

Métodos:
- get_full_name(): Retorna nome_completo
- get_short_name(): Retorna primeiro nome
- clean(): Valida se usuário não é cliente E prestador simultaneamente

Validações:
- CPF com dígito verificador (não aceita CPFs inválidos)
- Email único
- CPF único
```

### ClienteProfile (OneToOne com User)
```python
# Perfil específico de clientes

Atributos:
- user: OneToOneField (cada User cliente tem exatamente um ClienteProfile)
- telefone_contato: Telefone do cliente (11 dígitos)
- cep, rua, numero_casa, complemento: Dados de endereço
- cidade, bairro, estado: Preenchidos automaticamente via geolocalização
- latitude, longitude: Coordenadas (calculadas automaticamente)
- favoritos: ManyToManyField para PrestadorProfile (prestadores favoritados)
- foto_perfil: Imagem armazenada em Cloudinary
- created_at, updated_at: Timestamps

Método save():
- Detecta mudanças de endereço
- Chama pegar_dados_endereco() para geolocalizar
- Sanitiza telefone (remove caracteres não-numéricos)
- Executa validações completas
```

### PrestadorProfile (OneToOne com User)
```python
# Perfil específico de prestadores

Atributos:
- user: OneToOneField
- biografia: Descrição profissional
- telefone_publico: Telefone visível apenas para clientes autenticados
- cep, rua, numero_casa, complemento: Dados de endereço
- cidade, bairro, estado: Preenchidos automaticamente
- latitude, longitude: Coordenadas para busca por proximidade
- disponibilidade: 24h?
- possui_material_proprio: Fornece material?
- atende_fim_de_semana: Trabalha sábados/domingos?
- foto_perfil: Imagem em Cloudinary
- nota_media_cache: Média de notas das avaliações (cache para performance)
- total_avaliacoes_cache: Total de avaliações recebidas
- total_servicos_cache: Total de serviços realizados
- acessos_perfil: Número de vezes que o perfil foi visualizado
- servicos_nao_realizados_cache: Contador de serviços não realizados
- servico: ForeignKey para o tipo de serviço principal

Índices de BD:
- idx_cep: Otimiza buscas por CEP
- idx_geo: Otimiza buscas por latitude/longitude (proximidade)

Método save():
- Auto-localiza via BrasilAPI → ViaCEP + Nominatim
- Sanitiza telefone
- Executa validações completas

Funções Auxiliares:
- pegar_dados_endereco(): Obtém coordenadas a partir de CEP
  - Fallback de APIs: BrasilAPI → ViaCEP → Nominatim
  - Converte CEP/endereço em latitude/longitude
  - Preenche cidade, bairro, estado
```

## ============================================================================
## SERIALIZERS (accounts/serializers.py)
## ============================================================================

### ClienteRegistrationSerializer
```python
# Serializa dados de registro de novo cliente

Campos de Entrada:
- email, nome_completo, dt_nascimento, genero, cpf, password
- telefone_contato, cep, rua, numero_casa
- password2: Confirmação de senha

Validações:
- CPF: Dígito verificador correto
- Telefone: 11 dígitos
- CEP: 8 dígitos
- Data: Não pode ser no futuro
- Senha: Deve ter mínimo 8 caracteres e ser diferente de password2

Processo de Criação:
1. Validar todos os campos
2. Criar User com tipo_usuario='cliente'
3. Criar ClienteProfile associado
4. Retornar tokens JWT (access + refresh)
```

### PrestadorRegistrationSerializer
```python
# Serializa dados de registro de novo prestador

Campos Adicionais:
- telefone_publico, disponibilidade, possui_material_proprio, atende_fim_de_semana
- categoria, servico (ForeignKey para CategoriaServico e Servico)

Validações Extras:
- Verifica se serviço pertence à categoria selecionada

Processo de Criação:
1. Validar todos os campos
2. Criar User com tipo_usuario='prestador'
3. Criar PrestadorProfile com dados profissionais
4. Auto-localizar endereço (BrasilAPI)
5. Retornar tokens JWT + profile_id
```

### CustomTokenObtainPairSerializer
```python
# Customiza resposta do JWT login

Campos de Entrada:
- cpf: CPF do usuário (customizado, geralmente username)
- password: Senha

Campos de Resposta Extras:
- user_id: ID do usuário
- nome: Nome completo
- email: Email
- tipo_usuario: 'cliente' ou 'prestador'
- profile_id: ID do ClienteProfile ou PrestadorProfile
```

### PrestadorPublicoSerializer
```python
# Dados públicos de um prestador (sem informações sensíveis)

Campos:
- id, nome, foto, biografia
- servico (nome do serviço)
- categoria (nome da categoria)
- telefone_publico (oculto se não autenticado)
- cidade, bairro, estado
- nota_media, total_avaliacoes
- portfolio (últimas fotos)
- estatísticas (distribuição de notas)
- ultimas_avaliacoes (últimas 5 avaliaçõ)

Método to_representation():
- Remove telefone_publico se usuário não é cliente autenticado
```

### UserProfileSerializer
```python
# Serializa dados do usuário logado (/me/)

Permite Visualizar/Editar:
- Dados pessoais: nome, email, data de nascimento, gênero
- Perfil específico (aninhado):
  - ClienteProfile: telefone, endereço, favoritos
  - PrestadorProfile: biografia, serviço, disponibilidade

Validações:
- Lê todos os campos
- Escreve apenas em alguns campos
- Data em formato brasileiro (dd/mm/yyyy)
```

## ============================================================================
## VIEWS (accounts/views.py)
## ============================================================================

### ClienteRegistrationView
```python
# POST /api/accounts/registro/cliente/

Processo:
1. Validar serializer (todos os campos obrigatórios)
2. Se válido, criar usuário e profile
3. Gerar tokens JWT automaticamente
4. Retornar: access, refresh, user_id

Resposta (201 Created):
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "user_id": 1,
  "email": "cliente@example.com",
  ...
}
```

### PrestadorRegistrationView
```python
# POST /api/accounts/registro/prestador/

Idem ClienteRegistrationView, mas:
- Valida dados profissionais adicionais
- Auto-localiza endereço
- Retorna também profile_id
```

### CustomTokenObtainPairView
```python
# POST /api/auth/token/login/

Customização do TokenObtainPairView padrão:
- Aceita CPF ao invés de username
- Retorna dados adicionais no token

Entrada:
{
  "cpf": "12345678901",
  "password": "senha123"
}

Resposta:
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "user_id": 1,
  "tipo_usuario": "prestador",
  ...
}
```

### PrestadorListView
```python
# GET /api/accounts/prestadores/

Filtros Disponíveis:
- ?servico=1: Filtra por ID de serviço
- ?categoria=1: Filtra por ID de categoria
- ?disponibilidade=true: Apenas prestadores 24h
- ?atende_fim_de_semana=true
- ?possui_material_proprio=true
- ?nota_minima=4.5: Apenas top-rated
- ?nome=Maria: Busca por nome
- ?nome_servico=Limpeza: Busca por tipo de serviço
- ?latitude=X&longitude=Y: Coordenadas do cliente
- ?ordenar_por_distancia=true: Ordena por proximidade

Funcionalidade de Distância:
- Calcula distância usando Fórmula de Haversine
- Requer latitude/longitude do cliente
- Tira automaticamente do perfil se cliente autenticado
- Ordena lista por proximidade

Retorna (paginado):
[
  {
    "id": 1,
    "nome": "Maria",
    "nota_media": 4.8,
    "distancia": 2.5,  # km
    "portfolio": [...],
    ...
  }
]
```

### PrestadorDetailView
```python
# GET /api/accounts/prestadores/<id>/

Retorna dados públicos detalhados do prestador:
- Perfil completo
- Estatísticas de avaliações
- Últimas avaliações
- Galeria de portfólio
```

### PrestadorProfileEditView
```python
# GET/PUT /api/accounts/perfil/prestador/editar/

Apenas para prestador logado (IsAuthenticated)

Campos editáveis:
- foto_perfil: Upload de foto
- biografia: Descrição profissional

GET: Retorna perfil atual
PUT: Atualiza perfil
```

### ClienteProfileEditView
```python
# GET/PUT /api/accounts/perfil/cliente/editar/

Campos editáveis:
- foto_perfil
- telefone_contato
- cep, rua, numero_casa
- complemento, cidade, bairro, estado

Validações:
- Telefone: 11 dígitos
- CEP: 8 dígitos

Auto-atualização:
- Detecta mudança de CEP
- Re-localiza automaticamente (BrasilAPI)
- Preenche cidade, bairro, estado
```

### UserProfileView
```python
# GET/PUT /api/accounts/me/

Retorna/edita perfil do usuário logado

GET: Dados completos do usuário e seu perfil
PUT: Edita dados do usuário e seu perfil específico

Remove automaticamente:
- perfil_prestador se é cliente
- perfil_cliente se é prestador
```

### FavoritoManageView
```python
# GET: Lista favoritos do cliente
# POST: Adiciona ou remove prestador dos favoritos

GET /api/accounts/favoritos/
  Retorna lista de PrestadorProfile favoritados

POST /api/accounts/favoritos/
  Entrada: { "prestador_id": 1 }
  
  Se já é favoritado: Remove
  Se não é favoritado: Adiciona
  
  Resposta:
  {
    "detail": "Prestador adicionado aos favoritos.",
    "favoritado": true
  }
```

## ============================================================================
## SIGNALS (accounts/signals.py)
## ============================================================================

### atualizar_cache_avaliacao()
```python
# Signal que atualiza cache de avaliações automaticamente

Dispara Quando:
- Uma Avaliacao é criada (post_save)
- Uma Avaliacao é deletada (post_delete)

Ação:
1. Obtém o prestador da avaliação
2. Calcula a nova média de notas
3. Conta total de avaliações
4. Atualiza cache em PrestadorProfile:
   - nota_media_cache
   - total_avaliacoes_cache
   - total_servicos_cache

Propósito:
- Melhorar performance (não precisa calcular a cada requisição)
- Manter dados sempre atualizados
```

## ============================================================================
## VALIDADORES (accounts/validators.py)
## ============================================================================

### validar_cpf()
```python
# Valida CPF com dígito verificador (algoritmo oficial)

Etapas:
1. Remove caracteres não-numéricos
2. Verifica se tem 11 dígitos
3. Calcula primeiro dígito verificador
4. Calcula segundo dígito verificador
5. Compara com os dígitos fornecidos

Levanta ValidationError se inválido
```

### validar_telefone()
```python
# Valida telefone brasileiro (11 dígitos)

Etapas:
1. Remove caracteres não-numéricos
2. Verifica se tem 11 dígitos (DDD 2 + número 9)

Formato esperado: (XX) 9XXXX-XXXX
Aceito como: 11987654321 ou 11 9 8765-4321
```

### validar_cep()
```python
# Valida CEP brasileiro (8 dígitos)

Etapas:
1. Remove caracteres não-numéricos
2. Verifica se tem 8 dígitos

Formato esperado: XXXXX-XXX
Aceito como: 01310100 ou 01310-100
```

### validar_data_nascimento()
```python
# Valida data de nascimento

Validações:
1. Verifica se não é data futura
2. Levanta erro se for

Útil para evitar datas inválidas
```
