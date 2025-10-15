# E-Commerce Book Recommendation System

A comprehensive e-commerce platform for books with an intelligent recommendation engine built using Flask, SQLAlchemy, and machine learning algorithms.

## Features

### Core E-Commerce Features
- **Book Catalog**: Browse and search books by title, author, genre
- **User Management**: User registration and profile management
- **Shopping Cart**: Add, update, and remove books from cart
- **Purchase System**: Complete checkout process with stock management
- **Rating & Reviews**: Rate books and write reviews

### Recommendation Engine
The system includes an intelligent recommendation engine with multiple algorithms:

1. **Collaborative Filtering**: Recommends books based on similar users' preferences
   - Uses user-item rating matrix
   - Calculates user similarity using cosine similarity
   - Suggests books that similar users have rated highly

2. **Content-Based Filtering**: Recommends books similar to ones you've viewed
   - Matches books by genre and author
   - Great for discovering similar titles

3. **Popular Books**: Fallback recommendations based on overall ratings and purchase counts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tcheld0n/ecommerce-recommendation-system.git
cd ecommerce-recommendation-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

**Note**: By default, the application runs in debug mode for development. For production deployment:
- Set the environment variable `FLASK_DEBUG=0` to disable debug mode
- Use a production WSGI server like Gunicorn or uWSGI instead of the Flask development server

## API Endpoints

### Books
- `GET /api/books` - Get all books (supports filtering by genre, author, search)
- `GET /api/books/<book_id>` - Get specific book details
- `POST /api/books` - Add a new book
- `GET /api/books/<book_id>/ratings` - Get ratings for a book

### Users
- `POST /api/users` - Create a new user
- `GET /api/users/<user_id>` - Get user details

### Shopping Cart
- `GET /api/cart/<user_id>` - Get user's cart
- `POST /api/cart` - Add item to cart
- `PUT /api/cart/<cart_id>` - Update cart item quantity
- `DELETE /api/cart/<cart_id>` - Remove item from cart

### Purchases
- `POST /api/purchase` - Complete purchase from cart
- `GET /api/purchases/<user_id>` - Get user's purchase history

### Ratings
- `POST /api/ratings` - Add or update a book rating

### Recommendations
- `GET /api/recommendations/<user_id>` - Get personalized recommendations
- `GET /api/recommendations/book/<book_id>` - Get similar books
- `GET /api/recommendations/popular` - Get popular books

## Usage Examples

### Search for Books
```bash
curl http://localhost:5000/api/books?genre=Fantasy
curl http://localhost:5000/api/books?search=Harry%20Potter
```

### Create a User
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com"}'
```

### Add to Cart
```bash
curl -X POST http://localhost:5000/api/cart \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1, "quantity": 2}'
```

### Rate a Book
```bash
curl -X POST http://localhost:5000/api/ratings \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "book_id": 1, "rating": 5, "review": "Amazing book!"}'
```

### Get Personalized Recommendations
```bash
curl http://localhost:5000/api/recommendations/1?n=5
```

### Complete Purchase
```bash
curl -X POST http://localhost:5000/api/purchase \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

## Database Schema

### Book
- id, title, author, isbn, price, description, genre, published_year, stock, image_url

### User
- id, username, email

### Purchase
- id, user_id, book_id, quantity, total_price, purchase_date

### Rating
- id, user_id, book_id, rating (1-5), review

### Cart
- id, user_id, book_id, quantity

## Recommendation Algorithm

The recommendation engine uses a hybrid approach:

1. **Collaborative Filtering**: Builds a user-item matrix from ratings and calculates user similarity using cosine similarity. Recommends books that similar users have rated highly.

2. **Content-Based Filtering**: Analyzes book attributes (genre, author) to find similar books.

3. **Popularity-Based**: When user data is insufficient, recommends popular books based on average ratings and purchase counts.

## Sample Data

The application comes pre-loaded with 10 classic and popular books including:
- The Great Gatsby
- To Kill a Mockingbird
- 1984
- Harry Potter and the Sorcerer's Stone
- The Lord of the Rings
- And more...

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Machine Learning**: NumPy, Pandas, Scikit-learn
- **CORS**: Flask-CORS for cross-origin requests

## Development

The project follows a modular structure:
- `app.py`: Main application with API endpoints
- `models.py`: Database models
- `recommendation_engine.py`: Recommendation algorithms
- `requirements.txt`: Python dependencies

## Future Enhancements

Potential improvements for the system:
- User authentication and authorization
- Payment gateway integration
- Advanced search with filters
- Book categories and tags
- Wishlist functionality
- Order tracking
- Email notifications
- Admin dashboard
- Matrix factorization for better recommendations
- Deep learning-based recommendations

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
=======
# 🛒 E-Commerce MVP - Microservices Architecture

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)
![TypeScript](https://img.shields.io/badge/typescript-%5E5.0.0-blue.svg)
![NestJS](https://img.shields.io/badge/nestjs-%5E10.0.0-red.svg)

## 📋 Sobre o Projeto

MVP (Minimum Viable Product) de uma plataforma de e-commerce moderna baseada em **arquitetura de microserviços**, desenvolvida com **Node.js/TypeScript** e **NestJS**. Este projeto representa a primeira fase de migração tecnológica, focando na validação da arquitetura e integração entre serviços.

### 🎯 Objetivos do MVP

- ✅ Validar a viabilidade da arquitetura de microserviços
- ✅ Estabelecer padrões de desenvolvimento e comunicação entre serviços
- ✅ Implementar funcionalidade básica de listagem de produtos
- ✅ Integrar sistema de recomendações (mockado)
- ✅ Demonstrar comunicação síncrona via HTTP/REST

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                   API Gateway                        │
│              (Product-Service/Gateway)               │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐       ┌──────────────────────┐
│ Product       │       │ Recommendation       │
│ Service       │       │ Adapter              │
│ (Node.js)     │       │ (Node.js/NestJS)     │
│               │       │                      │
│ - CRUD        │       │ - Adapter Pattern    │
│ - PostgreSQL  │       │ - HTTP Proxy         │
│ - Prisma ORM  │       │ - Mock (MVP)         │
└───────┬───────┘       └──────────┬───────────┘
        │                          │
        ▼                          ▼
┌───────────────┐       ┌──────────────────────┐
│  PostgreSQL   │       │  Recommendation      │
│   Database    │       │  Service (Python)    │
│               │       │                      │
└───────────────┘       │  - FastAPI/Flask     │
                        │  - ML Models         │
                        │  - Redis Cache       │
                        └──────────────────────┘
```

### 🔧 Microserviços

#### 1️⃣ Product-Service (Port: 3001)
**Responsabilidade:** Gerenciamento completo do catálogo de produtos

- **Endpoints:**
  - `GET /products` - Lista todos os produtos
  - `POST /products` - Cria novo produto
  - `GET /products/:id` - Busca produto específico
- **Persistência:** PostgreSQL via Prisma ORM
- **Validação:** DTOs com class-validator

#### 2️⃣ Recommendation-Adapter (Port: 3002) - Node.js/NestJS
**Responsabilidade:** Adapter/Bridge para o sistema de recomendações Python

- **Endpoints:**
  - `GET /recommendations/:userId` - Retorna IDs de produtos recomendados
- **Persistência:** Nenhuma (stateless adapter)
- **Comunicação:** HTTP client para o Python Recommendation Service
- **Fase MVP:** Dados mockados localmente
- **Produção:** Proxy para `http://python-recommendation-service:5000`

#### 3️⃣ Gateway (Mock)
**Responsabilidade:** Orquestração e agregação de dados

- **Endpoints:**
  - `GET /home` - Consolida produtos + recomendações
- **Funcionalidade:** Chama múltiplos serviços e combina respostas

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Versão | Propósito |
|--------|-----------|---------|-----------|
| **Runtime** | Node.js | ≥18.x | Ambiente de execução |
| **Linguagem** | TypeScript | ^5.0.0 | Type safety e robustez |
| **Framework** | NestJS | ^10.0.0 | Arquitetura e microserviços |
| **Banco de Dados** | PostgreSQL | 15 | Persistência relacional |
| **ORM** | Prisma | ^5.0.0 | Type-safe database client |
| **Containerização** | Docker / Docker Compose | - | Orquestração de ambientes |
| **Validação** | class-validator | ^0.14.0 | Validação de DTOs |
| **HTTP Client** | Axios | ^1.6.0 | Comunicação entre serviços |
| **ML Service** | Python (FastAPI/Flask) | 3.11+ | Sistema de recomendações |

---

## 🚀 Quick Start

### Pré-requisitos

```bash
node >= 18.0.0
npm >= 9.0.0
docker >= 24.0.0
docker-compose >= 2.20.0
```

### Instalação

```bash
# 1. Clone o repositório
git clone <repository-url>
cd ecommerce-mvp

# 2. Instale as dependências
npm install

# 3. Suba a infraestrutura
docker-compose up -d

# 4. Execute as migrações
cd product-service
npx prisma migrate dev

# 5. Inicie os serviços
npm run start:dev
```

### Verificação

```bash
# Product Service
curl http://localhost:3001/products

# Recommendation Adapter
curl http://localhost:3002/recommendations/1

# Gateway
curl http://localhost:3001/home
```

---

## 📁 Estrutura do Projeto

```
ecommerce-mvp/
├── product-service/
│   ├── src/
│   │   ├── products/
│   │   │   ├── dto/
│   │   │   │   └── create-product.dto.ts
│   │   │   ├── products.controller.ts
│   │   │   ├── products.service.ts
│   │   │   └── products.module.ts
│   │   ├── gateway/
│   │   │   ├── gateway.controller.ts
│   │   │   └── gateway.service.ts
│   │   ├── prisma/
│   │   │   └── schema.prisma
│   │   └── main.ts
│   ├── prisma/
│   │   └── migrations/
│   ├── Dockerfile
│   └── package.json
│
├── recommendation-adapter/
│   ├── src/
│   │   ├── recommendations/
│   │   │   ├── recommendations.controller.ts
│   │   │   ├── recommendations.service.ts
│   │   │   └── recommendations.module.ts
│   │   ├── clients/
│   │   │   └── python-recommendation.client.ts
│   │   └── main.ts
│   ├── Dockerfile
│   └── package.json
│
├── python-recommendation-service/      # Sistema legado Python
│   ├── app/
│   │   ├── main.py                     # FastAPI/Flask app
│   │   ├── models/
│   │   │   └── recommendation_model.py
│   │   ├── routes/
│   │   │   └── recommendations.py
│   │   └── utils/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🎯 Sprint 1 - Roadmap (3 Dias)

### 📦 1. Infraestrutura (Dia 1)

- [x] Setup do monorepo/multi-projeto com NestJS CLI
- [x] Configuração do Docker Compose (PostgreSQL + Serviços)
- [x] Setup do Prisma ORM e primeira migração
- [x] Validação: `docker-compose up` sem erros

**DoD:** Todos os containers online e comunicando

### 🏪 2. Product-Service (Dia 2)

- [x] Implementação do CRUD básico de produtos
- [x] Definição de DTOs com validação
- [x] Tipagem end-to-end com Prisma
- [x] Seed inicial de produtos

**DoD:** `POST /products` e `GET /products` funcionais com validação

### 🔗 3. Comunicação & Gateway (Dia 3)

- [x] Adaptador de recomendações mockado
- [x] Gateway com composição de dados
- [x] Integração Product-Service ↔ Recommendation-Adapter
- [x] Testes de integração end-to-end

**DoD:** `GET /home` retorna produtos com flag `isRecommended`

---

## 🐍 Integração com Sistema Python (Recomendações)

### Arquitetura de Integração

O **Recommendation-Adapter** (Node.js) atua como uma camada de adaptação entre o ecossistema NestJS e o serviço Python legado de Machine Learning.

#### Fase 1 - MVP (Sprint 1-2)
```typescript
// Mock local no adapter
GET /recommendations/:userId → Retorna IDs hardcoded
```

#### Fase 2 - Integração Real (Sprint 3+)
```typescript
// Proxy para serviço Python
GET /recommendations/:userId 
  → HTTP Request para http://python-service:5000/api/recommend
  → Transformação de dados (Python → TypeScript)
  → Retorno padronizado
```

### Python Recommendation Service

**Stack Esperada:**
- **Framework:** FastAPI (recomendado) ou Flask
- **ML Libraries:** scikit-learn, TensorFlow, PyTorch
- **Cache:** Redis para otimização
- **Port:** 5000

**Endpoint Esperado:**
```python
POST /api/recommend
Content-Type: application/json

{
  "user_id": "123",
  "context": {
    "current_category": "electronics",
    "limit": 10
  }
}

Response:
{
  "user_id": "123",
  "recommendations": [
    {"product_id": 456, "score": 0.95},
    {"product_id": 789, "score": 0.87}
  ],
  "algorithm": "collaborative_filtering",
  "generated_at": "2025-10-15T10:30:00Z"
}
```

### Configuração Docker Compose

```yaml
services:
  python-recommendation:
    build: ./python-recommendation-service
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379
      - MODEL_PATH=/app/models/recommendation_model.pkl
    volumes:
      - ./python-recommendation-service:/app
    depends_on:
      - redis
  
  recommendation-adapter:
    environment:
      - PYTHON_SERVICE_URL=http://python-recommendation:5000
```

### Benefícios do Adapter Pattern

✅ **Isolamento:** Mudanças no Python não afetam o resto do sistema  
✅ **Transformação:** Converte respostas Python para padrão TypeScript  
✅ **Resiliência:** Circuit breaker e fallback para mock se Python cair  
✅ **Observabilidade:** Logs centralizados no ecossistema Node.js  
✅ **Type Safety:** Interface tipada mesmo com serviço não-tipado

---

## 🧪 Testes

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:cov
```

---

## 📝 Convenções de Código

### Commits (Conventional Commits)

```
feat: adiciona endpoint de listagem de produtos
fix: corrige validação de DTOs
docs: atualiza README com instruções de setup
chore: configura Docker Compose
```

### Code Style

- **Linter:** ESLint + Prettier
- **Naming:** camelCase para variáveis, PascalCase para classes
- **Imports:** Ordem alfabética com barrel exports

---

## 🔐 Variáveis de Ambiente

```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/ecommerce"

# Services
PRODUCT_SERVICE_PORT=3001
RECOMMENDATION_SERVICE_PORT=3002

# External APIs (Future)
RECOMMENDATION_API_URL=http://legacy-system.com/api
```

---

## 🚧 Próximos Passos

1. **Sprint 2:** Implementar serviço de autenticação
2. **Sprint 3:** Adicionar cache com Redis
3. **Sprint 4:** Migrar comunicação para message broker (RabbitMQ)
4. **Sprint 5:** Implementar observabilidade (logs, métricas, tracing)

---

## 📚 Recursos & Documentação

- [NestJS Documentation](https://docs.nestjs.com/)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

## 👥 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---


[⬆ Voltar ao topo](#-e-commerce-mvp---microservices-architecture)


