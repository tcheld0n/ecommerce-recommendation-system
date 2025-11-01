"""
Orders Service - Gerenciamento de Pedidos
Serviço simples e funcional para gerenciar pedidos
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import time
from jose import JWTError, jwt

from core.config import settings
from core.database import get_db, engine, Base
from core.logging import setup_logging, log_request, log_response, log_error, log_database_operation, log_service_call
from models.order import Order, OrderItem
from models.user import User
from schemas.order import OrderCreate, OrderUpdate, Order as OrderSchema, OrderItem as OrderItemSchema

logger = setup_logging("orders-service")

# Criar tabelas do banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Orders Service",
    description="Serviço de gerenciamento de pedidos",
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

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# HTTP client
http_client = httpx.AsyncClient()

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

# Dependency: obter user_id do token
async def get_user_id(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obter user_id do token JWT diretamente"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        logger.error("Token não fornecido")
        raise credentials_exception
    
    try:
        # Tentar decodificar o token sem verificar expiração primeiro para debug
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": True})
        except JWTError as decode_error:
            # Se falhar, tentar sem verificar expiração para ver se o problema é a expiração
            logger.warning(f"Token falhou na verificação normal | error={str(decode_error)}")
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
                logger.error("Token está EXPIRADO! Mas decodificando para debug")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado. Por favor, faça login novamente.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except JWTError:
                # Se ainda falhar, o problema é outro (SECRET_KEY diferente, formato, etc)
                raise decode_error
        
        email: str = payload.get("sub")
        
        if email is None:
            logger.error("Token não contém email (sub)")
            raise credentials_exception
            
        # Não verificar tipo do token - aceitar tanto access quanto refresh se necessário
        token_type = payload.get("type")
        logger.debug(f"Token decodificado | email={email} | type={token_type}")
        
    except JWTError as e:
        error_msg = str(e)
        logger.error(f"Erro ao decodificar token JWT | error={error_msg} | token_length={len(token) if token else 0}")
        
        # Mensagens de erro mais específicas
        if "expired" in error_msg.lower() or "exp" in error_msg.lower():
            detail = "Token expirado. Por favor, faça login novamente."
        elif "signature" in error_msg.lower():
            detail = "Token com assinatura inválida. Verifique SECRET_KEY."
        else:
            detail = f"Token inválido: {error_msg}"
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Erro inesperado ao validar token | error={str(e)}")
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.error(f"Usuário não encontrado | email={email}")
        raise credentials_exception
    
    logger.debug(f"Usuário autenticado | user_id={user.id} | email={email}")
    return user.id  # Retorna UUID diretamente

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "Orders Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Pedidos
@app.post("/orders", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    user_id = Depends(get_user_id),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Criar novo pedido do carrinho"""
    logger.info(f"Criando pedido | user_id={user_id} | token_present={bool(token)}")
    
    # Obter resumo do carrinho passando o token de autenticação
    try:
        if not token:
            logger.error("Token não disponível para chamar cart service")
            raise HTTPException(status_code=401, detail="Token de autenticação necessário")
            
        headers = {"Authorization": f"Bearer {token}"}
        logger.debug(f"Chamando cart service | url={settings.CART_SERVICE_URL}/cart/summary")
        
        response = await http_client.get(
            f"{settings.CART_SERVICE_URL}/cart/summary",
            headers=headers
        )
        
        logger.debug(f"Resposta do cart service | status_code={response.status_code}")
        
        if response.status_code == 401:
            logger.error("Cart service retornou 401 - token inválido")
            raise HTTPException(status_code=401, detail="Token inválido para acesso ao carrinho")
        elif response.status_code != 200:
            logger.error(f"Erro ao obter carrinho | status_code={response.status_code} | response={response.text[:200]}")
            raise HTTPException(status_code=400, detail="Não foi possível obter carrinho")
            
        try:
            cart_data = response.json()
            logger.debug(f"Dados do carrinho recebidos | items_count={len(cart_data.get('items', []))} | total_price={cart_data.get('total_price')}")
        except Exception as json_error:
            logger.error(f"Erro ao parsear JSON do carrinho | response_text={response.text[:500]} | error={str(json_error)}")
            raise HTTPException(status_code=500, detail=f"Erro ao processar resposta do carrinho: {str(json_error)}")
        
        log_service_call(logger, "cart", "/cart/summary", "GET", 200)
    except httpx.RequestError as e:
        log_error(logger, e, "get_cart_summary")
        raise HTTPException(status_code=503, detail="Serviço de carrinho indisponível")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter carrinho | error={str(e)} | type={type(e).__name__}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao obter carrinho: {str(e)}")
    
    if not cart_data.get("items"):
        logger.warning(f"Carrinho vazio | cart_data={cart_data}")
        raise HTTPException(status_code=400, detail="Carrinho vazio")
    
    # Preparar itens do pedido
    from uuid import UUID as UUIDType
    
    order_items_data = []
    for item in cart_data["items"]:
        try:
            # Converter book_id para UUID se for string
            book_id = item["book_id"]
            if isinstance(book_id, str):
                book_id = UUIDType(book_id)
            
            order_items_data.append({
                "book_id": book_id,
                "quantity": item["quantity"],
                "unit_price": item["price"]
            })
        except (ValueError, TypeError) as e:
            logger.error(f"Erro ao processar item do carrinho | item={item} | error={str(e)}")
            raise HTTPException(status_code=400, detail=f"ID de livro inválido: {item.get('book_id')}")
    
    # Criar pedido
    try:
        shipping_address = {}
        payment_method = "credit_card"
        
        if hasattr(order_data, 'shipping_address') and order_data.shipping_address:
            shipping_address = order_data.shipping_address
        elif isinstance(order_data, dict) and 'shipping_address' in order_data:
            shipping_address = order_data['shipping_address']
        
        if hasattr(order_data, 'payment_method') and order_data.payment_method:
            payment_method = order_data.payment_method
        elif isinstance(order_data, dict) and 'payment_method' in order_data:
            payment_method = order_data['payment_method']
        
        logger.debug(f"Criando pedido no banco | user_id={user_id} | total_amount={cart_data.get('total_price', 0)}")
        
        order = Order(
            user_id=user_id,
            status="pending",
            total_amount=cart_data.get("total_price", 0),
            shipping_address=shipping_address,
            payment_method=payment_method
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        log_database_operation(logger, "CREATE", "orders", order.id, user_id=user_id)
        logger.info(f"Pedido criado no banco | order_id={order.id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar pedido no banco | error={str(e)} | type={type(e).__name__}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao criar pedido: {str(e)}")
    
    # Criar itens do pedido
    try:
        logger.debug(f"Criando {len(order_items_data)} itens do pedido")
        for item_data in order_items_data:
            subtotal = item_data["quantity"] * item_data["unit_price"]
            order_item = OrderItem(
                order_id=order.id,
                book_id=item_data["book_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=subtotal
            )
            db.add(order_item)
        db.commit()
        logger.info(f"Itens do pedido criados | order_id={order.id} | items_count={len(order_items_data)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar itens do pedido | order_id={order.id} | error={str(e)} | type={type(e).__name__}", exc_info=True)
        # Tentar deletar o pedido criado
        try:
            db.delete(order)
            db.commit()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Erro ao criar itens do pedido: {str(e)}")
    
    # Limpar carrinho passando o token de autenticação
    try:
        headers = {"Authorization": f"Bearer {token}"}
        await http_client.delete(
            f"{settings.CART_SERVICE_URL}/cart",
            headers=headers
        )
        log_service_call(logger, "cart", "/cart", "DELETE", 200)
    except Exception as e:
        # Não falhar o pedido se não conseguir limpar o carrinho
        logger.warning(f"Erro ao limpar carrinho após criar pedido | error={str(e)}")
        pass
    
    logger.info(f"Pedido criado com sucesso | order_id={order.id} | user_id={user_id}")
    
    # Recarregar o pedido com os itens e books relacionados para retornar resposta completa
    try:
        from sqlalchemy.orm import joinedload
        
        # Recarregar o pedido com relacionamentos usando eager loading
        order_with_items = db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.book)
        ).filter(Order.id == order.id).first()
        
        if not order_with_items:
            logger.warning(f"Pedido não encontrado após recarregamento | order_id={order.id}")
            # Recarregar o pedido básico
            db.refresh(order)
            return order
        
        logger.debug(f"Retornando pedido com itens | order_id={order_with_items.id} | items_count={len(order_with_items.items)}")
        
        # O schema OrderItemWithBook agora aceita objetos ORM diretamente
        # graças ao from_attributes=True e ao uso de BookSchema
        return order_with_items
        
    except Exception as e:
        logger.error(f"Erro ao recarregar pedido | order_id={order.id} | error={str(e)}", exc_info=True)
        # Retornar pedido básico em caso de erro
        db.refresh(order)
        return order

@app.get("/orders", response_model=List[OrderSchema])
async def get_user_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    user_id = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Obter pedidos do usuário atual"""
    logger.info(f"Obtendo pedidos | user_id={user_id}")
    
    query = db.query(Order).filter(Order.user_id == user_id)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: str,
    user_id = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Obter pedido específico"""
    from uuid import UUID as UUIDType
    
    logger.info(f"Obtendo pedido | order_id={order_id} | user_id={user_id}")
    
    try:
        order_uuid = UUIDType(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    
    order = db.query(Order).filter(Order.id == order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    return order

@app.put("/orders/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    user_id = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Atualizar pedido"""
    from uuid import UUID as UUIDType
    
    logger.info(f"Atualizando pedido | order_id={order_id} | user_id={user_id}")
    
    try:
        order_uuid = UUIDType(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    
    order = db.query(Order).filter(Order.id == order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Apenas permitir cancelamento
    if order_update.status and order_update.status != "cancelled":
        raise HTTPException(status_code=400, detail="Status inválido")
    
    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(order, key, value)
    
    db.commit()
    db.refresh(order)
    log_database_operation(logger, "UPDATE", "orders", order_id)
    return order

@app.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    user_id = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Cancelar pedido"""
    from uuid import UUID as UUIDType
    
    logger.info(f"Cancelando pedido | order_id={order_id} | user_id={user_id}")
    
    try:
        order_uuid = UUIDType(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    
    order = db.query(Order).filter(Order.id == order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(status_code=400, detail="Pedido não pode ser cancelado")
    
    order.status = "cancelled"
    db.commit()
    log_database_operation(logger, "UPDATE", "orders", order_id, status="cancelled")
    return {"message": "Pedido cancelado com sucesso"}

@app.get("/orders/{order_id}/items", response_model=List[OrderItemSchema])
async def get_order_items(
    order_id: str,
    user_id = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Obter itens do pedido"""
    from uuid import UUID as UUIDType
    
    try:
        order_uuid = UUIDType(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    
    order = db.query(Order).filter(Order.id == order_uuid).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    return order.items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
