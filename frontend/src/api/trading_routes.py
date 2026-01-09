from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.services.execution.order_gateway import order_gateway
from src.services.risk.pre_flight_validator import validator

router = APIRouter(prefix="/trading", tags=["Trading"])

class OrderRequest(BaseModel):
    symbol: str
    action: str # BUY/SELL
    quantity: int
    price: float = 0.0
    order_type: str = "LMT"
    source: str = "MANUAL_USER"

@router.post("/order")
async def submit_order(order: OrderRequest):
    # 1. Pre-Flight Validation
    # Mocking market price/NAV for this endpoint context
    # In production, these would come from the Market Data Service and Account Service
    market_price = order.price if order.price > 0 else 100.0 
    nav = 100000.0

    validation = await validator.validate(order.dict(), market_price, nav)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["reason"])

    # 2. Submit to Gateway
    result = await order_gateway.submit_order(order.dict())

    if result["status"] == "REJECTED":
        raise HTTPException(status_code=403, detail=result["reason"])

    return result
