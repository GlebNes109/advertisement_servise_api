from starlette.responses import JSONResponse
from ..db.repository import Repository
from ..services.utility_service import make_http_error

dbcon = Repository()


class StatsService:
    def get_stats_campaign(self, campaignId: str):
        if not dbcon.get_campaign(campaignId):
            return make_http_error(404, "кампания с такими данными не найдена")

        stat = dbcon.get_stats_campaign(campaignId)

        return JSONResponse(status_code=200, content=stat.model_dump())

    def get_stats_campaign_daily(self, campaignId: str):
        if not dbcon.get_campaign(campaignId):
            return make_http_error(404, "кампания с такими данными не найдена")

        stat = dbcon.get_stats_campaign_daily(campaignId)
        stat_json = [daily_stat.model_dump() for daily_stat in stat]

        return JSONResponse(status_code=200, content=stat_json)

    def get_stats_advertisers(self, advertiserId: str):
        if not dbcon.get_advertiser_by_id(advertiserId):
            return make_http_error(404, "рекламодатель с такими данными не найден")

        stat = dbcon.get_stats_advertisers(advertiserId)
        return JSONResponse(status_code=200, content=stat.model_dump())

    def get_stats_advertisers_daily(self, advertiserId: str):
        if not dbcon.get_advertiser_by_id(advertiserId):
            return make_http_error(404, "рекламодатель с такими данными не найден")

        stat = dbcon.get_stats_advertisers_daily(advertiserId)
        stat_json = [daily_stat.model_dump() for daily_stat in stat]
        return JSONResponse(status_code=200, content=stat_json)
