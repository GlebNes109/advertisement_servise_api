from starlette.responses import JSONResponse

from .utility_service import make_http_error
from ..cache.RedisController import RedisController
from ..db.repository import Repository
from ..models.Model_converter import convert_to_apimodel
from ..models.api_models import *
from ..models.db_models import *

dbcon = Repository()
rediscon = RedisController()

class AdvertiserService:
    def add_advs(self, advs: list[AdvertiserUpsert]):
        advs_id = [advertiser.advertiser_id for advertiser in advs]
        
        print(f"AdvertiserUpsert: {list[AdvertiserUpsert]}")

        if not dbcon.check_advertisers(advs_id):
            return make_http_error(409, "рекламодатель с таким id есть в базе")

        if len(set(advs_id)) != len(advs_id):
            return make_http_error(409, "id рекламодателей в списке совпадают")

        advs_db = []
        advs_api = []
        for advertiser in advs:
            advertiser_db = AdvertiserDB(
                advertiser_id=advertiser.advertiser_id,
                name=advertiser.name
            )
            advs_api.append(advertiser.model_dump())
            # dbcon.add_client(client_db)
            advs_db.append(advertiser_db)

        dbcon.add_advertisers(advs_db)
        return JSONResponse(status_code=201, content=advs_api)

    def get_advertiser(self, advertiserId: str):
        advertiser_db = dbcon.get_advertiser_by_id(advertiserId)
        if advertiser_db:
            """client_api = ClientUpsert(
                client_id=client_db.client_id,
                login=client_db.login,
                age=client_db.age,
                location=client_db.location,
                gender=client_db.gender
            )"""
            return JSONResponse(status_code=200, content=advertiser_db.model_dump())
        else:
            return make_http_error(404, "рекламодатель с таким id не найден")

