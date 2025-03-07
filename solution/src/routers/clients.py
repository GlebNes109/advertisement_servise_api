from fastapi import APIRouter

from ..models.api_models import ClientUpsert
from ..services.client_service import ClientService

client_service = ClientService()

router = APIRouter()


@router.post("/bulk", summary="Добавление клиентов", description="Массово добавляет клиентов в бд")
def add_clients(clients: list[ClientUpsert]):
    return client_service.add_clients(clients)

@router.get("/{clientId}", summary="Получение клиента", description="Получение клинета по id")
def get_client(clientId: str):
    return client_service.get_client(clientId)