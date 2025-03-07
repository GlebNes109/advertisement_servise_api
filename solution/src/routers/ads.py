from fastapi import APIRouter

from ..models.api_models import Click_clientId
from ..services.ads_service import AdsService

router = APIRouter()
ads_service = AdsService()

@router.get("", summary="Получение рекламного объявления", description="Получение рекламного объявления для клиента с учетом таргетирования")
def get_ads(client_id: str):
    return ads_service.get_ads(client_id)

@router.post("/{adId}/click", summary="Клик по рекламному объявлению", description="Клик клиента по рекламному объявлению")
def add_click(adId: str, adClick: Click_clientId):
    return ads_service.add_click(adId, adClick)