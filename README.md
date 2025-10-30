# Bookstore - E-commerce de Livros com Sistema de Recomendação

Sistema completo de e-commerce especializado em livros com motor de recomendação inteligente, utilizando Python/FastAPI no backend e React com TypeScript no frontend.

## 🚀 Características

### Backend (FastAPI)
- **Framework**: FastAPI com Python 3.11+
- **Banco de Dados**: PostgreSQL 15+ com SQLAlchemy 2.0
- **Cache**: Redis 7+ para cache e sessões
- **Busca**: Elasticsearch 8+ para busca avançada
- **Autenticação**: JWT com refresh tokens
- **ML/Recomendação**: scikit-learn, pandas, numpy
- **Task Queue**: Celery + Redis para processamento assíncrono

### Frontend (React + TypeScript)
- **Framework**: React 18+ com TypeScript
- **Build Tool**: Vite
- **Estado**: Zustand para gerenciamento de estado
- **Roteamento**: React Router v6
- **UI Components**: shadcn/ui + Tailwind CSS
- **Formulários**: React Hook Form + Zod
- **HTTP Client**: Axios

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│              React + TypeScript                  │
│                    (Vite)                        │
│                  Porta 3000                      │
└────────────────┬────────────────────────────────┘
                 │ HTTP/REST
                 │
┌────────────────▼────────────────────────────────┐
│                  API Gateway                     │
│              FastAPI (Python)                    │
│              - Rotas REST                        │
│              - Autenticação JWT                  │
│              - Validação Pydantic                │
│              Porta 8000                          │
└─────┬─────────┬──────────┬─────────┬────────────┘
      │         │          │         │
      │         │          │         │
┌─────▼───┐ ┌──▼─────┐ ┌──▼────┐ ┌──▼──────────┐
│ Books   │ │ Users  │ │Orders │ │Recommendations│
│ Service │ │Service │ │Service│ │   Service     │
└─────┬───┘ └──┬─────┘ └──┬────┘ └──┬──────────┘
      │        │          │         │
      │        │          │         │
      └────────┴──────────┴─────────┘
                    │
      ┌─────────────┼─────────────────┐
      │             │                 │
┌─────▼────┐  ┌─────▼─────┐   ┌──────▼──────┐
│PostgreSQL│  │   Redis   │   │Elasticsearch│
│  5432    │  │   6379    │   │    9200     │
└──────────┘  └───────────┘   └─────────────┘
```

## 🎯 Funcionalidades

### ✅ Implementadas
- [x] Sistema de autenticação JWT
- [x] CRUD de livros e categorias
- [x] Sistema de busca avançada com Elasticsearch
- [x] Carrinho de compras
- [x] Sistema de pedidos
- [x] Sistema de recomendação híbrido (Content-Based + Collaborative Filtering)
- [x] Interface responsiva
- [x] Painel administrativo
- [x] Sistema de reviews (endpoints implementados)

### 🔄 Em Desenvolvimento
- [ ] Implementação completa do serviço de reviews
- [ ] Integração com gateway de pagamento
- [ ] Sistema de notificações por email
- [ ] Upload de imagens
- [ ] Sistema de cupons de desconto

## 🛠️ Instalação e Configuração

### Pré-requisitos
- **Docker** e **Docker Compose** (recomendado)
- **Python 3.11+** (se rodar backend localmente)
- **Node.js 18+** (se rodar frontend localmente)
- **PostgreSQL 15+** (se rodar localmente)
- **Redis 7+** (se rodar localmente)
- **Elasticsearch 8+** (se rodar localmente)

## 🚀 Como Rodar o Projeto

### Opção 1: Usando Docker Compose (Recomendado)

#### 1. Clone o repositório
```bash
git clone <repository-url>
cd ecommerce-recommendation-system
```

#### 2. Configure as variáveis de ambiente
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações se necessário
```

#### 3. Inicie os serviços de infraestrutura
```bash
docker-compose up -d postgres redis elasticsearch
```

Aguarde alguns segundos até que os serviços estejam saudáveis.

#### 4. Execute as migrations do banco de dados
```bash
docker-compose exec backend alembic upgrade head
```

#### 5. Popule os dados iniciais (livros)
```bash
docker-compose run --rm backend python import_csv_only.py
```

#### 6. Inicie todos os serviços (backend, celery, etc.)
```bash
docker-compose up -d
```

#### 7. Treine o modelo de recomendação (opcional, mas recomendado)
```bash
docker-compose exec backend python -m ml.model_trainer
```

#### 8. Inicie o frontend
```bash
cd frontend
npm install
npm run dev
```

### Opção 2: Execução Local (sem Docker)

#### Backend

1. **Instale as dependências**
```bash
pip install -r requirements.txt
```

2. **Configure as variáveis de ambiente**
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Certifique-se de que PostgreSQL, Redis e Elasticsearch estão rodando**

4. **Execute as migrations**
```bash
alembic upgrade head
```

5. **Inicie o servidor**
```bash
uvicorn main:app --reload --port 8000
```

6. **Em outro terminal, inicie o Celery worker**
```bash
celery -A tasks.celery_app worker --loglevel=info
```

7. **Em outro terminal, inicie o Celery beat**
```bash
celery -A tasks.celery_app beat --loglevel=info
```

#### Frontend

1. **Navegue para o diretório do frontend**
```bash
cd frontend
```

2. **Instale as dependências**
```bash
npm install
```

3. **Configure as variáveis de ambiente** (se necessário)
```bash
# Crie um arquivo .env no diretório frontend se necessário
# VITE_API_BASE_URL=http://localhost:8000/api/v1
```

4. **Inicie o servidor de desenvolvimento**
```bash
npm run dev
```

## 📊 Acessos

Após iniciar o projeto, você pode acessar:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 Sistema de Recomendação

O sistema implementa três abordagens de recomendação:

### 1. Filtragem Baseada em Conteúdo
- Similaridade entre livros baseada em:
  - Categoria/gênero
  - Autor
  - Tags e palavras-chave
  - Descrição (TF-IDF)
- Algoritmo: Cosine Similarity

### 2. Filtragem Colaborativa
- **User-based**: usuários similares compraram livros similares
- **Item-based**: livros comprados juntos frequentemente
- Algoritmo: Matrix Factorization (SVD) + KNN

### 3. Sistema Híbrido
- Combina scores de ambas abordagens
- Peso ajustável baseado em:
  - Quantidade de dados do usuário
  - Performance histórica
  - Contexto (cold start vs usuário ativo)

### Treinamento do Modelo

Para treinar o modelo de recomendação:

```bash
# Com Docker
docker-compose exec backend python -m ml.model_trainer

# Localmente
python -m ml.model_trainer
```

O modelo será salvo em `ml/models/` e usado pelo sistema de recomendações.

## 🔧 Configuração de Variáveis de Ambiente

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bookstore
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
SMTP_TLS=true
SMTP_SSL=false

# Payment Gateway (opcional)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Storage (opcional)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_BUCKET_NAME=bookstore-images
AWS_REGION=us-east-1

# ML Models
MODEL_PATH=/app/ml/models
RECOMMENDATION_THRESHOLD=0.5

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## 📚 API Endpoints Principais

### Autenticação
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Perfil do usuário
- `POST /api/v1/auth/logout` - Logout

### Livros
- `GET /api/v1/books` - Listar livros com filtros e busca
- `GET /api/v1/books/{id}` - Detalhes do livro
- `GET /api/v1/books/popular` - Livros populares
- `POST /api/v1/books` - Criar livro (admin)
- `PUT /api/v1/books/{id}` - Atualizar livro (admin)
- `DELETE /api/v1/books/{id}` - Deletar livro (admin)

### Categorias
- `GET /api/v1/categories` - Listar categorias
- `GET /api/v1/categories/{id}` - Detalhes da categoria

### Carrinho
- `GET /api/v1/cart` - Obter carrinho do usuário
- `POST /api/v1/cart/items` - Adicionar item ao carrinho
- `PUT /api/v1/cart/items/{item_id}` - Atualizar item do carrinho
- `DELETE /api/v1/cart/items/{item_id}` - Remover item do carrinho
- `DELETE /api/v1/cart` - Limpar carrinho

### Pedidos
- `POST /api/v1/orders` - Criar pedido
- `GET /api/v1/orders` - Listar pedidos do usuário
- `GET /api/v1/orders/{id}` - Detalhes do pedido

### Recomendações
- `GET /api/v1/recommendations/for-you` - Recomendações personalizadas
- `GET /api/v1/recommendations/trending` - Livros em alta
- `GET /api/v1/recommendations/popular` - Livros populares
- `GET /api/v1/recommendations/books/{id}/similar` - Livros similares
- `POST /api/v1/recommendations/interactions` - Registrar interação do usuário

### Reviews
- `GET /api/v1/reviews/books/{book_id}` - Listar reviews de um livro
- `POST /api/v1/reviews/books/{book_id}` - Criar review
- `PUT /api/v1/reviews/{review_id}` - Atualizar review
- `DELETE /api/v1/reviews/{review_id}` - Deletar review

### Usuários
- `GET /api/v1/users/me` - Perfil do usuário atual
- `PUT /api/v1/users/me` - Atualizar perfil

## 🧪 Testes

### Backend
```bash
pytest
```

### Frontend
```bash
cd frontend
npm run test
```

## 🛠️ Comandos Úteis

### Docker Compose

```bash
# Ver status dos containers
docker-compose ps

# Ver logs de um serviço específico
docker-compose logs backend
docker-compose logs -f backend  # Seguir logs em tempo real

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart backend

# Rebuild das imagens
docker-compose build
```

### Migrations

```bash
# Criar nova migration
docker-compose exec backend alembic revision --autogenerate -m "Descrição da migration"

# Aplicar migrations
docker-compose exec backend alembic upgrade head

# Reverter migration
docker-compose exec backend alembic downgrade -1

# Ver migration atual
docker-compose exec backend alembic current
```

### Treinamento do Modelo

```bash
# Treinar modelo
docker-compose exec backend python -m ml.model_trainer

# Ou localmente
python -m ml.model_trainer
```

## 🐛 Solução de Problemas

### Backend não inicia
1. Verifique se o PostgreSQL está rodando: `docker-compose logs postgres`
2. Verifique se as migrations foram aplicadas: `docker-compose exec backend alembic current`
3. Verifique os logs do backend: `docker-compose logs backend`
4. Verifique se as variáveis de ambiente estão configuradas corretamente

### Frontend não conecta ao backend
1. Verifique se o backend está rodando: `curl http://localhost:8000/health`
2. Verifique se a URL da API está correta no frontend
3. Verifique se o CORS está configurado corretamente no backend

### Problemas de Conexão com Banco de Dados
1. Verifique se o PostgreSQL está rodando: `docker-compose ps`
2. Verifique se a URL de conexão está correta no `.env`
3. Verifique os logs: `docker-compose logs postgres`

### Modelo de Recomendação não funciona
1. Certifique-se de que o modelo foi treinado: `docker-compose exec backend python -m ml.model_trainer`
2. Verifique se existem livros no banco de dados
3. Verifique se existem interações de usuários (para filtragem colaborativa)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique se todas as dependências estão instaladas
2. Confirme se as variáveis de ambiente estão configuradas
3. Verifique os logs do Docker: `docker-compose logs`
4. Consulte a documentação da API: http://localhost:8000/docs
5. Abra uma issue no GitHub

## 📖 Documentação Adicional

Para instruções mais detalhadas de execução, consulte o arquivo `GUIA_EXECUCAO.md`.
