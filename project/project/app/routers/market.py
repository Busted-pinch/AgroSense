from fastapi import APIRouter
from models.schemas import MarketRequest, MarketOutput
from app.services.market_service import calc_market

router = APIRouter(prefix="/api/v1/market", tags=["Market"])

@router.post("/profit", response_model=MarketOutput)
def calc_profit(data: MarketRequest):
    profit, supply_status = calc_market(**data.dict())
    return {"profit": profit, "supply_status": supply_status}
