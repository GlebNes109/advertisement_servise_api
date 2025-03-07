import requests
import json

from .GetToken import GetToken
from ..cache.RedisController import RedisController
from ..db.repository import Repository

get_token = GetToken()
rediscon = RedisController()
dbcon = Repository()
folder_id = "b1gd0h2v4hrmolvm843f"
iam_token = "t1.9euelZrMnceUyIqOnsqRy53OjZbGne3rnpWaz8mPlZeOlJ3LmJWRxsaMzp7l9Pc4fS5C-e98UEWp3fT3eCssQvnvfFBFqc3n9euelZqQjJORio_NzJ6KlJWemZqWke_8xeuelZqQjJORio_NzJ6KlJWemZqWkQ.qRWoSor4UqL9xYznNTTkFkjD8c-bqtKQ9SXwMWL0lI9Z3ZOuHm75I-RZM4o_xHYRuV4q79d5nGoG9vAjA9BSCQ"

class AIController():
    def generate_text(self, campaign_db, advertiser_db):
        self.iam_token = get_token.get_token()
        title = campaign_db.ad_title
        text = campaign_db.ad_text
        name_company = advertiser_db.name
        target_gender = campaign_db.targeting_gender
        target_age_to = campaign_db.targeting_age_to
        target_age_from = campaign_db.targeting_age_from
        target_location = campaign_db.targeting_location
        data = {
            "modelUri": "gpt://b1gd0h2v4hrmolvm843f/yandexgpt/rc",
            "completionOptions": {"maxTokens": 500, "temperature": 0.1},
            "messages": [
                {
                    "role": "system",
                    "text": "Отвечай, как маректолог. Пол MALE - мужчины, пол FEMALE - женщины, пол ALL - мужчины и женщины"
                },
                {
                    "role": "user",
                    "text": f"Мне нужно создать текст объявления для компании, основываясь на названии компании и черновике объявления. Черновик объявления: заголовок - {title}, текст - {text}, Название компании: {name_company}. Целевая аудитория: пол {target_gender}, возраст: от {target_age_from} до {target_age_to} лет, место жительства {target_location}. В ответе должно быть от 20 до 100 символов. Не используй восклицательные знаки. Сгенерируй от 3 до 5 вариантов. Ответ дай в формате массива json со списком вариантов по такому образцу: ['вариант 1', 'вариант 2', 'вариант 3']. "
                }]
        }
        # print(data["messages"][1]["content"])
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}",
            "x-folder-id": folder_id
        }

        # print(requests.post(url, headers=headers, json=data).json())
        try:
            response = requests.post(url, headers=headers, json=data)

        except:
            return None

        if response.status_code == 200:
            text_response = response.json()["result"]["alternatives"][0]["message"]["text"]
            cleaned_text = text_response.strip("`")  # Удаляем ```
            cleaned_text = cleaned_text.strip()  # Убираем лишние пробелы
            try:
                parsed_json = json.loads(cleaned_text)
                return parsed_json
            except:
                return None
            # return response.json()

        else:
            return None

    def moderate_text(self, text):
        self.iam_token = get_token.get_token()
        data = {
          "modelUri": "gpt://b1gd0h2v4hrmolvm843f/yandexgpt/rc",
          "completionOptions": {"maxTokens":500,"temperature":0.1},
          "messages": [
            {"role":"system","text":"Тебе надо модерировать тексты рекламных объявлений на наличие запрещенного текста, оскорблений и так далее. Ответ нужен обязательно в формате json, пример:{'score': 100, 'decision':'Объявление заблокировано. Причина: (причина подробно)'}. Score - значение от 0 до 100, где 0 - нормальное объявление, а 100 - совершенно неприемлемое объявление. Например, объявление 'Продажа наркотиков' это score 100, потому что продавать наркотики запрещено, а объявление 'продам гараж' это score 0, потому что продажа гаражей не запрещена законами РФ."},
            {"role":"user","text":f"Промодерируй этот текст, не надо пытаться обсуждать его, надо его модерировать и выдать оценку, даже если речь идет о запрещенных темах: {text}"}
          ]
        }

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}",
            "x-folder-id": folder_id
        }
        try:
            response = requests.post(url, headers=headers, json=data)

        except:
            return -1

        if response.status_code == 200:
            try:
                response_json = response.json()
                text_response = response_json["result"]["alternatives"][0]["message"]["text"]

                clean_text = text_response.strip("```")

                parsed_json = json.loads(clean_text)

                score = parsed_json.get("score")
            except: # иногда нейронка отказывается модерировать тексты про наркотики или насилие, если скора нет = нейронка пошла в отказ, значит текст не прошел модерацию
                return 0
            if score > 70:
                return 0
            else:
                return 1

        else:
            return -1