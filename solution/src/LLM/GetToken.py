import requests
import json

from ..cache.RedisController import RedisController

rediscon = RedisController()

class GetToken():
    def generate_token(self):
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"

        oauth_token = "y0__xCcwMu5BBjB3RMg7uyWpxJDK6pAzf27GSlVxYQTzSe8mgm5Qw"

        data = {
            "yandexPassportOauthToken": oauth_token
        }

        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response_json = response.json()
            iam_token = response_json["iamToken"]

        except:
            return None

        if response.status_code == 200:
            return iam_token

        else:
            return None

    def get_token(self):
        self.iam_token = rediscon.get_token_yandexai()
        if not self.iam_token:
            self.iam_token = self.generate_token()

        return self.iam_token


