# 📖 Guia Rápido de Navegação da Documentação

## 🎯 Comece por Aqui

Você está buscando informações sobre o código? Siga este guia:

---

## 🚀 1. Se Você Quer Entender a Arquitetura Geral

### Arquivos a Ler (na ordem):
1. **Este arquivo** (você está aqui) - 2 minutos
2. `SUMARIO_EXECUTIVO_DOCUMENTACAO.md` - 5 minutos
3. `MAPA_DOCUMENTACAO.md` - 10 minutos
4. `CODIGO_COMENTADO.md` - 15 minutos

**Tempo total:** ~30 minutos para entender tudo.

---

## 💻 2. Se Você Quer Usar a API

### Arquivos a Ler:
1. `API_CONSUMO.md` - Exemplos em cURL, JavaScript e Python

### Exemplos Rápidos:

#### Registrar novo cliente:
```bash
curl -X POST http://localhost:8000/api/accounts/registro-cliente/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "nome_completo": "João Silva",
    "password": "senha123",
    "cpf": "12345678901",
    "tipo_usuario": "cliente"
  }'
```

#### Listar prestadores:
```bash
curl http://localhost:8000/api/accounts/prestadores/?categoria=1&nota_minima=4.0
```

#### Ver mais exemplos:
- Abra `API_CONSUMO.md`

---

## 📚 3. Se Você Quer Estudar um App Específico

### **App: accounts (Autenticação)**
1. Leia: `COMENTARIOS_ACCOUNTS.md`
2. Explore: 
   - `accounts/models.py` - User, ClienteProfile, PrestadorProfile
   - `accounts/views.py` - Registro, Login, Busca, Favoritos

### **App: servicos (Categorias e Serviços)**
1. Explore:
   - `servicos/models.py` - CategoriaServico, Servico, PrestadorServicos
   - `servicos/views.py` - ViewSets com serializers dinâmicos

### **App: contratacoes (Contratos)**
1. Explore:
   - `contratacoes/models.py` - SolicitacaoContato
   - `contratacoes/views.py` - Fluxo WhatsApp

### **App: avaliacoes (Avaliações)**
1. Explore:
   - `avaliacoes/models.py` - Avaliacao (1-5 estrelas)
   - `avaliacoes/views.py` - Listar com estatísticas

### **App: portfolio (Fotos)**
1. Explore:
   - `portfolio/models.py` - PortfolioItem
   - `portfolio/views.py` - Upload e gerenciamento

---

## 🔍 4. Se Você Quer Entender um Conceito Específico

### **Geolocalização**
- `accounts/models.py` - Função `pegar_dados_endereco()` (30 linhas de docstring)
- Leia sobre o fallback chain (BrasilAPI → ViaCEP → Nominatim)

### **Cálculo de Distância**
- `accounts/views.py` - Função `calcular_distancia()` (15 linhas de docstring)
- Leia sobre Haversine formula

### **Integração WhatsApp**
- `contratacoes/views.py` - `IniciarContatoWhatsAppView` (20 linhas de docstring)
- Ver exemplos de mensagens pré-preenchidas

### **Sistema de Estatísticas**
- `avaliacoes/views.py` - `AvaliacaoListView.list()` (30 linhas de docstring)
- Cálculo de média, distribuição, porcentagem

### **Cache de Métricas**
- `accounts/models.py` - `PrestadorProfile` (campos com `_cache`)
- Leia como signals atualizam automaticamente

### **Serializers Dinâmicos**
- `servicos/views.py` - `CategoriaViewSet.get_serializer_class()` (10 linhas de docstring)
- Retorna diferentes serializers baseado em parâmetro

---

## 🛠️ 5. Se Você Quer Implementar uma Mudança

### Passo a Passo:

1. **Identifique o modelo afetado**
   - Ex: Quer mudar como prestadores são listados? → `PrestadorProfile`

2. **Leia a docstring do modelo**
   - Ex: `accounts/models.py` linha ~150

3. **Veja os exemplos de uso**
   - Cada docstring tem exemplo prático

4. **Procure a view correspondente**
   - Ex: `accounts/views.py` → `PrestadorListView`

5. **Entenda a lógica atual**
   - Leia as docstrings dos métodos
   - Veja os comentários inline

6. **Faça sua mudança seguindo o mesmo padrão**

---

## 📁 6. Estrutura de Arquivos

```
Back-End_ServicosJa_API/
├── 📋 Documentação Markdown
│   ├── API_CONSUMO.md (exemplos de uso)
│   ├── CODIGO_COMENTADO.md (visão técnica)
│   ├── COMENTARIOS_ACCOUNTS.md (app específico)
│   ├── COMENTARIOS_APPS.md (outros apps)
│   ├── README_COMENTARIOS.md (navegação)
│   ├── MAPA_DOCUMENTACAO.md (índice)
│   ├── SUMARIO_EXECUTIVO_DOCUMENTACAO.md (resumo)
│   └── GUIA_RAPIDO_NAVEGACAO.md (este arquivo)
│
├── 🐍 Código Python
│   ├── accounts/
│   │   ├── models.py ✅ (3 modelos comentados)
│   │   ├── views.py ✅ (7+ views comentadas)
│   │   └── ...
│   ├── servicos/
│   │   ├── models.py ✅ (3 modelos comentados)
│   │   ├── views.py ✅ (2 viewsets comentados)
│   │   └── ...
│   ├── contratacoes/
│   │   ├── models.py ✅ (1 modelo comentado)
│   │   ├── views.py ✅ (4 views comentadas)
│   │   └── ...
│   ├── avaliacoes/
│   │   ├── models.py ✅ (1 modelo comentado)
│   │   ├── views.py ✅ (3 views comentadas)
│   │   └── ...
│   ├── portfolio/
│   │   ├── models.py ✅ (1 modelo comentado)
│   │   ├── views.py ✅ (1 viewset comentado)
│   │   └── ...
│   └── config/
│       ├── settings.py (config comentada)
│       ├── urls.py (rotas documentadas)
│       └── ...
│
└── 🗄️ BD e Config
    └── db.sqlite3
```

---

## ⏱️ 7. Tempo de Leitura por Recurso

| Recurso | Tipo | Tempo |
|---------|------|-------|
| Este arquivo | Guia | 5 min |
| SUMARIO_EXECUTIVO_DOCUMENTACAO.md | Resumo | 10 min |
| API_CONSUMO.md | Exemplos | 15 min |
| MAPA_DOCUMENTACAO.md | Índice | 10 min |
| accounts/models.py (com comentários) | Código | 20 min |
| accounts/views.py (com comentários) | Código | 25 min |
| CODIGO_COMENTADO.md | Visão Técnica | 30 min |
| Um app inteiro (models + views) | Completo | 30-40 min |

**Total para entender tudo:** ~2-3 horas lendo tudo sequencialmente

---

## 🎓 8. Níveis de Conhecimento

### **Nível 1: Usuário da API** (30 min)
- Leia: `API_CONSUMO.md`
- Saiba: Como chamar os endpoints

### **Nível 2: Desenvolvedor (Frontend/Mobile)** (1 hora)
- Leia: `API_CONSUMO.md` + `SUMARIO_EXECUTIVO_DOCUMENTACAO.md`
- Saiba: O que cada endpoint faz, parâmetros, respostas

### **Nível 3: Desenvolvedor Backend Novo** (2 horas)
- Leia: Todos os arquivos .md + modelos + views
- Saiba: Arquitetura completa, como implementar mudanças

### **Nível 4: Mantenedor** (3+ horas)
- Leia: Tudo + código inline + execute testes
- Saiba: Tudo, pode fazer grandes refatorações

---

## 🔗  9. Fluxos Principais

### **Fluxo 1: Cliente Encontra Prestador**
1. Cliente faz login → `accounts/views.py`:`CustomTokenObtainPairView`
2. Lista prestadores → `accounts/views.py`:`PrestadorListView`
3. Visualiza detalhe → `accounts/views.py`:`PrestadorDetailView`
4. Favorita → `accounts/views.py`:`FavoritoManageView`

### **Fluxo 2: Cliente Contrata Serviço**
1. Clica "Contratar" → `contratacoes/views.py`:`IniciarContatoWhatsAppView`
2. Cria `SolicitacaoContato` → `contratacoes/models.py`
3. Abre WhatsApp com mensagem pré-preenchida
4. Conversa via WhatsApp (fora da plataforma)
5. Prestador marca concluído → `contratacoes/views.py`:`ConcluirServicoView`

### **Fluxo 3: Cliente Avalia Serviço**
1. Recebe mensagem WhatsApp com link
2. Entra na plataforma e deixa avaliação → `avaliacoes/views.py`:`CriarAvaliacaoView`
3. Avaliação é salva → `avaliacoes/models.py`:`Avaliacao`
4. Signal atualiza cache do prestador automaticamente

### **Fluxo 4: Prestador Gerencia Portfolio**
1. Faz login → `accounts/views.py`:`CustomTokenObtainPairView`
2. Adiciona fotos → `portfolio/views.py`:`PortfolioViewSet` (POST)
3. Upload vai para Cloudinary → `portfolio/models.py`:`PortfolioItem`
4. URL pública fica acessível

---

## 💡 10. Dicas de Leitura

### Ao ler código Python:
1. Comece pelo docstring da classe
2. Leia os comentários de cada campo
3. Estude os métodos (leia docstring primeiro, depois código)
4. Veja o exemplo de uso no docstring
5. Se tiver dúvida, procure em qual arquivo está usado

### Ao ler um arquivo .md:
1. Leia os títulos primeiro (overview)
2. Se interessado, leia a seção completa
3. Use Ctrl+F para buscar palavras-chave
4. Siga os links para código relacionado

### Ao ler um endpoint:
1. Leia o método HTTP (GET, POST, etc)
2. Leia a URL
3. Leia os parâmetros
4. Veja exemplo de resposta
5. Note as permissões
6. Leia os comentários do código

---

## 🚨 11. Quando Algo Não Está Claro

### Opção 1: Busque no Código
```bash
# No VS Code:
Ctrl+F: "termo para buscar"
Ctrl+Shift+F: Buscar em todos os arquivos
```

### Opção 2: Leia a Documentação
```bash
# Busque o conceito em:
- MAPA_DOCUMENTACAO.md (índice)
- CODIGO_COMENTADO.md (visão geral)
- COMENTARIOS_ACCOUNTS.md ou COMENTARIOS_APPS.md
```

### Opção 3: Use Python Help
```python
from accounts.models import User
help(User)
help(User.save)
```

### Opção 4: Procure em COMENTARIOS_*.md
```bash
# Cada app tem um arquivo .md detalhado:
- COMENTARIOS_ACCOUNTS.md
- COMENTARIOS_APPS.md (servicos, contratacoes, avaliacoes, portfolio)
```

---

## ✅ 12. Checklist para Novo Dev

Ao começar a trabalhar no projeto:

- [ ] Leia este arquivo (5 min)
- [ ] Leia SUMARIO_EXECUTIVO_DOCUMENTACAO.md (10 min)
- [ ] Leia API_CONSUMO.md (15 min)
- [ ] Configure o ambiente Django
- [ ] Rode o servidor local
- [ ] Teste alguns endpoints via cURL/Postman
- [ ] Leia MAPA_DOCUMENTACAO.md (10 min)
- [ ] Explore um app inteiro (models + views)
- [ ] Leia CODIGO_COMENTADO.md (30 min)
- [ ] Estude o código com comentários abertos
- [ ] Implemente sua primeira mudança pequena

**Tempo total:** ~2-3 horas para estar produtivo

---

## 🎯 13. Encontrando Informações Específicas

### "Como registrar um cliente?"
→ `API_CONSUMO.md` + `accounts/views.py` (ClienteRegistrationView)

### "Como funciona a geolocalização?"
→ `accounts/models.py` (pegar_dados_endereco)

### "Como contatar um prestador?"
→ `contratacoes/views.py` (IniciarContatoWhatsAppView)

### "Como avaliações são calculadas?"
→ `avaliacoes/views.py` (AvaliacaoListView.list)

### "Que filtros existem para buscar prestadores?"
→ `accounts/views.py` (PrestadorListView.get_queryset)

### "Como adicionar fotos ao portfolio?"
→ `portfolio/views.py` (PortfolioViewSet.perform_create)

### "Como funcionam os serializers dinâmicos?"
→ `servicos/views.py` (CategoriaViewSet.get_serializer_class)

---

## 📞 14. Estrutura de Suporte

```
Dúvida/Problema
├─ É sobre API?
│  └─ Veja: API_CONSUMO.md
├─ É sobre um modelo específico?
│  └─ Veja: O arquivo models.py do app (docstring da classe)
├─ É sobre uma view específica?
│  └─ Veja: O arquivo views.py do app (docstring da classe)
├─ É sobre um conceito (geoloc, stats, etc)?
│  └─ Veja: CODIGO_COMENTADO.md ou COMENTARIOS_ACCOUNTS.md
└─ Não sabe por onde começar?
   └─ Veja: MAPA_DOCUMENTACAO.md
```

---

**Criado em:** Janeiro 2025  
**Status:** ✅ Documentação Completa  
**Próximo Passo:** Comece lendo SUMARIO_EXECUTIVO_DOCUMENTACAO.md
