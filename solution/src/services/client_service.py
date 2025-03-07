from starlette.responses import JSONResponse
from ..db.repository import Repository
from ..models.api_models import *
from ..models.db_models import *
from ..services.utility_service import make_http_error

dbcon = Repository()

class ClientService:

    def __init__(self):
        #self.dbcon = DbController()
        pass

    def add_clients(self, clients: list[ClientUpsert]):
        clients_id = [client.client_id for client in clients]
        print(f"ClientsUpsert: {list[ClientUpsert]}")
        if not dbcon.check_clients(clients_id):
            print(f"clients_id {clients_id} есть в базе")
            return make_http_error(409, "клиент с таким id есть в базе")

        if len(set(clients_id)) != len(clients_id):
            print("есть дубли айди")
            return make_http_error(409, "id клиентов в списке совпадают")

        clients_db = []
        clients_api = []
        for client in clients:
            client_db = ClientDB(
                client_id=client.client_id,
                login=client.login,
                age=client.age,
                location=client.location,
                gender=client.gender
            )
            clients_api.append(client.model_dump())
            # dbcon.add_client(client_db)
            clients_db.append(client_db)

        dbcon.add_clients(clients_db)
        return JSONResponse(status_code=201, content=clients_api)

    def get_client(self, clientId: str):
        client_db = dbcon.get_client_by_id(clientId)

        if client_db:
            client_api = ClientUpsert(
                client_id=client_db.client_id,
                login=client_db.login,
                age=client_db.age,
                location=client_db.location,
                gender=client_db.gender
            )
            return JSONResponse(status_code=200, content=client_api.model_dump())

        else:
            return make_http_error(404, "клиент с таким id не найден")