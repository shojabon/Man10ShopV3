import datetime
import traceback

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class IpLimitFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("count", 0)
        self.set_variable("time", 0)

    def get_count(self):
        return self.get("count")

    def get_time(self):
        return self.get("time")

    def get_player_alts_in_time(self, player: Player):
        try:
            result = self.shop.api.main.mongo["man10shop_v3"]["trade_log"].aggregate(
                [
                    {
                        "$match": {
                            "shopId": self.shop.get_shop_id(),
                            "player.ipAddress": player.ip_address,
                            "time": {
                                "$gte": datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() - self.get_time() * 60)
                            },
                        }
                    },
                    {
                        "$group": {
                            "_id": "$player.uuid",
                            "uuid": {
                                "$first": "$player.uuid"
                            },
                            "name": {
                                "$first": "$player.name"
                            }
                        }
                    }
                ]
            )
            result = [x for x in result]
            return [x["uuid"] for x in result], [x["name"] for x in result]
        except Exception:
            traceback.print_exc()
            return None

    def is_function_enabled(self) -> bool:
        if self.get_time() == 0 or self.get_count() == 0:
            return False
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if order.player.ip_address is None:
            order.player.warn_message("内部エラーが発生しました(IP)")
            return False
        alt_uuids, alt_names = self.get_player_alts_in_time(order.player)
        alt_uuids = alt_uuids[:self.get_count()]
        alt_names = alt_names[:self.get_count()]

        if len(alt_names) >= self.get_count() and order.player.uuid not in alt_uuids:
            order.player.warn_message("このショップを使えるアカウントは")
            order.player.warn_message(" ".join(alt_names) + "です")
            return False
        return True


