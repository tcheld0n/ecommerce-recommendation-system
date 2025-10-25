# Bookstore - E-commerce de Livros com Sistema de Recomendação

Sistema completo de e-commerce especializado em livros com motor de recomendação inteligente, utilizando **arquitetura de microsserviços** com FastAPI no backend e React com TypeScript no frontend.

## 🚀 **Status do Projeto**

**✅ Sprint 1-3 Concluídas:** Fundação, Microsserviços e Simplificação  
**🚧 Sprint 4 Em Andamento:** Funcionalidades Avançadas  
**📊 Progresso:** 80% das funcionalidades core implementadas  

[📋 Ver Status Detalhado](./IMPLEMENTATION_STATUS.md)

## 🏗️ **Arquitetura de Microsserviços**

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
│              FastAPI (Port 8000)                 │
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
└─────────┘ └────────┘ └────────┘ └─────────────┘
```

## 🎯 **Funcionalidades Implementadas**

### **✅ Core Features**
- [x] **Sistema de Autenticação JWT** - Registro, login, refresh tokens
- [x] **Catálogo de Livros** - CRUD completo com busca avançada
- [x] **Carrinho de Compras** - Adicionar, remover, atualizar itens
- [x] **Sistema de Pedidos** - Checkout completo com rastreamento
- [x] **Sistema de Pagamentos** - Processamento e métodos de pagamento
- [x] **Sistema de Recomendação** - ML híbrido (colaborativo + conteúdo)
- [x] **Interface Responsiva** - React com TypeScript
- [x] **Painel Administrativo** - Gestão completa do sistema

### **✅ Arquitetura**
- [x] **8 Microsserviços** independentes e escaláveis
- [x] **API Gateway** para orquestração
- [x] **Docker** para containerização
- [x] **PostgreSQL** como banco principal
- [x] **Redis** para cache e sessões
- [x] **Elasticsearch** para busca avançada

### **🔄 Em Desenvolvimento (Sprint 4)**
- [ ] **Sistema de Reviews** - Avaliações e comentários
- [ ] **Upload de Imagens** - Gestão de imagens dos produtos
- [ ] **Sistema de Notificações** - Email e push notifications
- [ ] **Sistema de Cupons** - Descontos e promoções
- [ ] **Testes Unitários** - Cobertura completa de testes

## 🛠️ **Tecnologias Utilizadas**

### **Backend (Microsserviços)**
- **Framework:** FastAPI com Python 3.11+
- **Banco de Dados:** PostgreSQL 15+ com SQLAlchemy 2.0
- **Cache:** Redis 7+ para cache e sessões
- **Busca:** Elasticsearch 8+ para busca avançada
- **Autenticação:** JWT com refresh tokens
- **ML/Recomendação:** scikit-learn, pandas, numpy
- **Task Queue:** Celery + Redis para processamento assíncrono
- **Containerização:** Docker + Docker Compose

### **Frontend**
- **Framework:** React 18+ com TypeScript
- **Build Tool:** Vite
- **Estado:** Zustand para gerenciamento de estado
- **Roteamento:** React Router v6
- **UI Components:** shadcn/ui + Tailwind CSS
- **Formulários:** React Hook Form + Zod
- **HTTP Client:** Axios

## 🚀 **Instalação e Execução**

### **Método Recomendado: Docker**

1. **Clone o repositório**
```bash
git clone <repository-url>
cd ecommerce-recommendation-system
```

2. **Inicie todos os serviços**
```bash
docker-compose up -d
```

3. **Execute as migrations**
```bash
docker-compose exec api-gateway alembic upgrade head
```

4. **Acesse o sistema**
- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost:8000
- **Documentação:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### **Desenvolvimento Local**

#### **Backend (Microsserviços)**
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar serviço específico
cd services/catalog-service
uvicorn catalog_service:app --host 0.0.0.0 --port 8001 --reload

# Ou todos os serviços
docker-compose up -d
```

#### **Frontend**
```bash
cd frontend
npm install
npm run dev
```

## 📊 **Sistema de Recomendação**

O sistema implementa **três abordagens** de recomendação:

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

## 🔧 **Configuração de Variáveis de Ambiente**

### **Backend (.env)**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bookstore

# Redis
REDIS_URL=redis://localhost:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Service URLs
CATALOG_SERVICE_URL=http://localhost:8001
AUTH_SERVICE_URL=http://localhost:8002
USERS_SERVICE_URL=http://localhost:8003
CART_SERVICE_URL=http://localhost:8004
ORDERS_SERVICE_URL=http://localhost:8005
PAYMENT_SERVICE_URL=http://localhost:8006
RECOMMENDATION_SERVICE_URL=http://localhost:8007
```

### **Frontend (.env)**
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=E-commerce Bookstore
```

## 📚 **API Endpoints Principais**

### **Autenticação**
- `POST /api/v1/auth/register` - Registrar usuário
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Perfil do usuário

### **Catálogo**
- `GET /api/v1/books` - Listar livros com filtros
- `GET /api/v1/books/{id}` - Detalhes do livro
- `POST /api/v1/books` - Criar livro (admin)

### **Carrinho**
- `GET /api/v1/cart` - Obter carrinho
- `POST /api/v1/cart/items` - Adicionar item
- `PUT /api/v1/cart/items/{id}` - Atualizar item

### **Pedidos**
- `POST /api/v1/orders` - Criar pedido
- `GET /api/v1/orders` - Listar pedidos
- `GET /api/v1/orders/{id}` - Detalhes do pedido

### **Recomendações**
- `GET /api/v1/recommendations` - Recomendações personalizadas
- `GET /api/v1/recommendations/trending` - Livros em alta
- `GET /api/v1/recommendations/books/{id}/similar` - Livros similares

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
# Executar testes
npm run test

# Testes com cobertura
npm run test:coverage
```

## 📈 **Monitoramento e Saúde**

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Frontend:** http://localhost:3000
- **Serviços Individuais:**
  - Catalog: http://localhost:8001/health
  - Auth: http://localhost:8002/health
  - Cart: http://localhost:8004/health
  - Orders: http://localhost:8005/health
  - Payment: http://localhost:8006/health
  - Recommendation: http://localhost:8007/health

## 🎯 **Próximas Funcionalidades**

### **Sprint 4 (Em Andamento)**
- [ ] Sistema de reviews e avaliações
- [ ] Upload de imagens com AWS S3
- [ ] Sistema de notificações por email
- [ ] Sistema de cupons e promoções
- [ ] Testes unitários abrangentes

### **Sprint 5 (Planejada)**
- [ ] Integração com gateway de pagamento
- [ ] Sistema de frete
- [ ] Relatórios de vendas
- [ ] Performance e escalabilidade

### **Sprint 6 (Futuro)**
- [ ] App mobile (React Native)
- [ ] Sistema de afiliados
- [ ] Marketplace para vendedores
- [ ] Chat de suporte

## 🤝 **Contribuição**

### **Para Desenvolvedores:**
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

1. **Verifique a documentação** de implementação
2. **Confirme se todas as dependências** estão instaladas
3. **Verifique as variáveis de ambiente** estão configuradas
4. **Verifique os logs do Docker** se estiver usando
5. **Abra uma issue** no GitHub

## 🏆 **Conquistas**

- ✅ **Arquitetura de microsserviços** funcional e escalável
- ✅ **Sistema de recomendação** inteligente com ML
- ✅ **Interface moderna** e responsiva
- ✅ **Autenticação segura** com JWT
- ✅ **E-commerce completo** com todas as funcionalidades core
- ✅ **Código limpo** e bem documentado
- ✅ **Containerização** completa com Docker

---

**Desenvolvido com ❤️ usando FastAPI, React e TypeScript**