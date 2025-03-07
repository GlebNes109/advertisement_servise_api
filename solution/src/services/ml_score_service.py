from starlette.responses import JSONResponse

from .utility_service import make_http_error
from ..db.repository import Repository
from ..models.api_models import MLScore

dbcon = Repository()


class MlScoreService():
    def add_score(self, mlscore: MLScore):

        if dbcon.get_client_by_id(mlscore.client_id) is None:
            return make_http_error(404, "клиент не найден")
        if dbcon.get_advertiser_by_id(mlscore.advertiser_id) is None:
            return make_http_error(404, "рекламодатель не найден")

        dbcon.add_scrore(mlscore)
        return JSONResponse(status_code=200, content="ML скор успешно добавлен или обновлён")