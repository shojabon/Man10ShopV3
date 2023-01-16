import datetime
import random

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class RandomPriceFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    def on_function_init(self):
        self.set_variable("prices", [])
        self.set_variable("time", 0)
        self.set_variable("last_refill_time", -1)

    def set_time(self, time: int):
        return self.set("time", time)

    def set_prices(self, prices: list):
        return self.set("prices", prices)

    def set_last_refill_time(self, time: int):
        return self.set("last_refill_time", time)

    def get_time(self):
        return self.get("time")

    def get_prices(self) -> list:
        return self.get("prices")

    def get_last_refill_time(self):
        return self.get("last_refill_time")

    #=======
    def is_function_enabled(self) -> bool:
        if len(self.get_prices()) == 0 or self.get_time() == 0 or self.get_last_refill_time() == -1:
            return False
        return True

    def calculate_last_pick_time(self):
        seconds_since_last_refill = datetime.datetime.now().timestamp() - self.get_last_refill_time()
        skipped_refills = seconds_since_last_refill//(self.get_time() * 60)
        return self.get_last_refill_time() + skipped_refills * self.get_time() * 60

    def per_minute_execution_task(self):
        if datetime.datetime.now().timestamp() - self.get_last_refill_time() >= self.get_time():
            self.set_last_refill_time(self.calculate_last_pick_time())
            if len(self.get_prices()) == 0: return
            prices = self.get_prices().copy()
            random.shuffle(prices)
            self.shop.price_function.set_price(prices[0])
            self.shop.sign_function.update_signs()
