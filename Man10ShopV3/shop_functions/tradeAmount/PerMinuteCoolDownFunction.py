import datetime
import traceback
from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class PerMinuteCoolDownFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("time", 0)
        self.set_variable("amount", 0)

    def set_time(self, time: int):
        return self.set("time", time)

    def get_time(self) -> int:
        return self.get("time")

    def set_amount(self, amount: int):
        return self.set("amount", amount)

    def get_amount(self) -> int:
        return self.get("amount")

    # =====

    def player_in_time_trade_count(self, player: Player):
        try:
            result = self.shop.api.main.mongo["man10shop_v3"]["trade_log"].aggregate([
                {
                    "$match": {
                        "shopId": self.shop.get_shop_id(),
                        "player.uuid": player.uuid,
                        "time": {
                            "$gte": datetime.datetime.fromtimestamp(
                                datetime.datetime.now().timestamp() - self.get_time() * 60)
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$player.uuid",
                        "total": {"$sum": "$orderData.amount"}
                    }

                }
            ])
            result = [x for x in result]
            if len(result) == 0:
                return 0
            return result[0]["total"]
        except Exception:
            traceback.print_exc()
            return None

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        player_trade_count_in_time = self.player_in_time_trade_count(order.player)
        if player_trade_count_in_time is None:
            order.player.warn_message("内部エラーが発生しました")
            return False
        if player_trade_count_in_time + order.amount > self.get_amount():
            order.player.warn_message("時間内の最大取引数に達しています")
            return False
        return True

    def item_count(self, player: Player) -> Optional[int]:
        if player is None:
            return 0
        count = self.get_amount() - self.player_in_time_trade_count(player)
        if self.shop.is_admin():
            return -count
        if count < 0:
            return 0
        return count

    def is_function_enabled(self) -> bool:
        if self.get_time() == 0 or self.get_amount() == 0:
            return False
        return True
