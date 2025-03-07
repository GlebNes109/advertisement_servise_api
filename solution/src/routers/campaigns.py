from fastapi import APIRouter

from ..models.api_models import *
from ..services.campaign_service import CampaignService

router = APIRouter()
campaign_service = CampaignService()

@router.get("/{advertiserId}/campaigns", summary="Получение кампании", description="Получение кампаний с пагинацией")
def get_campaigns_pagination(advertiserId: str, size: int = 10, page: int = 1):
    return campaign_service.get_campaigns_pagination(advertiserId, size, page)

@router.post("/{advertiserId}/campaigns", summary="Добавление кампании", description="Добавление кампании")
def add_new_campaign(advertiserId: str, campaign_create: CampaignCreate):
    return campaign_service.add_new_campaign(advertiserId, campaign_create)

@router.get("/{advertiserId}/campaigns/{campaignId}", summary="Получение кампании", description="Получение кампании по id")
def get_campaign(advertiserId: str, campaignId: str):
    return campaign_service.get_campaign(advertiserId, campaignId)

@router.put("/{advertiserId}/campaigns/{campaignId}", tags=["Campaigns"], summary="Изменение кампании", description="Изменение кампании по id целиком")
def put_campaign(campaign: CampaignUpdate, advertiserId: str, campaignId: str):
    return campaign_service.put_campaign(campaign, advertiserId, campaignId)

@router.delete("/{advertiserId}/campaigns/{campaignId}", tags=["Campaigns"], summary="Удаление кампании", description="Удаление кампании")
def delete_campaign(advertiserId: str, campaignId: str):
    return campaign_service.delete_campaign(advertiserId, campaignId)

@router.get("/{advertiserId}/campaigns/{campaignId}/create-ai-text", tags=["Campaigns"], summary="Генерация текста для кампании", description="Возвращает несколько вариантов текста, сгенерированного ИИ, для рекламного объявления на основе данных о кампании и рекламодателе")
def llm_generate_text(advertiserId: str, campaignId: str):
    return campaign_service.llm_generate_text(advertiserId, campaignId)