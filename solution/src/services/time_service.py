from starlette.responses import JSONResponse

from ..cache.RedisController import RedisController
from ..models.api_models import *

rediscon = RedisController()

class TimeService:
    def set_date(self, date: RequestDay):
        day = date.current_date
        rediscon.set_day(day)
        return JSONResponse(status_code=200, content=f"день {day} установлен")