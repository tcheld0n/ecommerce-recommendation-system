# Bookstore - E-commerce de Livros com Sistema de Recomendação

Sistema completo de e-commerce especializado em livros com motor de recomendação inteligente, utilizando **arquitetura de microsserviços** com FastAPI no backend e React com TypeScript no frontend.

## 🚀 **Status do Projeto**

**✅ Sprint 1-3 Concluídas:** Fundação, Microsserviços e Simplificação  
**🚧 Sprint 4 Em Andamento:** Funcionalidades Avançadas  
**📊 Progresso:** 80% das funcionalidades core implementadas  

[📋 Ver Status Detalhado](./IMPLEMENTATION_STATUS.md)

## 🏗️ **Arquitetura de Microsserviços Simplificada**

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
┌─────▼───┐ ┌──▼─────┐ ┌──▼────┐ ┌──▼──────────┐
│Catalog  │ │ Auth   │ │ Cart  │ │ Orders      │
│Service  │ │Service │ │Service│ │Service      │
│:8001    │ │:8002   │ │:8004  │ │:8005        │
└─────┬───┘ └──┬─────┘ └──┬────┘ └──┬──────────┘
      │        │          │         │
┌─────▼───┐ ┌──▼─────┐ ┌──▼────┐ ┌──▼──────────┐
│Payment  │ │ Users  │ │Recommend│ │            │
│Service  │ │Service │ │Service │ │            │
│:8006    │ │:8003   │ │:8007   │ │            │
└─────┬───┘ └──┬─────┘ └──┬────┘ └──┬──────────┘
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

### 🔧 **Serviços Implementados (7)**

| Serviço | Porta | Status | Funcionalidade |
|---------|-------|--------|----------------|
| **API Gateway** | 8000 | ✅ | Roteamento e orquestração |
| **Catalog Service** | 8001 | ✅ | Gestão de produtos/livros |
| **Auth Service** | 8002 | ✅ | Autenticação e autorização |
| **Users Service** | 8003 | ✅ | Gestão de usuários e perfis |
| **Cart Service** | 8004 | ✅ | Carrinho de compras |
| **Orders Service** | 8005 | ✅ | Gestão de pedidos |
| **Payment Service** | 8006 | ✅ | Pagamentos (placeholder) |
| **Recommendation Service** | 8007 | ✅ | Sistema de recomendações |

### 🏗️ **Infraestrutura de Apoio**

| Componente | Porta | Status | Função |
|------------|-------|--------|--------|
| **PostgreSQL** | 5432 | ✅ | Banco de dados principal |
| **Redis** | 6379 | ✅ | Cache e sessões |
| **Elasticsearch** | 9200 | ✅ | Busca e indexação |
| **Celery** | - | ✅ | Processamento assíncrono |
| **Celery Beat** | - | ✅ | Agendamento de tarefas |

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

### 🔄 Futuras implementações
- [ ] Implementação completa do serviço de envios
- [ ] Sistema de notificações por email
- [ ] Implementação completa do serviço de reviews
- [ ] Upload de imagens
- [ ] Sistema de cupons de desconto


## 🛠️ Instalação e Configuração

### Pré-requisitos
- **Docker** e **Docker Compose** (recomendado)
- **Python 3.11+** (se rodar backend localmente)
- **Node.js 18+** (se rodar frontend localmente)

> **💡 Nota:** Para projeto didático, recomendamos usar Docker Compose para simplicidade.

## 🚀 Como Rodar o Projeto

### Opção 1: Usando Docker Compose (Recomendado) ⭐

#### 1. Clone o repositório
```bash
git clone <repository-url>
cd ecommerce-recommendation-system
```

#### 2. Inicie todos os serviços
```bash
docker compose up -d
```

#### 3. Popule o banco de dados com dados de exemplo (recomendado)
```bash
docker compose run --rm catalog-service python import_csv_only.py
```

> **📝 Nota:** Este comando importa dados do arquivo `livros.csv` para o banco de dados, criando categorias padrão e livros de exemplo. É recomendado executar este passo para ter dados para testar o sistema de recomendação.

#### 4. Inicie o frontend
```bash
cd frontend
npm install
npm run dev
```

#### 5. Acesse a aplicação
- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost:8000
- **Documentação da API:** http://localhost:8000/docs

### ✅ Verificação dos Serviços

Para verificar se todos os serviços estão rodando:

```bash
docker compose ps
```

Você deve ver todos os serviços com status "Up":
- ✅ api-gateway (porta 8000)
- ✅ catalog-service (porta 8001) 
- ✅ auth-service (porta 8002)
- ✅ users-service (porta 8003)
- ✅ cart-service (porta 8004)
- ✅ orders-service (porta 8005)
- ✅ payment-service (porta 8006)
- ✅ recommendation-service (porta 8007)
- ✅ postgres (porta 5432)
- ✅ redis (porta 6379)
- ✅ elasticsearch (porta 9200)
- ✅ celery (worker)
- ✅ celery-beat (scheduler)

### Opção 2: Execução Local (sem Docker) ⚠️

> **⚠️ Aviso:** Execução local é mais complexa devido à arquitetura de microsserviços. Recomendamos usar Docker Compose.

#### Pré-requisitos
- PostgreSQL 15+ rodando na porta 5432
- Redis 7+ rodando na porta 6379  
- Elasticsearch 8+ rodando na porta 9200

#### 1. Configure as variáveis de ambiente
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

#### 2. Instale dependências de cada serviço
```bash
# Para cada serviço em services/*/requirements.txt
pip install -r services/catalog-service/requirements.txt
pip install -r services/auth-service/requirements.txt
pip install -r services/users-service/requirements.txt
pip install -r services/cart-service/requirements.txt
pip install -r services/orders-service/requirements.txt
pip install -r services/payment-service/requirements.txt
pip install -r services/recommendation-service/requirements.txt
pip install -r services/api-gateway/requirements.txt
```

#### 3. Popule o banco de dados
```bash
python import_csv_only.py
```

#### 4. Inicie cada microserviço (em terminais separados)
```bash
# Terminal 1 - API Gateway
cd services/api-gateway
uvicorn api_gateway:app --reload --port 8000

# Terminal 2 - Catalog Service  
cd services/catalog-service
uvicorn catalog_service:app --reload --port 8001

# Terminal 3 - Auth Service
cd services/auth-service
uvicorn auth_service:app --reload --port 8002

# Terminal 4 - Users Service
cd services/users-service
uvicorn users_service:app --reload --port 8003

# Terminal 5 - Cart Service
cd services/cart-service
uvicorn cart_service:app --reload --port 8004

# Terminal 6 - Orders Service
cd services/orders-service
uvicorn orders_service:app --reload --port 8005

# Terminal 7 - Payment Service
cd services/payment-service
uvicorn payment_service:app --reload --port 8006

# Terminal 8 - Recommendation Service
cd services/recommendation-service
uvicorn recommendation_service:app --reload --port 8007

# Terminal 9 - Celery Worker
celery -A tasks.celery_app worker --loglevel=info

# Terminal 10 - Celery Beat
celery -A tasks.celery_app beat --loglevel=info
```

#### Frontend

1. **Navegue para o diretório do frontend**
```bash
cd frontend
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
- **API Gateway**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Microserviços Individuais
- **Catalog Service**: http://localhost:8001/docs
- **Auth Service**: http://localhost:8002/docs
- **Users Service**: http://localhost:8003/docs
- **Cart Service**: http://localhost:8004/docs
- **Orders Service**: http://localhost:8005/docs
- **Payment Service**: http://localhost:8006/docs
- **Recommendation Service**: http://localhost:8007/docs

## 📊 Sistema de Recomendação

O sistema implementa três abordagens de recomendação:

### **1. Filtragem Baseada em Conteúdo**
- Similaridade entre livros baseada em:
  - Categoria/gênero
  - Autor
  - Tags e palavras-chave
  - Descrição (TF-IDF)
- **Algoritmo:** Cosine Similarity

### **2. Filtragem Colaborativa**
- **User-based:** usuários similares compraram livros similares
- **Item-based:** livros comprados juntos frequentemente
- **Algoritmo:** Matrix Factorization (SVD) + KNN

### **3. Sistema Híbrido**
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

### **Autenticação**
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login
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

## 🧪 **Testes**

### **Backend**
```bash
# Executar todos os testes
pytest

# Teste específico
pytest tests/test_catalog_service.py
```

### **Frontend**
```bash
cd frontend
npm run test

# Testes com cobertura
npm run test:coverage
```

## 🛠️ Comandos Úteis

### Docker Compose

```bash
# Ver status dos containers
docker compose ps

# Ver logs de todos os serviços
docker compose logs

# Ver logs de um serviço específico
docker compose logs api-gateway
docker compose logs catalog-service
docker compose logs -f api-gateway  # Seguir logs em tempo real

# Parar todos os serviços
docker compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker compose down -v

# Reiniciar um serviço específico
docker compose restart catalog-service

# Reconstruir e reiniciar um serviço
docker compose up --build catalog-service

# Executar comando em um serviço específico
docker compose exec catalog-service python import_csv_only.py
docker compose exec postgres psql -U user -d bookstore
```

### Migrations

```bash
# Criar nova migration
docker compose exec catalog-service alembic revision --autogenerate -m "Descrição da migration"

# Aplicar migrations
docker compose exec catalog-service alembic upgrade head

# Reverter migration
docker compose exec catalog-service alembic downgrade -1

# Ver migration atual
docker compose exec catalog-service alembic current
```

### Importação de Dados

```bash
# Importar dados do CSV (Docker)
docker compose run --rm catalog-service python import_csv_only.py

# Importar dados do CSV (local)
python import_csv_only.py

# Verificar quantos livros foram importados
docker compose exec postgres psql -U user -d bookstore -c "SELECT COUNT(*) FROM books;"
```

### Treinamento do Modelo

```bash
# Treinar modelo
docker compose exec recommendation-service python -m ml.model_trainer

# Ou localmente
python -m ml.model_trainer
```

### Monitoramento

```bash
# Verificar saúde dos serviços
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# Ver documentação da API
# Acesse: http://localhost:8000/docs
```

## 🐛 Solução de Problemas

### Microserviços não iniciam
1. Verifique se o PostgreSQL está rodando: `docker compose logs postgres`
2. Verifique se as migrations foram aplicadas: `docker compose exec catalog-service alembic current`
3. Verifique os logs dos serviços: `docker compose logs api-gateway`
4. Verifique se as variáveis de ambiente estão configuradas corretamente
5. Verifique se todos os volumes estão montados: `docker compose ps`

### Frontend não conecta ao API Gateway
1. Verifique se o API Gateway está rodando: `curl http://localhost:8000/health`
2. Verifique se a URL da API está correta no frontend
3. Verifique se o CORS está configurado corretamente no API Gateway
4. Verifique se todos os microserviços estão rodando: `docker compose ps`

### Problemas de Conexão com Banco de Dados
1. Verifique se o PostgreSQL está rodando: `docker compose ps`
2. Verifique se a URL de conexão está correta no `.env`
3. Verifique os logs: `docker compose logs postgres`
4. Teste a conexão: `docker compose exec postgres psql -U user -d bookstore -c "SELECT 1;"`

### Modelo de Recomendação não funciona
1. Certifique-se de que o modelo foi treinado: `docker compose exec recommendation-service python -m ml.model_trainer`
2. Verifique se existem livros no banco de dados: `docker compose exec postgres psql -U user -d bookstore -c "SELECT COUNT(*) FROM books;"`
3. Verifique se existem interações de usuários (para filtragem colaborativa)

### Problemas de Importação de Dados
1. Verifique se o arquivo `livros.csv` existe no diretório raiz
2. Execute a importação: `docker compose run --rm catalog-service python import_csv_only.py`
3. Verifique se os dados foram importados: `docker compose exec postgres psql -U user -d bookstore -c "SELECT COUNT(*) FROM books;"`

## 🏗️ **Arquitetura Simplificada**

### **Princípios da Refatoração**

Este projeto foi **refatorado** para eliminar over-engineering e focar no aprendizado de arquitetura de microsserviços:

#### ✅ **O que foi simplificado:**
- **Removidas dependências desnecessárias** entre serviços
- **Eliminadas abstrações excessivas** (services, repositories)
- **Implementação direta** da lógica nos endpoints FastAPI
- **Configuração centralizada** em `core/config.py`
- **Payment Service** como placeholder (não implementação real)
- **Variáveis de ambiente** comentadas (email, AWS) para projeto didático

#### 🎯 **Benefícios:**
- **Código mais limpo** e fácil de entender
- **Menos complexidade** para estudantes
- **Foco na arquitetura** de microsserviços
- **Manutenção simplificada**
- **Setup rápido** com Docker Compose

#### 📚 **Para Estudantes:**
- **Cada serviço** é independente e focado
- **Lógica de negócio** clara nos endpoints
- **Comunicação** entre serviços via HTTP/REST
- **Banco de dados** compartilhado (PostgreSQL)
- **Cache** compartilhado (Redis)
- **Busca** compartilhada (Elasticsearch)

### **Estrutura de Diretórios**

```
├── core/                    # Configurações compartilhadas
│   ├── config.py           # Configurações centralizadas
│   ├── database.py         # Conexão com banco
│   └── utils.py            # Utilitários comuns
├── models/                  # Modelos SQLAlchemy
├── schemas/                 # Schemas Pydantic
├── services/                # Microserviços
│   ├── api-gateway/        # Gateway principal
│   ├── catalog-service/    # Gestão de livros
│   ├── auth-service/       # Autenticação
│   ├── users-service/      # Gestão de usuários
│   ├── cart-service/       # Carrinho de compras
│   ├── orders-service/     # Gestão de pedidos
│   ├── payment-service/    # Pagamentos (placeholder)
│   └── recommendation-service/ # Sistema de recomendações
├── frontend/                # Interface React
└── docker-compose.yml      # Orquestração dos serviços
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Implemente seguindo os padrões estabelecidos
4. Adicione testes para sua funcionalidade
5. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
6. Push para a branch (`git push origin feature/AmazingFeature`)
7. Abra um Pull Request

### **Para Testadores:**
1. Teste as funcionalidades existentes
2. Reporte bugs encontrados
3. Sugira melhorias de UX
4. Valide a performance

### **Para Designers:**
1. Melhore a interface existente
2. Crie novos componentes
3. Otimize a experiência do usuário
4. Desenvolva identidade visual

## 📄 **Documentação**

- [📋 Status de Implementação](./IMPLEMENTATION_STATUS.md) - Status detalhado por sprint
- [🏗️ Arquitetura Simplificada](./SIMPLIFIED_ARCHITECTURE.md) - Guia da arquitetura
- [📚 Documentação da API](http://localhost:8000/docs) - Swagger/OpenAPI

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 **Suporte**

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique se todas as dependências estão instaladas
2. Confirme se as variáveis de ambiente estão configuradas
3. Verifique os logs do Docker: `docker compose logs`
4. Consulte a documentação da API: http://localhost:8000/docs
5. Verifique o status dos serviços: `docker compose ps`
6. Abra uma issue no GitHub

## 📖 Documentação Adicional