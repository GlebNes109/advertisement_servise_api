from fastapi import APIRouter

from ..models.api_models import MLScore
from ..services.ml_score_service import MlScoreService

router = APIRouter()
ml_score_service = MlScoreService()

@router.post("/ml-scores", summary="Добавление скора", description="Добавление скора для пары 'клиент - рекламодатель'")
def add_advs(mlscore: MLScore):
    return ml_score_service.add_score(mlscore)