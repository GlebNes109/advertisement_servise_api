from fastapi import APIRouter

from ..services.utility_service import MetricsService

metrics_service = MetricsService()

router = APIRouter()

# Эндпоинт для метрик Prometheus
@router.get("/metrics")
def metrics():
    return metrics_service.metrics()

@router.get("/business_metrics")
def business_metrics():
    return metrics_service.business_metrics()
