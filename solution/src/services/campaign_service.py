from ..services.client_service import dbcon
from starlette.responses import JSONResponse, PlainTextResponse

from .utility_service import make_http_error
from ..LLM.AIController import AIController
from ..cache.RedisController import RedisController
from ..db.repository import Repository
from ..models.Model_converter import convert_to_apimodel
from ..models.api_models import *

dbcon = Repository()
rediscon =RedisController()
aicon = AIController()

class CampaignService:
    def add_new_campaign(self, advertiserId: str, campaign_create: CampaignCreate):
        # words = campaign_create.ad_title + " " + campaign_create.ad_text
        if dbcon.get_advertiser_by_id(advertiserId) is None:
            return make_http_error(404, "рекламодатель с таким id не найден")

        if rediscon.check_company_date(campaign_create.start_date, campaign_create.end_date):

            campaign_db = dbcon.add_campaign(advertiserId, campaign_create)
            campaign = convert_to_apimodel(campaign_db)

            print(f"AddCampaign {campaign_db}")

            return JSONResponse(status_code=200, content=campaign)

        else:
            return make_http_error(400, "дата неверная")


    def get_campaigns_pagination(self, advertiserId: str, size: int = 10, page: int = 1):
        if dbcon.get_advertiser_by_id(advertiserId) is None:
            return make_http_error(404, f"Рекламодатель с ид {advertiserId} не найден")

        limit = size
        offset = (page - 1) * size
        campaigns_db = dbcon.get_campaigns_with_pagination(advertiserId, limit, offset)
        campaigns_api = [convert_to_apimodel(campaign) for campaign in campaigns_db]
        return JSONResponse(status_code=200, content=campaigns_api)


    def get_campaign(self, advertiserId: str, campaignId: str):
        campaign_db = dbcon.get_campaign(campaignId)
        if campaign_db:
            campaign_api = convert_to_apimodel(campaign_db)
            return JSONResponse(status_code=200, content=campaign_api)

        else:
            return make_http_error(404, "кампания с такими данными не найдена")

    def put_campaign(self, campaign: CampaignUpdate, advertiserId: str, campaignId: str):
        campaign_db = dbcon.put_campaign(campaignId, advertiserId, campaign)
        if not rediscon.check_company_date(campaign.start_date, campaign.end_date):
            return make_http_error(400, "дата неверная")

        if campaign_db:
            campaign_api = convert_to_apimodel(campaign_db)
            return JSONResponse(status_code=200, content=campaign_api)

        else:
            return make_http_error(404, "кампания с такими данными не найдена")

    def delete_campaign(self, advertiserId: str, campaignId: str):
        if not dbcon.get_advertiser_by_id(advertiserId):
            return make_http_error(404, f"рекламодатель с Id {advertiserId} не найден")

        if dbcon.get_campaign(campaignId):
            dbcon.delete_campaign(campaignId)
            return PlainTextResponse(status_code=204)

        else:
            return make_http_error(404, "кампания с такими данными не найдена")

    def llm_generate_text(self, advertiserId: str, campaignId: str):
        campaign_db = dbcon.get_campaign(campaignId)
        advertiser_db = dbcon.get_advertiser_by_id(advertiserId)
        if not campaign_db or not advertiser_db:
            return make_http_error(404, "кампания с такими данными не существует")

        result = aicon.generate_text(campaign_db, advertiser_db)

        if result:
            return JSONResponse(status_code=200, content={"варианты рекламного объявления": result})

        else:
            return make_http_error(400,"Извините, AI генератор объявлений сейчас недоступен, проверьте настройки сети и прокси на сервере, а также текст вашего объявления на наличие некорректных слов (нейросеть может отказаться обработать текст если в нем есть мат или нарушение законов рф)")

