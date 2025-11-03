# 📚 E-commerce de Livros com Recomendação Inteligente

Sistema de e-commerce especializado em livros com motor de recomendação baseado em inteligência artificial. Arquitetura de microsserviços com **FastAPI** no backend e **React + TypeScript** no frontend.

---

## 🏗️ Arquitetura de Microsserviços

```
                        ┌─────────────┐
                        │  Frontend   │
                        │ React/Vite  │
                        │ :3000       │
                        └──────┬──────┘
                               │ HTTP
                    ┌──────────▼──────────┐
                    │   API Gateway       │
                    │   FastAPI :8000     │
                    └──┬─┬─┬─┬─┬─┬─┬──────┘
        ┌───────────────┘ │ │ │ │ │ └──────────┐
        │                 │ │ │ │ │            │
   ┌────▼────┐ ┌─────┬────▼─┐ │ │ ┌──────┬───▼────┐
   │ Catalog │ │Auth │Users │ │ │ │Recomm│Shipping│
   │:8001    │ │:8002│:8003 │ │ │ │:8007 │:8008   │
   └─────────┘ └─────┴──────┘ │ │ └──────┴────────┘
                       ┌───────▼─▼─────┬──────┐
                       │  Cart │Orders │Payment
                       │:8004  │:8005  │:8006
                       └───────────────┴──────┘
                              │
                  ┌───────────┼──────────┐
                  ▼           ▼          ▼
            PostgreSQL    Redis    Elasticsearch
              :5432       :6379        :9200
```

### 🔧 Serviços Disponíveis

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **API Gateway** | 8000 | Orquestração e roteamento |
| **Catalog** | 8001 | Gestão de livros e categorias |
| **Auth** | 8002 | Autenticação JWT |
| **Users** | 8003 | Perfil e gestão de usuários |
| **Cart** | 8004 | Carrinho de compras |
| **Orders** | 8005 | Gestão de pedidos |
| **Payment** | 8006 | Processamento de pagamentos |
| **Recommendation** | 8007 | Sistema de recomendações |
| **Shipping** | 8008 | Serviço de envios |
| **Celery Worker** | - | Processamento assíncrono |
| **Celery Beat** | - | Agendador de tarefas |

---

## 📁 Estrutura do Projeto

```
.
├── core/                          # Configurações compartilhadas
│   ├── config.py                 # Variáveis de ambiente
│   ├── database.py               # Conexão com DB
│   ├── security.py               # JWT e autenticação
│   └── dependencies.py           # Dependências injetáveis
├── models/                        # Modelos SQLAlchemy
│   ├── book.py
│   ├── user.py
│   ├── order.py
│   └── ...
├── schemas/                       # Schemas Pydantic (validação)
│   ├── book.py
│   ├── user.py
│   └── ...
├── ml/                           # Machine Learning
│   ├── content_based.py          # Recomendação por conteúdo
│   ├── collaborative_filtering.py # Filtragem colaborativa
│   ├── hybrid_recommender.py     # Sistema híbrido
│   └── model_trainer.py          # Treinamento
├── services/                      # Microsserviços
│   ├── api-gateway/              # Gateway (porta 8000)
│   ├── catalog-service/          # Livros (porta 8001)
│   ├── auth-service/             # Autenticação (porta 8002)
│   ├── users-service/            # Usuários (porta 8003)
│   ├── cart-service/             # Carrinho (porta 8004)
│   ├── orders-service/           # Pedidos (porta 8005)
│   ├── payment-service/          # Pagamentos (porta 8006)
│   ├── recommendation-service/   # Recomendações (porta 8007)
│   └── shipping-service/         # Envios (porta 8008)
├── frontend/                      # React + TypeScript
│   ├── src/
│   │   ├── components/           # Componentes React
│   │   ├── pages/                # Páginas
│   │   ├── services/             # Chamadas API
│   │   └── stores/               # Estado (Zustand)
│   └── package.json
├── docker-compose.yml            # Orquestração
└── requirements.txt              # Dependências Python
```
---

## 🚀 Quick Start (5 minutos)

### Prerequisites
- **Docker** e **Docker Compose**
- **Node.js 18+** (para frontend local)

### 1️⃣ Clone e inicie os serviços
```bash
git clone <repository-url>
cd ecommerce-recommendation-system
docker compose up -d
```

### 2️⃣ Popule o banco de dados
```bash
docker compose exec catalog-service python import_csv_only.py
```

### 3️⃣ Inicie o frontend
```bash
cd frontend
npm install
npm run dev
```

### 4️⃣ Acesse
- **App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## 📦 Stack Utilizado

### Backend
| Tecnologia | Função |
|-----------|--------|
| **FastAPI** | Framework web principal |
| **Python 3.11+** | Linguagem |
| **SQLAlchemy** | ORM para banco de dados |
| **Pydantic** | Validação de dados |
| **Redis** | Cache e sessões |
| **Elasticsearch** | Busca avançada |
| **Celery** | Tasks assíncronas |
| **scikit-learn** | Machine Learning |

### Frontend
| Tecnologia | Função |
|-----------|--------|
| **React 18** | Framework UI |
| **TypeScript** | Tipagem estática |
| **Vite** | Build tool |
| **Tailwind CSS** | Estilização |
| **Zustand** | State management |

### Infraestrutura
| Serviço | Versão | Porta |
|--------|--------|------|
| **PostgreSQL** | 15 | 5432 |
| **Redis** | 7 | 6379 |
| **Elasticsearch** | 8 | 9200 |

---

## ✅ Funcionalidades Implementadas

### Autenticação & Usuários
- ✅ Registro e login com JWT
- ✅ Perfil de usuário
- ✅ Roles (admin, user)
- ✅ Atualização de dados

### Catálogo
- ✅ CRUD de livros
- ✅ Categorias
- ✅ Busca com Elasticsearch
- ✅ Filtros (preço, categoria, autor)
- ✅ Livros populares

### Carrinho e Pedidos
- ✅ Adicionar/remover itens do carrinho
- ✅ Atualizar quantidades
- ✅ Criar pedidos
- ✅ Histórico de pedidos
- ✅ Status de pedido

### Recomendações
- ✅ Filtragem baseada em conteúdo
- ✅ Filtragem colaborativa
- ✅ Sistema híbrido (combinado)
- ✅ Recomendações personalizadas
- ✅ Livros similares
- ✅ Livros em alta (trending)

### Frontend
- ✅ Interface responsiva
- ✅ Catálogo com filtros
- ✅ Detalhes do produto
- ✅ Carrinho de compras
- ✅ Checkout
- ✅ Autenticação
- ✅ Painel de usuário

---

## 🔄 Implementações Futuras

- 🔲 Notificações por email
- 🔲 Upload de imagens (AWS S3)
- 🔲 Sistema de avaliações completo
- 🔲 Cupons de desconto
- 🔲 Integração com gateway de pagamento real
- 🔲 Dashboard administrativo
- 🔲 Analytics e relatórios
- 🔲 Wishlist/favoritos
- 🔲 Integração com redes sociais

---

## 🛠️ Instalação & Configuração

### Opção 1: Docker Compose (Recomendado) ⭐

#### Iniciar todos os serviços
```bash
docker compose up -d
```

#### Verificar status
```bash
docker compose ps
```

#### Importar dados de exemplo
```bash
docker compose exec catalog-service python import_csv_only.py
```

#### Visualizar logs
```bash
# Todos os serviços
docker compose logs -f

# Serviço específico
docker compose logs -f api-gateway
```

### Opção 2: Execução Local (sem Docker)

#### Pré-requisitos
```bash
# Instale PostgreSQL, Redis e Elasticsearch
# Ou use Homebrew/package manager da sua plataforma

# macOS
brew install postgresql redis elasticsearch

# Inicie os serviços
brew services start postgresql
brew services start redis
# elasticsearch: siga as instruções do site
```

#### Instale dependências
```bash
pip install -r requirements.txt
cd frontend && npm install
```

#### Configure variáveis de ambiente
```bash
cp env.example .env
# Edite .env com suas configurações
```

#### Inicie cada serviço (em terminais separados)
```bash
# Terminal 1: API Gateway
cd services/api-gateway && uvicorn api_gateway:app --reload --port 8000

# Terminal 2: Catalog Service
cd services/catalog-service && uvicorn catalog_service:app --reload --port 8001

# Terminal 3: Auth Service
cd services/auth-service && uvicorn auth_service:app --reload --port 8002

# Terminal 4: Frontend
cd frontend && npm run dev
```

---

## 🎯 Endpoints Principais

### Autenticação
```
POST   /api/v1/auth/register    # Criar conta
POST   /api/v1/auth/login       # Login
GET    /api/v1/auth/me          # Perfil atual
POST   /api/v1/auth/logout      # Logout
```

### Livros
```
GET    /api/v1/books            # Listar com filtros
GET    /api/v1/books/{id}       # Detalhes
GET    /api/v1/books/popular    # Livros populares
POST   /api/v1/books            # Criar (admin)
PUT    /api/v1/books/{id}       # Atualizar (admin)
DELETE /api/v1/books/{id}       # Deletar (admin)
```

### Carrinho
```
GET    /api/v1/cart             # Obter carrinho
POST   /api/v1/cart/items       # Adicionar item
PUT    /api/v1/cart/items/{id}  # Atualizar
DELETE /api/v1/cart/items/{id}  # Remover
```

### Pedidos
```
POST   /api/v1/orders           # Criar pedido
GET    /api/v1/orders           # Meus pedidos
GET    /api/v1/orders/{id}      # Detalhes
```

### Recomendações
```
GET    /api/v1/recommendations/for-you          # Personalizadas
GET    /api/v1/recommendations/trending         # Em alta
GET    /api/v1/recommendations/books/{id}/similar # Similares
```

**Documentação completa**: http://localhost:8000/docs

---

## 📊 Sistema de Recomendação

### Filtragem Baseada em Conteúdo
Recomenda livros similares baseado em:
- Categoria/Gênero
- Autor
- Descrição (TF-IDF)
- Atributos do livro

### Filtragem Colaborativa
Combina:
- User-based: usuários similares compraram livros similares
- Item-based: livros frequentemente comprados juntos
- Algoritmo: SVD + KNN

### Sistema Híbrido
Combina as duas abordagens com pesos dinâmicos baseados em:
- Quantidade de dados disponível
- Contexto do usuário (cold-start vs ativo)
- Performance histórica

#### Treinar modelo
```bash
# Com Docker
docker compose exec recommendation-service python -m ml.model_trainer

# Localmente
python -m ml.model_trainer
```

---

## 🛠️ Comandos Úteis

### Docker Compose
```bash
# Iniciar
docker compose up -d

# Parar
docker compose down

# Parar e remover dados
docker compose down -v

# Ver logs
docker compose logs -f service-name

# Executar comando
docker compose exec service-name command

# Reconstruir
docker compose up --build
```

### Banco de Dados
```bash
# Acessar PostgreSQL
docker compose exec postgres psql -U user -d bookstore

# Ver quantos livros importados
docker compose exec postgres psql -U user -d bookstore -c "SELECT COUNT(*) FROM books;"

# Migrations
docker compose exec catalog-service alembic upgrade head
```

### Importar Dados
```bash
docker compose exec catalog-service python import_csv_only.py
```

---

## 🐛 Solução de Problemas

### Serviços não iniciam
```bash
# Verifique logs
docker compose logs postgres
docker compose logs api-gateway

# Verifique status
docker compose ps

# Reinicie tudo
docker compose down && docker compose up -d
```

### Frontend não conecta à API
```bash
# Verifique se API está rodando
curl http://localhost:8000/health

# Verifique logs do gateway
docker compose logs api-gateway

# Verifique CORS no navegador (console)
```

### Banco de dados vazio
```bash
# Importe os dados
docker compose exec catalog-service python import_csv_only.py

# Verifique importação
docker compose exec postgres psql -U user -d bookstore -c "SELECT COUNT(*) FROM books;"
```

### Recomendações não funcionam
```bash
# Treine o modelo
docker compose exec recommendation-service python -m ml.model_trainer

# Verifique se há livros
docker compose exec postgres psql -U user -d bookstore -c "SELECT COUNT(*) FROM books;"
```

---

## 📚 Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Saúde da API**: http://localhost:8000/health

---

## 🤝 Como Contribuir

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/sua-feature`)
3. Implemente a feature
4. Commit (`git commit -m 'Add feature'`)
5. Push (`git push origin feature/sua-feature`)
6. Abra um Pull Request

---

## 📄 Licença

MIT License - veja `LICENSE` para detalhes

---
