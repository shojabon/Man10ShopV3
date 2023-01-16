import datetime
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class WeekDayToggleFunction(ShopFunction):
    allowed_shop_type = []

    date_labels = ["日曜日", "月曜日", "火曜日", "水曜日","木曜日", "金曜日", "土曜日"]

    def on_function_init(self):
        self.set_variable("dates", [True, True, True, True, True, True, True])

    def get_dates(self) -> list:
        return self.get("dates")

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if not self.get_dates()[(datetime.datetime.now().weekday() + 1) % 7]:
            allowed_dates = " ".join([x for x in self.date_labels if self.get_dates()[self.date_labels.index(x)]])[:-1]
            order.player.warn_message("このショップを本日ご利用することはできません")
            order.player.warn_message("このショップは" + allowed_dates + "に利用することができます")
            return False
        return True


