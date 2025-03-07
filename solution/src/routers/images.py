from fastapi import APIRouter, UploadFile, File
from starlette.responses import JSONResponse

from ..db.repository import Repository
from ..services.image_service import ImageService
from ..services.utility_service import make_http_error

images_service = ImageService()

router = APIRouter()
dbcon = Repository()

@router.post("/campaigns/{campaignId}", summary="Добавление изображения для кампании")
def add_image(campaignId: str, file: UploadFile = File(...)):
    return images_service.add_image(campaignId, file)

@router.get("/campaigns/{campaignId}", summary="Получение изображения кампании")
def get_image(campaignId: str):
    return images_service.get_image(campaignId)

@router.delete("/campaigns/{campaignId}", summary="Удаление изображения кампании")
def delete_image(campaignId: str):
    return images_service.delete_image(campaignId)

@router.put("/campaigns/{campaignId}", summary="Замена изображения кампании")
def put_image(campaignId: str, file: UploadFile = File(...)):
    return images_service.put_image(campaignId, file)