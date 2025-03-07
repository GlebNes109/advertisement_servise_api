import re
import time as time_module

import starlette
from fastapi import Request, FastAPI
from starlette.responses import JSONResponse
from prometheus_client import  Counter, Gauge, Summary, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

from ..db.repository import Repository

dbcon = Repository()

def make_http_error(code, text):
    return JSONResponse(
        status_code=code,
        content={
            "status": "error",
            "message": text
        })


def get_or_create_metric(metric_type, name, documentation, labelnames=None, **kwargs):
    """Функция для получения существующей метрики или создания новой"""
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    # Если labelnames не передан, передаём пустой список, чтобы избежать ошибки
    labelnames = labelnames or []

    return metric_type(name, documentation, labelnames=labelnames, **kwargs)

class Metrics:
    REQUEST_COUNT = get_or_create_metric(Counter, 'request_count', 'Total number of requests', ['method', 'endpoint'])
    ACTIVE_REQUESTS = get_or_create_metric(Gauge, 'active_requests', 'Number of active requests')
    REQUEST_TIME = get_or_create_metric(Summary, 'request_processing_seconds', 'Time spent processing requests',
                                        ['method', 'endpoint'])
    REQUEST_DURATION = get_or_create_metric(Histogram, 'request_duration_seconds', 'Request duration in seconds',
                                            ['method', 'endpoint'], buckets=[0.1, 0.5, 1, 2, 5])

    ERRORS_4XX = get_or_create_metric(Counter, 'http_errors_4xx', 'Number of 4xx errors', ['http_code'])
    ERRORS_5XX = get_or_create_metric(Counter, 'http_errors_5xx', 'Number of 5xx errors', ['http_code'])

    BUSINESS_IMPRESSIONS_INCOME = get_or_create_metric(Gauge, 'business_imp_income', 'Impressions income')
    BUSINESS_CLICKS_INCOME = get_or_create_metric(Gauge, 'business_click_income', 'Clicks income')
    BUSINESS_TOTAL_INCOME = get_or_create_metric(Gauge, 'business_total_income', 'Total income')
    BUSINESS_COMPANY_INCOME = get_or_create_metric(Gauge, 'business_company_income', 'Company income', ['company_name'])


metrics = Metrics()  # Создаем единственный экземпляр


async def metrics_middleware(request: Request, call_next):
    """Middleware для сбора метрик"""
    method = request.method
    endpoint = request.url.path

    metrics.REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    metrics.ACTIVE_REQUESTS.inc()
    start_time = time_module.time()

    response = await call_next(request)

    process_time = time_module.time() - start_time
    metrics.REQUEST_TIME.labels(method=method, endpoint=endpoint).observe(process_time)
    metrics.REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(process_time)
    metrics.ACTIVE_REQUESTS.dec()

    # Обрабатываем коды ошибок
    if 400 <= response.status_code < 500:
        metrics.ERRORS_4XX.labels(http_code=response.status_code).inc()
    elif 500 <= response.status_code < 600:
        metrics.ERRORS_5XX.labels(http_code=response.status_code).inc()

    return response

# Функция для нормализации пути
def normalize_path(path: str) -> str:
    # Заменяем path-параметры на плейсхолдеры
    return re.sub(r'/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '/{uuid}', path)

class MetricsService:
    def metrics(self):
        return starlette.responses.Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    def business_metrics(self):
        impstat, clickstat = dbcon.get_income_total()
        impstat = impstat if impstat else 0
        clickstat = clickstat if clickstat else 0
        metrics.BUSINESS_IMPRESSIONS_INCOME.set(impstat)
        metrics.BUSINESS_CLICKS_INCOME.set(clickstat)
        metrics.BUSINESS_TOTAL_INCOME.set(impstat + clickstat)
        # аналогично подбирать стату отдельно по адвертайзерам
        # imps: [{name:"company", sum:1}]
        # clicks = [{name:"company", sum:2}]
        # res = [{name:"company", sum:3}]
        imps, clicks = dbcon.get_advertiser_costs()
        imps = imps if imps else []
        clicks = clicks if clicks else []
        adv_costs = imps + clicks

        res = []

        # Преобразуем списки в словари для удобства поиска
        imps_dict = {imp.name: imp.sum for imp in imps}
        clicks_dict = {click.name: click.sum for click in clicks}

        # Создаем результат
        all_names = set(imps_dict.keys()).union(clicks_dict.keys())

        for name in all_names:
            # Суммируем значения для каждой компании
            total = imps_dict.get(name, 0) + clicks_dict.get(name, 0)
            res.append({
                "name": name,
                "sum": total
            })
        for adv in res:
            metrics.BUSINESS_COMPANY_INCOME.labels(company_name=adv["name"]).set(adv["sum"])

        return starlette.responses.Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

def setup_middlewares(app: FastAPI):
    """Функция для подключения middleware"""
    app.middleware("http")(metrics_middleware)