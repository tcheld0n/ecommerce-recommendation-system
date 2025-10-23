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
└────────────────┬────────────────────────────────┘
                 │ HTTP/REST
                 │
┌────────────────▼────────────────────────────────┐
│                  API Gateway                     │
│              FastAPI (Python)                    │
│              - Rotas REST                        │
│              - Autenticação JWT                  │
│              - Validação Pydantic                │
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
│          │  │  (Cache)  │   │  (Busca)    │
└──────────┘  └───────────┘   └─────────────┘
```

## 🎯 Funcionalidades

### ✅ Implementadas
- [x] Sistema de autenticação JWT
- [x] CRUD de livros e categorias
- [x] Sistema de busca avançada
- [x] Carrinho de compras
- [x] Sistema de pedidos
- [x] Sistema de recomendação híbrido
- [x] Interface responsiva
- [x] Painel administrativo

### 🔄 Em Desenvolvimento
- [ ] Sistema de reviews e avaliações
- [ ] Integração com gateway de pagamento
- [ ] Sistema de notificações por email
- [ ] Upload de imagens
- [ ] Sistema de cupons de desconto

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Elasticsearch 8+

### Backend

1. **Clone o repositório**
```bash
git clone <repository-url>
cd ecommerce-recommendation-system
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

4. **Execute as migrations**
```bash
alembic upgrade head
```

5. **Inicie o servidor**
```bash
uvicorn main:app --reload --port 8000
```

### Frontend

1. **Navegue para o diretório do frontend**
```bash
cd frontend
```

2. **Instale as dependências**
```bash
npm install
```

3. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. **Inicie o servidor de desenvolvimento**
```bash
npm run dev
```

### Docker (Recomendado)

1. **Inicie todos os serviços**
```bash
docker-compose up -d
```

2. **Execute as migrations**
```bash
docker-compose exec backend alembic upgrade head
```

3. **Treine o modelo de recomendação**
```bash
docker-compose exec backend python -m ml.model_trainer
```

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
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Payment Gateway
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_BUCKET_NAME=bookstore-images

# ML Models
MODEL_PATH=/app/ml/models
RECOMMENDATION_THRESHOLD=0.5
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 📚 API Endpoints

### Autenticação
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Perfil do usuário

### Livros
- `GET /api/v1/books` - Listar livros com filtros
- `GET /api/v1/books/{id}` - Detalhes do livro
- `POST /api/v1/books` - Criar livro (admin)
- `PUT /api/v1/books/{id}` - Atualizar livro (admin)
- `DELETE /api/v1/books/{id}` - Deletar livro (admin)

### Recomendações
- `GET /api/v1/recommendations/for-you` - Recomendações personalizadas
- `GET /api/v1/recommendations/trending` - Livros em alta
- `GET /api/v1/recommendations/popular` - Livros populares
- `GET /api/v1/recommendations/books/{id}/similar` - Livros similares

## 🧪 Testes

### Backend
```bash
pytest
```

### Frontend
```bash
npm run test
```

## 📈 Monitoramento

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:3000

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas, por favor:

1. Verifique se todas as dependências estão instaladas
2. Confirme se as variáveis de ambiente estão configuradas
3. Verifique os logs do Docker se estiver usando
4. Abra uma issue no GitHub

## 🎯 Próximos Passos

- [ ] Implementar sistema de cupons e promoções
- [ ] Adicionar sistema de notificações push
- [ ] Implementar chat de suporte
- [ ] Criar app mobile (React Native)
- [ ] Adicionar sistema de afiliados
- [ ] Implementar marketplace para vendedores terceiros
