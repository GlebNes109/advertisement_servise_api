from io import BytesIO

from starlette.responses import JSONResponse, PlainTextResponse, StreamingResponse
from ..db.repository import Repository
from ..services.utility_service import make_http_error
from fastapi import UploadFile, File
dbcon = Repository()

class ImageService:
    def add_image(self, campaignId: str, file: UploadFile = File(...)):
        campaign_db = dbcon.get_campaign(campaignId)

        if not campaign_db:
            return make_http_error(404, "кампания с такими данными не существует")

        image_data = file.file.read()
        res = dbcon.add_image(image_data, campaignId)
        if not res:
            return make_http_error(409, "изображение уже загружено, обновите изображение")

        return JSONResponse(status_code=200, content="изображение загружено")

    def get_image(self, campaignId: str):
        campaign_db = dbcon.get_campaign(campaignId)

        if not campaign_db:
            return make_http_error(404, "кампания с такими данными не существует")

        image_data = dbcon.get_campaign(campaignId).ad_image
        if not image_data:
            # Если изображения нет, возвращаем ошибку 404
            return make_http_error(404, "Изображение не найдено")

        # Возвращаем изображение с типом "image/jpeg" напрямую из памяти
        return StreamingResponse(BytesIO(image_data), media_type="image/jpeg")

    def delete_image(self, campaignId: str):
        campaign_db = dbcon.get_campaign(campaignId)

        if not campaign_db:
            return make_http_error(404, "кампания с такими данными не существует")

        dbcon.delete_image(campaignId)
        return PlainTextResponse(status_code=204)

    def put_image(self, campaignId: str, file: UploadFile = File(...)):
        campaign_db = dbcon.get_campaign(campaignId)

        if not campaign_db:
            return make_http_error(404, "кампания с такими данными не существует")

        image_data = file.file.read()
        res = dbcon.put_image(image_data, campaignId)
        if res == False:
            return make_http_error(404, "изображение не найдено")

        return JSONResponse(status_code=200, content="изображение загружено")