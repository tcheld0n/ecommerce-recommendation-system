"""
API Gateway - Orquestração de Microsserviços
Gateway simples e funcional para rotear requisições aos serviços
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
import os
import time

try:
    from core.config import settings
    from core.logging import setup_logging, log_request, log_response, log_service_call, log_error
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
    from core.config import settings
    from core.logging import setup_logging, log_request, log_response, log_service_call, log_error

logger = setup_logging("api-gateway")

app = FastAPI(
    title="E-commerce API Gateway",
    description="API Gateway para orquestração de microsserviços",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
uploads_dir = os.path.join(os.getcwd(), "uploads")
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# HTTP client
http_client = httpx.AsyncClient()

# Service URLs
SERVICE_URLS = {
    "catalog": settings.CATALOG_SERVICE_URL,
    "auth": settings.AUTH_SERVICE_URL,
    "users": settings.USERS_SERVICE_URL,
    "cart": settings.CART_SERVICE_URL,
    "orders": settings.ORDERS_SERVICE_URL,
    "payment": settings.PAYMENT_SERVICE_URL,
    "recommendation": settings.RECOMMENDATION_SERVICE_URL,
}

# Middleware de logging
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Middleware para logar todas as requisições"""
    start_time = time.time()
    method = request.method
    path = request.url.path
    
    log_request(logger, method, path, client_ip=request.client.host if request.client else None)
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        log_response(logger, method, path, response.status_code, duration_ms)
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_error(logger, e, f"{method} {path}")
        log_response(logger, method, path, 500, duration_ms, error=str(e))
        raise

# Helper: fazer chamada a serviço
async def call_service(service_name: str, method: str, endpoint: str, **kwargs):
    """Fazer chamada a um serviço"""
    if service_name not in SERVICE_URLS:
        raise HTTPException(status_code=500, detail=f"Serviço desconhecido: {service_name}")
    
    service_url = SERVICE_URLS[service_name]
    if not service_url:
        logger.error(f"URL do serviço não configurada | service={service_name}")
        raise HTTPException(status_code=500, detail=f"Serviço {service_name} não configurado")
    
    url = f"{service_url}{endpoint}"
    logger.debug(f"Chamando serviço | service={service_name} | url={url} | method={method} | endpoint={endpoint}")
    
    try:
        response = await http_client.request(method, url, timeout=30.0, **kwargs)
        log_service_call(logger, service_name, endpoint, method, response.status_code)
        
        if response.status_code == 404:
            logger.error(f"Endpoint não encontrado | service={service_name} | endpoint={endpoint} | url={url} | service_url={service_url}")
            # Não levantar erro aqui para refresh token - deixar tentar endpoint alternativo
            raise HTTPException(status_code=404, detail=f"Endpoint não encontrado: {endpoint}")
        
        if response.status_code >= 400:
            try:
                error_detail = response.json().get("detail", response.text)
            except:
                error_detail = response.text or "Erro desconhecido"
            logger.error(f"Erro do serviço | service={service_name} | status={response.status_code} | detail={error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        return response.json()
    except HTTPException:
        raise
    except httpx.TimeoutException:
        log_error(logger, Exception("Timeout"), f"{service_name}{endpoint}")
        raise HTTPException(status_code=504, detail="Timeout do serviço")
    except httpx.RequestError as e:
        logger.error(f"Erro de conexão com serviço | service={service_name} | endpoint={endpoint} | url={url} | error={str(e)}")
        log_error(logger, e, f"{service_name}{endpoint}")
        raise HTTPException(status_code=503, detail=f"Serviço {service_name} indisponível: {str(e)}")
    except Exception as e:
        log_error(logger, e, f"{service_name}{endpoint}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

# Endpoints básicos
@app.get("/")
async def root():
    return {
        "message": "E-commerce API Gateway",
        "version": "1.0.0",
        "services": list(SERVICE_URLS.keys())
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ========== CATALOG SERVICE ROUTES ==========
@app.get("/api/v1/books")
async def get_books(skip: int = 0, limit: int = 100, category_id: int = None, search: str = None):
    """Listar livros"""
    params = {"skip": skip, "limit": limit}
    if category_id:
        params["category_id"] = category_id
    if search:
        params["search"] = search
    return await call_service("catalog", "GET", "/books", params=params)

@app.get("/api/v1/books/popular")
async def get_popular_books(limit: int = 10):
    """Obter livros populares"""
    return await call_service("catalog", "GET", "/books/popular", params={"limit": limit})

@app.get("/api/v1/books/recent")
async def get_recent_books(limit: int = 10):
    """Obter livros recentes"""
    return await call_service("catalog", "GET", "/books/recent", params={"limit": limit})

@app.get("/api/v1/books/{book_id}")
async def get_book(book_id: str):
    """Obter livro específico"""
    return await call_service("catalog", "GET", f"/books/{book_id}")

@app.post("/api/v1/books")
async def create_book(book_data: dict):
    """Criar livro"""
    return await call_service("catalog", "POST", "/books", json=book_data)

@app.put("/api/v1/books/{book_id}")
async def update_book(book_id: str, book_data: dict):
    """Atualizar livro"""
    return await call_service("catalog", "PUT", f"/books/{book_id}", json=book_data)

@app.delete("/api/v1/books/{book_id}")
async def delete_book(book_id: str):
    """Deletar livro"""
    return await call_service("catalog", "DELETE", f"/books/{book_id}")

@app.get("/api/v1/categories")
async def get_categories():
    """Listar categorias"""
    return await call_service("catalog", "GET", "/categories")

# ========== AUTH SERVICE ROUTES ==========
@app.post("/api/v1/auth/register")
async def register(user_data: dict):
    """Registrar usuário"""
    required_fields = ["email", "password", "full_name"]
    missing = [f for f in required_fields if f not in user_data or not user_data[f]]
    if missing:
        raise HTTPException(status_code=400, detail=f"Campos obrigatórios: {', '.join(missing)}")
    
    return await call_service("auth", "POST", "/register", json=user_data)

@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    """Fazer login"""
    form_data = {
        "username": credentials.get("username") or credentials.get("email"),
        "password": credentials.get("password")
    }
    if not form_data["username"] or not form_data["password"]:
        raise HTTPException(status_code=400, detail="Email/senha obrigatórios")
    
    return await call_service("auth", "POST", "/login", data=form_data)

@app.get("/api/v1/auth/me")
async def get_current_auth_user(request: Request):
    """Obter usuário atual do auth service"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token de autenticação necessário")
    
    headers = {"Authorization": authorization}
    return await call_service("auth", "GET", "/me", headers=headers)

@app.post("/api/v1/auth/refresh")
async def refresh_token(request: Request):
    """Renovar token usando refresh token"""
    try:
        body = await request.json()
        if not body.get("refresh_token"):
            raise HTTPException(status_code=400, detail="Refresh token é obrigatório")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao parsear body do refresh token | error={str(e)}")
        raise HTTPException(status_code=400, detail="Refresh token é obrigatório")
    
    logger.info(f"Recebendo requisição de refresh token | auth_url={SERVICE_URLS.get('auth')}")
    
    try:
        # Tentar primeiro com /refresh-token, se falhar tentar /refresh
        try:
            logger.info(f"Tentando refresh token via /refresh-token | auth_service_url={SERVICE_URLS.get('auth')}")
            result = await call_service("auth", "POST", "/refresh-token", json=body)
            logger.info("Refresh token processado com sucesso via /refresh-token")
            return result
        except HTTPException as e:
            if e.status_code == 404:
                logger.warning(f"Endpoint /refresh-token não encontrado (404), tentando /refresh | auth_service_url={SERVICE_URLS.get('auth')}")
                try:
                    # Tentar endpoint alternativo
                    result = await call_service("auth", "POST", "/refresh", json=body)
                    logger.info("Refresh token processado com sucesso via /refresh")
                    return result
                except HTTPException as e2:
                    if e2.status_code == 404:
                        logger.error(f"Ambos os endpoints de refresh retornaram 404 | auth_service_url={SERVICE_URLS.get('auth')} | verifique se o auth service está rodando")
                        raise HTTPException(
                            status_code=503, 
                            detail=f"Serviço de autenticação indisponível. Verifique se o auth service está rodando em {SERVICE_URLS.get('auth')}"
                        )
                    else:
                        raise
            else:
                raise
    except HTTPException as e:
        logger.error(f"Erro ao processar refresh token | status={e.status_code} | detail={e.detail} | auth_service_url={SERVICE_URLS.get('auth')}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao processar refresh token | error={str(e)} | auth_service_url={SERVICE_URLS.get('auth')}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar refresh token: {str(e)}")

@app.post("/api/v1/auth/refresh-token")
async def refresh_token_legacy(request: Request):
    """Renovar token (endpoint legado)"""
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Refresh token é obrigatório")
    
    # Chamar o serviço de auth passando o body com refresh_token
    return await call_service("auth", "POST", "/refresh-token", json=body)

# ========== USERS SERVICE ROUTES ==========
@app.get("/api/v1/users/me")
async def get_current_user(request: Request):
    """Obter perfil do usuário"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("users", "GET", "/users/me", headers=headers)

@app.put("/api/v1/users/me")
async def update_current_user(user_data: dict, request: Request):
    """Atualizar perfil"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("users", "PUT", "/users/me", json=user_data, headers=headers)

@app.get("/api/v1/users/me/addresses")
async def get_user_addresses(request: Request):
    """Obter endereços"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("users", "GET", "/users/me/addresses", headers=headers)

# ========== CART SERVICE ROUTES ==========
@app.get("/api/v1/cart")
async def get_cart(request: Request):
    """Obter carrinho"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("cart", "GET", "/cart", headers=headers)

@app.post("/api/v1/cart/items")
async def add_to_cart(item_data: dict, request: Request):
    """Adicionar item ao carrinho"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("cart", "POST", "/cart/items", json=item_data, headers=headers)

@app.put("/api/v1/cart/items/{book_id}")
async def update_cart_item(book_id: str, item_data: dict, request: Request):
    """Atualizar item do carrinho"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("cart", "PUT", f"/cart/items/{book_id}", json=item_data, headers=headers)

@app.delete("/api/v1/cart/items/{book_id}")
async def remove_from_cart(book_id: str, request: Request):
    """Remover item do carrinho"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("cart", "DELETE", f"/cart/items/{book_id}", headers=headers)

@app.delete("/api/v1/cart")
async def clear_cart(request: Request):
    """Limpar carrinho"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("cart", "DELETE", "/cart", headers=headers)

@app.get("/api/v1/cart/summary")
async def get_cart_summary(request: Request):
    """Obter resumo do carrinho"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("cart", "GET", "/cart/summary", headers=headers)

# ========== ORDERS SERVICE ROUTES ==========
@app.post("/api/v1/orders")
async def create_order(order_data: dict, request: Request):
    """Criar pedido"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("orders", "POST", "/orders", json=order_data, headers=headers)

@app.get("/api/v1/orders")
async def get_orders(request: Request, skip: int = 0, limit: int = 100, status_filter: str = None):
    """Listar pedidos"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    params = {"skip": skip, "limit": limit}
    if status_filter:
        params["status_filter"] = status_filter
    return await call_service("orders", "GET", "/orders", params=params, headers=headers)

@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: int, request: Request):
    """Obter pedido específico"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("orders", "GET", f"/orders/{order_id}", headers=headers)

@app.post("/api/v1/orders/{order_id}/cancel")
async def cancel_order(order_id: int, request: Request):
    """Cancelar pedido"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Token necessário")
    headers = {"Authorization": authorization}
    return await call_service("orders", "POST", f"/orders/{order_id}/cancel", headers=headers)

# ========== PAYMENT SERVICE ROUTES ==========
@app.post("/api/v1/payments")
async def process_payment(payment_data: dict):
    """Processar pagamento"""
    return await call_service("payment", "POST", "/payments", json=payment_data)

@app.get("/api/v1/payment-methods")
async def get_payment_methods():
    """Obter métodos de pagamento"""
    return await call_service("payment", "GET", "/payment-methods")

# ========== RECOMMENDATION SERVICE ROUTES ==========
@app.get("/api/v1/recommendations")
async def get_recommendations(request: Request, limit: int = 10):
    """Obter recomendações"""
    authorization = request.headers.get("Authorization")
    headers = {"Authorization": authorization} if authorization else {}
    return await call_service("recommendation", "GET", "/recommendations", params={"limit": limit}, headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
