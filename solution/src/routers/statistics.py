from fastapi import APIRouter

from ..services.statistics_service import StatsService

stats_service = StatsService()

router = APIRouter()

@router.get("/campaigns/{campaignId}", summary="Получение статиcтики по рекламной кампании", description="Получение статиcтики по рекламной кампании (клики, показы, прибыль)")
def get_stats_campaign(campaignId: str):
    return stats_service.get_stats_campaign(campaignId)

@router.get("/campaigns/{campaignId}/daily", summary="Получение ежедневной статиcтики по рекламной кампании", description="Получение статиcтики по рекламной кампании (клики, показы, прибыль) списком по дням")
def get_stats_campaign_daily(campaignId: str):
    return stats_service.get_stats_campaign_daily(campaignId)

@router.get("/advertisers/{advertiserId}/campaigns", summary="Получение статиcтики по всем кампаниям рекламодателя", description="Возвращает сводную статистику по всем кампаниям рекламодателя")
def get_stats_advertisers(advertiserId: str):
    return stats_service.get_stats_advertisers(advertiserId)

@router.get("/advertisers/{advertiserId}/campaigns/daily", summary="Получение ежедневной статиcтики по всем кампаниям рекламодателя", description="Возвращает сводную статистику по всем кампаниям рекламодателя по дням")
def get_stats_advertisers_daily(advertiserId: str):
    return stats_service.get_stats_advertisers_daily(advertiserId)