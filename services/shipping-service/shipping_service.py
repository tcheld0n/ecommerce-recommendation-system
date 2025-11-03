"""
Shipping Service - Cálculo de frete, criação e rastreamento de envios
Serviço simples (mock) com regras básicas de preço e prazos
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import math
import uuid

from core.config import settings
from core.logging import setup_logging

logger = setup_logging("shipping-service")

app = FastAPI(
    title="Shipping Service",
    description="Serviço de cálculo de frete e rastreamento",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== Models ======
class PackageItem(BaseModel):
    weight_kg: float = Field(..., gt=0)
    length_cm: float = Field(..., gt=0)
    width_cm: float = Field(..., gt=0)
    height_cm: float = Field(..., gt=0)
    quantity: int = Field(1, gt=0)

class QuoteRequest(BaseModel):
    destination_zip: str
    origin_zip: Optional[str] = None
    items: List[PackageItem]
    declared_value: Optional[float] = 0

class CarrierOption(BaseModel):
    carrier: str
    service: str
    price: float
    currency: str = "BRL"
    estimated_days: int
    estimated_delivery_date: datetime

class QuoteResponse(BaseModel):
    destination_zip: str
    options: List[CarrierOption]

class CreateShipmentRequest(BaseModel):
    order_id: str
    carrier: str
    service: str
    destination: Dict[str, Any]
    items: List[PackageItem]
    declared_value: Optional[float] = 0

class CreateShipmentResponse(BaseModel):
    tracking_code: str
    carrier: str
    service: str
    label_url: Optional[str] = None
    price: float
    currency: str = "BRL"
    estimated_delivery_date: datetime

class TrackingEvent(BaseModel):
    status: str
    location: Optional[str] = None
    timestamp: datetime

class TrackingResponse(BaseModel):
    tracking_code: str
    carrier: str
    service: str
    status: str
    history: List[TrackingEvent]
    estimated_delivery_date: datetime

# ====== In-memory store (mock) ======
SHIPMENTS: Dict[str, TrackingResponse] = {}

# ====== Pricing logic (mock) ======
CARRIERS = [
    {"carrier": "Correios", "service": "PAC", "base": 12.9, "per_kg": 6.5, "days": 7, "multiplier": 1.0},
    {"carrier": "Correios", "service": "SEDEX", "base": 19.9, "per_kg": 9.5, "days": 3, "multiplier": 1.25},
    {"carrier": "Jadlog", "service": "Expresso", "base": 16.9, "per_kg": 7.2, "days": 5, "multiplier": 1.1},
    {"carrier": "Azul Cargo", "service": "Aéreo", "base": 24.9, "per_kg": 10.0, "days": 2, "multiplier": 1.35},
]

REGION_DISTANCE_FACTOR = {
    "local": 1.0,  # mesmo estado
    "regional": 1.15,  # estados vizinhos
    "nacional": 1.3,  # demais estados
}


def estimate_distance_factor(origin_zip: Optional[str], destination_zip: str) -> float:
    if not destination_zip or len(destination_zip) < 2:
        return REGION_DISTANCE_FACTOR["nacional"]
    # Simplificação: comparar primeiros 2 dígitos
    if origin_zip and len(origin_zip) >= 2 and origin_zip[:2] == destination_zip[:2]:
        return REGION_DISTANCE_FACTOR["local"]
    # Também considerar 'regional' por um heurístico simples
    try:
        od = int(origin_zip[:2]) if origin_zip and len(origin_zip) >= 2 else None
        dd = int(destination_zip[:2])
        if od is not None and abs(od - dd) <= 3:
            return REGION_DISTANCE_FACTOR["regional"]
    except Exception:
        pass
    return REGION_DISTANCE_FACTOR["nacional"]


def calc_billable_weight(item: PackageItem) -> float:
    # Peso cúbico no padrão aéreo: (LxWxH)/6000 em kg
    volumetric = (item.length_cm * item.width_cm * item.height_cm) / 6000.0
    return max(item.weight_kg, volumetric)


def calc_total_weight(items: List[PackageItem]) -> float:
    total = 0.0
    for it in items:
        total += calc_billable_weight(it) * it.quantity
    return max(0.1, round(total, 3))


@app.post("/quote", response_model=QuoteResponse)
async def quote(req: QuoteRequest):
    if not req.items:
        raise HTTPException(status_code=400, detail="Itens são obrigatórios para cálculo de frete")

    weight = calc_total_weight(req.items)
    distance_factor = estimate_distance_factor(req.origin_zip, req.destination_zip)

    options: List[CarrierOption] = []
    for c in CARRIERS:
        price = (c["base"] + c["per_kg"] * weight) * distance_factor
        # Seguro simples sobre valor declarado
        if req.declared_value and req.declared_value > 0:
            price += 0.005 * float(req.declared_value)
        # Arredondar para 2 casas
        price = float(f"{price:.2f}")
        eta = datetime.utcnow() + timedelta(days=c["days"])  # estimativa simples
        options.append(CarrierOption(
            carrier=c["carrier"],
            service=c["service"],
            price=price,
            estimated_days=c["days"],
            estimated_delivery_date=eta,
        ))

    return QuoteResponse(destination_zip=req.destination_zip, options=options)


@app.post("/shipments", response_model=CreateShipmentResponse)
async def create_shipment(req: CreateShipmentRequest):
    # Recalcular preço aproximado com a mesma regra da cotação
    weight = calc_total_weight(req.items)
    distance_factor = estimate_distance_factor(None, req.destination.get("zip") or req.destination.get("cep") or "")

    carrier_rule = next((c for c in CARRIERS if c["carrier"] == req.carrier and c["service"] == req.service), None)
    if not carrier_rule:
        raise HTTPException(status_code=400, detail="Serviço de transporte inválido")

    price = (carrier_rule["base"] + carrier_rule["per_kg"] * weight) * distance_factor
    if req.declared_value and req.declared_value > 0:
        price += 0.005 * float(req.declared_value)
    price = float(f"{price:.2f}")

    tracking_code = f"SHIP-{uuid.uuid4().hex[:10].upper()}"
    eta = datetime.utcnow() + timedelta(days=carrier_rule["days"])

    # Persistir mock in-memory
    history = [
        TrackingEvent(status="Criado", location=req.destination.get("city", ""), timestamp=datetime.utcnow()),
    ]
    SHIPMENTS[tracking_code] = TrackingResponse(
        tracking_code=tracking_code,
        carrier=req.carrier,
        service=req.service,
        status="Criado",
        history=history,
        estimated_delivery_date=eta,
    )

    return CreateShipmentResponse(
        tracking_code=tracking_code,
        carrier=req.carrier,
        service=req.service,
        label_url=None,
        price=price,
        estimated_delivery_date=eta,
    )


@app.get("/track/{tracking_code}", response_model=TrackingResponse)
async def track(tracking_code: str):
    shipment = SHIPMENTS.get(tracking_code)
    if not shipment:
        # Retornar stub de rastreio não encontrado
        raise HTTPException(status_code=404, detail="Rastreamento não encontrado")
    return shipment


@app.get("/")
async def root():
    return {"message": "Shipping Service", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
