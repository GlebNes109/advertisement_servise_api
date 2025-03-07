from fastapi import Depends
from starlette.responses import JSONResponse, PlainTextResponse

from .utility_service import make_http_error
from ..cache.RedisController import RedisController
from ..db.repository import Repository
from ..models.api_models import *

dbcon = Repository()
rediscon = RedisController()

class AdsService:
    def get_ads(self, client_id: str):
        curday = rediscon.get_day()
        res = dbcon.get_ad(client_id, curday)

        if res is None:
            print(f"ImpTrouble client_id: {client_id} curday: {curday}")
            return make_http_error(404, "Adv for client not found")

        ad = Ad(ad_id=res.campaign_id, ad_title=res.ad_title, ad_text=res.ad_text, advertiser_id=res.advertiser_id)

        return JSONResponse(status_code=200, content=ad.model_dump())

    def add_click(self, adId: str, adClick: Click_clientId):
        curday = rediscon.get_day()
        client_id = adClick.client_id
        campaign_db = dbcon.get_campaign(adId)
        if campaign_db is None:
            # print(f"ClickTrouble client_id: {client_id} advId: {adId} curday: {curday} campaign: {campaign_db} не найдено")
            return make_http_error(404, f"Рекламное объявление с ID {adId} не найдено")

        if (campaign_db.clicks_used + 1) > (campaign_db.clicks_limit + campaign_db.clicks_limit * 0.1):  # с учетом этого клика превысим порог в 5%
            # print(f"ClickTrouble client_id: {client_id} advId: {adId} curday: {curday} campaign: {campaign_db} недоступно для клика по лимитам")

            return make_http_error(404, f"Рекламное объявление с ID {adId} недоступно для клика")

        if campaign_db.start_date > curday or campaign_db.end_date < curday:  # нельзя кликать по неактуальным
            # print(f"ClickTrouble client_id: {client_id} advId: {adId} curday: {curday} campaign: {campaign_db} недоступно для клика по дате")
            return make_http_error(404, f"Рекламное объявление с ID {adId} недоступно для клика")

        client = dbcon.get_client_by_id(client_id)
        if client is None:
            print(f"ClickTrouble client_id: {client_id} advId: {adId} curday: {curday} campaign: {campaign_db} клиент не найден")
            return make_http_error(404, f"Клиент с ID {client_id} не найдено")

        dbcon.click(campaign_db, client_id, curday)
        return PlainTextResponse(status_code=204)