"""
Cart Service - Gerenciamento de Carrinho de Compras
Serviço simples e funcional para gerenciar carrinho de compras
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import httpx
import time

from core.config import settings
from core.database import get_db, engine, Base
from core.logging import setup_logging, log_request, log_response, log_error, log_database_operation, log_service_call
from models.cart import Cart, CartItem
from models.user import User
from models.book import Book  # Importar Book para garantir que a tabela seja criada
from schemas import cart as cart_schema
from schemas.cart import CartItemCreate, CartItemUpdate, CartItem as CartItemSchema

logger = setup_logging("cart-service")

# Criar tabelas do banco (importar Book garante que a tabela books seja criada)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cart Service",
    description="Serviço de gerenciamento de carrinho de compras",
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
        logger.error("Token não fornecido no cart service")
        raise credentials_exception
    
    try:
        # Tentar decodificar o token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": True})
        except JWTError as decode_error:
            # Se falhar, tentar sem verificar expiração para diagnóstico
            logger.warning(f"Token falhou na verificação normal no cart service | error={str(decode_error)}")
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
                logger.error("Token está EXPIRADO no cart service! Mas decodificando para debug")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado. Por favor, faça login novamente.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except JWTError:
                raise decode_error
        
        email: str = payload.get("sub")
        
        if email is None:
            logger.error("Token não contém email (sub) no cart service")
            raise credentials_exception
        
        logger.debug(f"Token decodificado no cart service | email={email}")
        
    except JWTError as e:
        error_msg = str(e)
        logger.error(f"Erro ao decodificar token JWT no cart service | error={error_msg} | token_preview={token[:20] if token else 'None'}...")
        
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
        logger.error(f"Erro inesperado ao validar token no cart service | error={str(e)}")
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.error(f"Usuário não encontrado no cart service | email={email}")
        raise credentials_exception
    
    logger.debug(f"Usuário autenticado no cart service | user_id={user.id} | email={email}")
    return user.id  # Retorna UUID diretamente

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "Cart Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Carrinho
@app.get("/cart")
async def get_cart(user_id = Depends(get_user_id), db: Session = Depends(get_db)):
    """Obter carrinho do usuário atual"""
    from sqlalchemy.orm import joinedload
    
    logger.info(f"Obtendo carrinho | user_id={user_id}")
    
    cart = db.query(Cart).options(joinedload(Cart.items)).filter(Cart.user_id == user_id).first()
    if not cart:
        # Criar carrinho vazio se não existir
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        log_database_operation(logger, "CREATE", "carts", cart.id, user_id=user_id)
        logger.info(f"Carrinho criado | cart_id={cart.id} | user_id={user_id}")
        return {
            "id": str(cart.id),
            "user_id": str(cart.user_id),
            "items": [],
            "total_items": 0,
            "total_amount": 0.0,
            "created_at": cart.created_at.isoformat() if hasattr(cart.created_at, 'isoformat') else str(cart.created_at),
            "updated_at": cart.updated_at.isoformat() if hasattr(cart.updated_at, 'isoformat') else str(cart.updated_at)
        }
    
    # Carregar informações dos livros para cada item
    items_with_book = []
    total_items = 0
    total_amount = 0.0
    
    for item in cart.items:
        book = db.query(Book).filter(Book.id == item.book_id).first()
        if book:
            subtotal = float(book.price) * item.quantity
            total_items += item.quantity
            total_amount += subtotal
            
            items_with_book.append({
                "id": str(item.id),
                "cart_id": str(item.cart_id),
                "book_id": str(item.book_id),
                "quantity": item.quantity,
                "created_at": item.created_at.isoformat() if hasattr(item.created_at, 'isoformat') else str(item.created_at),
                "updated_at": item.updated_at.isoformat() if hasattr(item.updated_at, 'isoformat') else str(item.updated_at),
                "book": {
                    "id": str(book.id),
                    "title": book.title,
                    "author": book.author,
                    "price": float(book.price),
                    "cover_image_url": book.cover_image_url or ""
                },
                "unit_price": float(book.price),
                "subtotal": subtotal
            })
    
    logger.info(f"Carrinho retornado | items={len(items_with_book)} | total={total_amount}")
    
    return {
        "id": str(cart.id),
        "user_id": str(cart.user_id),
        "items": items_with_book,
        "total_items": total_items,
        "total_amount": float(total_amount),
        "created_at": cart.created_at.isoformat() if hasattr(cart.created_at, 'isoformat') else str(cart.created_at),
        "updated_at": cart.updated_at.isoformat() if hasattr(cart.updated_at, 'isoformat') else str(cart.updated_at)
    }

@app.post("/cart/items", response_model=CartItemSchema, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item: CartItemCreate,
    user_id = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Adicionar item ao carrinho"""
    logger.info(f"Adicionando item ao carrinho | user_id={user_id} | book_id={item.book_id}")
    
    # Verificar se livro existe
    try:
        book_id_str = str(item.book_id)
        response = await http_client.get(f"{settings.CATALOG_SERVICE_URL}/books/{book_id_str}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Livro não encontrado")
        book_data = response.json()
        log_service_call(logger, "catalog", f"/books/{book_id_str}", "GET", 200)
    except httpx.RequestError as e:
        log_error(logger, e, f"verify_book | book_id={item.book_id}")
        raise HTTPException(status_code=503, detail="Serviço de catálogo indisponível")
    
    # Obter ou criar carrinho
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Verificar se item já existe no carrinho
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.book_id == item.book_id
    ).first()
    
    if existing_item:
        # Atualizar quantidade
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        log_database_operation(logger, "UPDATE", "cart_items", existing_item.id)
        logger.info(f"Item atualizado | item_id={existing_item.id}")
        return existing_item
    else:
        # Adicionar novo item
        # Nota: CartItem não tem campo price no modelo, o preço vem do Book
        cart_item = CartItem(
            cart_id=cart.id,
            book_id=item.book_id,
            quantity=item.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        log_database_operation(logger, "CREATE", "cart_items", cart_item.id)
        logger.info(f"Item adicionado | item_id={cart_item.id}")
        return cart_item

@app.put("/cart/items/{book_id}", response_model=CartItemSchema)
async def update_cart_item(
    book_id: str,
    item_update: CartItemUpdate,
    user_id = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Atualizar quantidade de item no carrinho"""
    from uuid import UUID
    
    logger.info(f"Atualizando item | user_id={user_id} | book_id={book_id} | quantity={item_update.quantity}")
    
    try:
        book_uuid = UUID(book_id)
    except ValueError as e:
        logger.error(f"ID de livro inválido | book_id={book_id} | error={str(e)}")
        raise HTTPException(status_code=400, detail="ID de livro inválido")
    
    # Validar quantidade
    if item_update.quantity <= 0:
        logger.error(f"Quantidade inválida | quantity={item_update.quantity}")
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        logger.warning(f"Carrinho não encontrado | user_id={user_id}")
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.book_id == book_uuid
    ).first()
    
    if not cart_item:
        logger.warning(f"Item não encontrado no carrinho | user_id={user_id} | book_id={book_id}")
        raise HTTPException(status_code=404, detail="Item não encontrado no carrinho")
    
    try:
        cart_item.quantity = item_update.quantity
        db.commit()
        db.refresh(cart_item)
        log_database_operation(logger, "UPDATE", "cart_items", cart_item.id)
        logger.info(f"Item atualizado | item_id={cart_item.id} | new_quantity={cart_item.quantity}")
        return cart_item
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar item do carrinho | item_id={cart_item.id} | error={str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar item do carrinho")

@app.delete("/cart/items/{book_id}")
async def remove_from_cart(
    book_id: str,
    user_id = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """Remover item do carrinho"""
    from uuid import UUID
    
    logger.info(f"Removendo item | user_id={user_id} | book_id={book_id}")
    
    try:
        book_uuid = UUID(book_id)
    except ValueError as e:
        logger.error(f"ID de livro inválido | book_id={book_id} | error={str(e)}")
        raise HTTPException(status_code=400, detail="ID de livro inválido")
    
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        logger.warning(f"Carrinho não encontrado | user_id={user_id}")
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    
    # Buscar item no carrinho
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.book_id == book_uuid
    ).first()
    
    if not cart_item:
        logger.warning(f"Item não encontrado no carrinho | user_id={user_id} | book_id={book_id} | cart_id={cart.id}")
        # Listar itens do carrinho para debug
        all_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
        logger.debug(f"Itens no carrinho: {[str(item.book_id) for item in all_items]}")
        raise HTTPException(status_code=404, detail="Item não encontrado no carrinho")
    
    try:
        db.delete(cart_item)
        db.commit()
        log_database_operation(logger, "DELETE", "cart_items", cart_item.id)
        logger.info(f"Item removido com sucesso | item_id={cart_item.id} | book_id={book_id} | user_id={user_id}")
        return {"message": "Item removido com sucesso"}
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao remover item do carrinho | item_id={cart_item.id} | error={str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao remover item do carrinho")

@app.delete("/cart")
async def clear_cart(user_id = Depends(get_user_id), db: Session = Depends(get_db)):
    """Limpar carrinho"""
    logger.info(f"Limpando carrinho | user_id={user_id}")
    
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
        logger.info(f"Carrinho limpo | user_id={user_id}")
    
    return {"message": "Carrinho limpo com sucesso"}

@app.get("/cart/summary")
async def get_cart_summary(user_id = Depends(get_user_id), db: Session = Depends(get_db)):
    """Obter resumo do carrinho"""
    logger.info(f"Obtendo resumo do carrinho | user_id={user_id}")
    
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart or not cart.items:
        return {
            "total_items": 0,
            "total_price": 0.0,
            "items": []
        }
    
    # Carregar informações do livro para obter o preço
    from sqlalchemy.orm import joinedload
    
    total_items = sum(item.quantity for item in cart.items)
    
    # Calcular total buscando preços dos livros
    total_price = 0.0
    for item in cart.items:
        book = db.query(Book).filter(Book.id == item.book_id).first()
        if book:
            total_price += float(book.price) * item.quantity
    
    # Preparar itens com informações dos livros
    items_data = []
    for item in cart.items:
        book = db.query(Book).filter(Book.id == item.book_id).first()
        if book:
            items_data.append({
                "book_id": str(item.book_id),
                "quantity": item.quantity,
                "price": float(book.price),
                "subtotal": float(book.price) * item.quantity
            })
    
    return {
        "total_items": total_items,
        "total_price": total_price,
        "items": items_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
