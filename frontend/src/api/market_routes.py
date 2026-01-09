from fastapi import APIRouter, HTTPException
from src.adapters.thetadata_adapter import theta_adapter

router = APIRouter(prefix="/market", tags=["Market Data"])

@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    quote = await theta_adapter.get_stock_price(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found or market closed")
    return quote
