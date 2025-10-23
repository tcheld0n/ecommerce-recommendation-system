# 🚀 Guia de Execução do Sistema de E-commerce de Livros

## 📋 Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado:

- **Docker** e **Docker Compose** (versão mais recente)
- **Node.js** (versão 18 ou superior)
- **npm** (vem com Node.js)

## 🛠️ Passos para Executar o Projeto

### 1. Clone o Repositório (se necessário)
```bash
git clone <url-do-repositorio>
cd ecommerce-recommendation-system
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto baseado no `env.example`:

```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bookstore

# Redis
REDIS_URL=redis://localhost:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Payment Gateway (opcional)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# Storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# ML Models
MODEL_PATH=models/
RECOMMENDATION_THRESHOLD=0.5
```

### 3. Executar o Backend (Docker)

#### 3.1. Iniciar os Serviços de Infraestrutura
```bash
# Iniciar PostgreSQL, Redis e Elasticsearch
docker-compose up -d postgres redis elasticsearch

# Aguardar os serviços ficarem saudáveis (cerca de 30-60 segundos)
docker-compose ps
```

#### 3.2. Executar as Migrations do Banco de Dados
```bash
# Executar migrations dentro do container
docker-compose exec backend alembic upgrade head
```

#### 3.3. Iniciar Todos os Serviços
```bash
# Iniciar todos os serviços (backend, celery, etc.)
docker-compose up -d
```

#### 3.4. Verificar se o Backend está Funcionando
```bash
# Testar endpoint de health
curl http://localhost:8000/health

# Deve retornar: {"status":"healthy"}
```

### 4. Executar o Frontend

#### 4.1. Navegar para o Diretório do Frontend
```bash
cd frontend
```

#### 4.2. Instalar Dependências
```bash
npm install
```

#### 4.3. Iniciar o Servidor de Desenvolvimento
```bash
npm run dev
```

#### 4.4. Verificar se o Frontend está Funcionando
- Abra o navegador em: `http://localhost:5173`
- Você deve ver a página inicial do sistema

### 5. Verificar se Tudo Está Funcionando

#### 5.1. Backend (API)
- **Health Check**: `http://localhost:8000/health`
- **Documentação Swagger**: `http://localhost:8000/docs`
- **Documentação ReDoc**: `http://localhost:8000/redoc`

#### 5.2. Frontend
- **Aplicação**: `http://localhost:5173`

#### 5.3. Serviços de Infraestrutura
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **Elasticsearch**: `http://localhost:9200`

## 🔧 Comandos Úteis

### Gerenciar Serviços Docker
```bash
# Ver status dos containers
docker-compose ps

# Ver logs de um serviço específico
docker-compose logs backend
docker-compose logs frontend

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart backend
```

### Gerenciar Migrations
```bash
# Criar nova migration
docker-compose exec backend alembic revision --autogenerate -m "Descrição da migration"

# Aplicar migrations
docker-compose exec backend alembic upgrade head

# Reverter migration
docker-compose exec backend alembic downgrade -1
```

### Desenvolvimento Frontend
```bash
# Instalar nova dependência
npm install nome-do-pacote

# Build para produção
npm run build

# Preview do build
npm run preview
```

## 🐛 Solução de Problemas

### Backend não inicia
1. Verifique se o PostgreSQL está rodando: `docker-compose logs postgres`
2. Verifique se as migrations foram aplicadas: `docker-compose exec backend alembic current`
3. Verifique os logs do backend: `docker-compose logs backend`

### Frontend não inicia
1. Verifique se o Node.js está instalado: `node --version`
2. Limpe o cache do npm: `npm cache clean --force`
3. Delete `node_modules` e reinstale: `rm -rf node_modules && npm install`

### Problemas de Conexão
1. Verifique se as portas não estão em uso: `netstat -an | findstr :8000`
2. Verifique se o firewall não está bloqueando as portas
3. Reinicie os serviços: `docker-compose restart`

## 📊 Monitoramento

### Logs em Tempo Real
```bash
# Ver todos os logs
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
```

### Status dos Serviços
```bash
# Ver status dos containers
docker-compose ps

# Ver uso de recursos
docker stats
```

## 🚀 Deploy em Produção

### 1. Configurar Variáveis de Produção
- Atualize o arquivo `.env` com configurações de produção
- Configure SSL/HTTPS
- Configure domínios e DNS

### 2. Build do Frontend
```bash
cd frontend
npm run build
```

### 3. Deploy com Docker
```bash
# Build das imagens
docker-compose build

# Deploy
docker-compose up -d
```

## 📝 Próximos Passos

1. **Testar a API**: Use a documentação Swagger em `http://localhost:8000/docs`
2. **Criar usuários**: Registre-se através da API ou frontend
3. **Adicionar livros**: Use a interface admin ou API
4. **Testar recomendações**: Navegue pelo sistema e veja as recomendações funcionando

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs: `docker-compose logs`
2. Verifique se todos os serviços estão rodando: `docker-compose ps`
3. Reinicie os serviços: `docker-compose restart`
4. Consulte a documentação da API: `http://localhost:8000/docs`

---

**🎉 Parabéns! Seu sistema de e-commerce de livros com sistema de recomendação está funcionando!**
