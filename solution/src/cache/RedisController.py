import redis
from ..config import settings

class RedisController:
    def __init__(self):

        print(f"try to connect to redis with {settings.redis_host} {settings.redis_port}")
        self.client = redis.StrictRedis(
        host=settings.redis_host,
        port=settings.redis_port,
        # password='1232'
        )
        print("redis connected")
        self.key_blacklist = "BLACKLIST"
        '''self.client.set("DAY", 0)
        self.client.set("BLACKLIST", "")'''

    def set_day(self, day):
        self.client.set("DAY", day)

    def get_day(self):
        if self.client.exists("DAY"):
            day = int(self.client.get("DAY"))
            return day

        else:
            return -1 # ну типа день не задан = день отрицательный, ну понятно короче

    def check_company_date(self, start_date, end_date):
        if self.client.exists("DAY"):
            day = int(self.client.get("DAY"))
            return int(start_date) >= day and int(end_date) >= day and start_date < end_date

    def add_blacklist(self, ban_words):
        if isinstance(ban_words, list):
            self.client.delete(self.key_blacklist)  # Очищаем старый список перед добавлением нового
            self.client.rpush(self.key_blacklist, *ban_words)

    def check_blacklist(self, text):
        if self.client.exists(self.key_blacklist):
            ban_words = self.client.lrange(self.key_blacklist, 0, -1)
            ban_words = [word.decode("utf-8") for word in ban_words]
            words = text.split()
            return not any(word in ban_words for word in words)  # True, если нет запрещённых слов

        return True

    def get_blacklist(self):
        if self.client.exists(self.key_blacklist):
            return [word.decode("utf-8") for word in self.client.lrange(self.key_blacklist, 0, -1)]
        return []

    def add_token_yandexai(self, token, date):
        self.client.set("TTL_YANDEXAI_TOKEN", token)
        self.client.expire("TTL_YANDEXAI_TOKEN", 3600)

    def get_token_yandexai(self):
        if self.client.exists("TTL_YANDEXAI_TOKEN"):
            return self.client.get("TTL_YANDEXAI_DATE")
        else:
            return None


