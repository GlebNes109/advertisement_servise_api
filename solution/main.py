from src.routers import ml_scores
from src.config import settings
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from src.routers import statistics, moderation, images
from src.services.utility_service import make_http_error, metrics_middleware, setup_middlewares
from src.routers import clients, advertisers, time, campaigns, ads, metrics


app = FastAPI()
setup_middlewares(app)
# app.middleware("http")(metrics_middleware)

@app.exception_handler(RequestValidationError)
async def raise_validation_error(request: Request, exc: RequestValidationError):
    return make_http_error(400, "ошибка в данных запроса")

app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(advertisers.router, prefix="/advertisers", tags=["Advertisers"])
app.include_router(time.router, prefix="/time", tags=["Time"])
app.include_router(campaigns.router, prefix="/advertisers", tags=["Campaigns"])
app.include_router(ads.router, prefix="/ads", tags=["Ads"])
app.include_router(statistics.router, prefix="/stats", tags=["Statistics"])
app.include_router(moderation.router, prefix="/moderation", tags=["Moderation"])
app.include_router(images.router, prefix="/img", tags=["Images"])
app.include_router(ml_scores.router, prefix="", tags=["Advertisers"])
app.include_router(metrics.router, prefix="", tags=["Metrics"])


if __name__ == "__main__":
    server_address = settings.server_address
    host, port = server_address.split(":")
    uvicorn.run(app, host=host, port=int(port))