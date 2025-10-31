"""
Configuração de logging compartilhada para todos os serviços
"""
import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configura logging para um serviço específico
    
    Args:
        service_name: Nome do serviço (ex: "api-gateway", "auth-service")
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    # Criar logger com o nome do serviço
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Criar formatter com informações estruturadas
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para stdout (capturado pelo Docker)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para stderr (para erros e críticos)
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


def log_request(logger: logging.Logger, method: str, path: str, status_code: Optional[int] = None, **kwargs):
    """Log de requisição HTTP"""
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items() if v])
    status_info = f" | status={status_code}" if status_code else ""
    logger.info(f"REQUEST | {method} {path}{status_info} | {extra_info}")


def log_response(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: Optional[float] = None, **kwargs):
    """Log de resposta HTTP"""
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items() if v])
    duration_info = f" | duration={duration_ms}ms" if duration_ms else ""
    level = logging.WARNING if status_code >= 400 else logging.INFO
    logger.log(level, f"RESPONSE | {method} {path} | status={status_code}{duration_info} | {extra_info}")


def log_service_call(logger: logging.Logger, service_name: str, endpoint: str, method: str = "GET", status_code: Optional[int] = None, error: Optional[str] = None):
    """Log de chamada entre serviços"""
    status_info = f" | status={status_code}" if status_code else ""
    error_info = f" | error={error}" if error else ""
    logger.info(f"SERVICE_CALL | {method} {service_name}{endpoint}{status_info}{error_info}")


def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None):
    """Log de erro com contexto"""
    context_info = f" | context={context}" if context else ""
    logger.error(f"ERROR | {type(error).__name__}: {str(error)}{context_info}", exc_info=True)


def log_database_operation(logger: logging.Logger, operation: str, table: str, record_id: Optional[int] = None, **kwargs):
    """Log de operação de banco de dados"""
    id_info = f" | id={record_id}" if record_id else ""
    extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items() if v])
    logger.debug(f"DB | {operation} | table={table}{id_info} | {extra_info}")

