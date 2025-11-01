"""
Utilitários compartilhados para os microserviços
"""
import httpx
from fastapi import HTTPException
from typing import Optional, Dict, Any
import logging
from core.config import settings

# Logger compartilhado
logger = logging.getLogger("core.utils")

# HTTP client compartilhado
http_client = httpx.AsyncClient()

async def get_current_user_id(token: str) -> int:
    """Extrai o ID do usuário do token JWT via auth service"""
    logger.debug("Extracting user ID from token")
    try:
        response = await http_client.post(
            f"{settings.AUTH_SERVICE_URL}/verify-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            user_id = data["user"]["id"]
            logger.debug(f"User ID extracted | user_id={user_id}")
            return user_id
        else:
            logger.warning(f"Token verification failed | status_code={response.status_code}")
            raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed | error={str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def verify_service_call(service_url: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
    """Faz chamada para outro serviço e retorna dados"""
    logger.debug(f"Service call | url={service_url} | endpoint={endpoint}")
    try:
        response = await http_client.get(f"{service_url}{endpoint}", **kwargs)
        if response.status_code == 200:
            logger.debug(f"Service call successful | url={service_url} | endpoint={endpoint}")
            return response.json()
        else:
            logger.warning(f"Service call failed | url={service_url} | endpoint={endpoint} | status={response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Service call failed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service unavailable | url={service_url} | endpoint={endpoint} | error={str(e)}")
        raise HTTPException(status_code=500, detail="Service unavailable")

async def verify_book_exists(book_id: int) -> Dict[Any, Any]:
    """Verifica se um livro existe no catálogo"""
    return await verify_service_call(settings.CATALOG_SERVICE_URL, f"/books/{book_id}")

async def verify_order_exists(order_id: int) -> Dict[Any, Any]:
    """Verifica se um pedido existe"""
    return await verify_service_call(settings.ORDERS_SERVICE_URL, f"/orders/{order_id}")

def create_error_response(message: str, status_code: int = 400) -> HTTPException:
    """Cria uma resposta de erro padronizada"""
    return HTTPException(status_code=status_code, detail=message)
