from fastapi import APIRouter

from ..cache.RedisController import RedisController
from ..models.api_models import CampaignCreate, Blacklist
from ..services.moderation_service import ModerationService

moderation_service = ModerationService()

rediscon = RedisController()
router = APIRouter()

@router.post("/campaigns", summary="Модерация рекламного объявления (кампании)", description="Модерация кампании перед ее созданием. Модерация осуществляется с помощью ИИ и черного списка, можно использовать как оба этих решения, так и каждое по отдельности.")
def llm_moderation(campaign_create: CampaignCreate, blacklist: bool=True, ai:bool=True):
    return moderation_service.llm_moderation(campaign_create, blacklist, ai)

@router.post("/blacklist", summary="Добавление blacklist", description="Добавление blacklist для модерации объявлений")
def add_blacklist(blacklist: Blacklist):
    return moderation_service.add_blacklist(blacklist)

@router.get("/blacklist", summary="Просмотр текущего blacklist", description="Просмотр всего blacklist для модерации")
def get_blacklist_words():
    return moderation_service.get_blacklist_words()