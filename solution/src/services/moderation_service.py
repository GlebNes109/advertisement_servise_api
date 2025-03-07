from starlette.responses import JSONResponse

from .utility_service import make_http_error
from ..LLM.AIController import AIController
from ..cache.RedisController import RedisController
from ..db.repository import Repository
from ..models.api_models import *

dbcon = Repository()
rediscon =RedisController()
aicon = AIController()

class ModerationService:
    def llm_moderation(self, campaign_create: CampaignCreate, blacklist: bool = True, ai: bool = True):
        if ai:
            if aicon.moderate_text(campaign_create.ad_title + " " + campaign_create.ad_text) == 0:
                return make_http_error(400,
                                       "модерация не пройдена: содержание заголовка или текста рекламы некорректно (ai moderation).")
            if aicon.moderate_text(campaign_create.ad_title + " " + campaign_create.ad_text) == -1:
                return make_http_error(400,
                                       "Извините, AI модерация сейчас недоступна, рекомендуется ее отключить. Вместо нее воспользуйтесь модерацией по blacklist или попробуйте позже")
        if blacklist:
            if not rediscon.check_blacklist(campaign_create.ad_title) or not rediscon.check_blacklist(
                    campaign_create.ad_text):
                return make_http_error(400,
                                       "кампания не добавлена: содержание заголовка или текста рекламы некорректно (blacklist moderation)")

        return JSONResponse(status_code=200, content="модерация прошла успешно")

    def add_blacklist(self, blacklist: Blacklist):
        ban_words = blacklist.ban_words
        rediscon.add_blacklist(ban_words)
        return JSONResponse(status_code=200, content="blacklist добавлен")

    def get_blacklist_words(self):
        blacklist = rediscon.get_blacklist()
        return JSONResponse(status_code=200, content={"черный список слов": blacklist})
