from fastapi import APIRouter

from ..models.api_models import *
from ..services.time_service import TimeService

time_service = TimeService()

router = APIRouter()

@router.post("/advance", summary="Установка текущей даты", description="Устанавливает текущий день в системе в заданную дату.")
def set_date(date: RequestDay):
    return time_service.set_date(date)