from fastapi import APIRouter
from sqlalchemy.sql.visitors import replacement_traverse

from ..models.api_models import *
from ..services.advertiser_service import AdvertiserService

router = APIRouter()
adv_service = AdvertiserService()

@router.post("/bulk", summary="Добавление рекламодателей", description="Массовое добавление рекламодателей в бд")
def add_advs(advs: list[AdvertiserUpsert]):
    return adv_service.add_advs(advs)

@router.get("/{advertiserId}", summary="Получение рекламодателя", description="Получение рекламодателя по id")
def get_client(advertiserId: str):
    return adv_service.get_advertiser(advertiserId)