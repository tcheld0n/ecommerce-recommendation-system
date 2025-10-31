"""
Payment Service - Processamento de Pagamentos
Serviço simples e funcional para processar pagamentos
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import uuid
import time

from core.config import settings
from core.logging import setup_logging, log_request, log_response, log_error

logger = setup_logging("payment-service")

app = FastAPI(
    title="Payment Service",
    description="Serviço de processamento de pagamentos",
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

# Endpoints básicos
@app.get("/")
async def root():
    return {"message": "Payment Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Pagamentos
@app.post("/payments")
async def process_payment(payment_data: dict):
    """Processar pagamento"""
    order_id = payment_data.get("order_id")
    amount = payment_data.get("amount", 0)
    
    logger.info(f"Processando pagamento | order_id={order_id} | amount={amount}")
    
    # Simulação de processamento
    payment_id = str(uuid.uuid4())
    
    logger.info(f"Pagamento processado | payment_id={payment_id} | order_id={order_id}")
    return {
        "payment_id": payment_id,
        "status": "completed",
        "amount": amount,
        "order_id": order_id,
        "message": "Pagamento processado com sucesso"
    }

@app.get("/payment-methods")
async def get_payment_methods():
    """Obter métodos de pagamento disponíveis"""
    return [
        {
            "id": 1,
            "type": "credit_card",
            "name": "Cartão de Crédito",
            "enabled": True
        },
        {
            "id": 2,
            "type": "bank_transfer",
            "name": "Transferência Bancária",
            "enabled": True
        }
    ]

@app.post("/payment-methods")
async def create_payment_method(payment_method: dict):
    """Criar método de pagamento"""
    return {
        "id": uuid.uuid4().int % 10000,
        "type": payment_method.get("type", "credit_card"),
        "message": "Método de pagamento criado com sucesso"
    }

@app.get("/payments/{payment_id}")
async def get_payment(payment_id: str):
    """Obter informações de pagamento"""
    return {
        "payment_id": payment_id,
        "status": "completed",
        "message": "Informações do pagamento"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
