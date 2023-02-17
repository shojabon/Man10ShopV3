import datetime
import traceback

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class IpLimitFunction(ShopFunction):
    allowed_shop_type = []

    ip_tables_cache = {}

    def on_function_init(self):
        self.set_variable("count", 0)
        self.set_variable("time", 0)

    def get_count(self):
        return self.get("count")

    def get_time(self):
        return self.get("time")

    def get_player_alts_in_time(self, player: Player):
        try:
            if player.ip_address not in IpLimitFunction.ip_tables_cache:
                ip_table_data = self.shop.api.main.mongo["man10shop_v3"]["iptables"].find_one({"ip": player.ip_address})
                if ip_table_data is not None:
                    IpLimitFunction.ip_tables_cache[ip_table_data["ip"]] = ip_table_data["accounts"]
            data = IpLimitFunction.ip_tables_cache.get(player.ip_address)
            if data is None:
                data = {}

            final_data = {}
            for player_uuid in data.keys():
                if data[player_uuid]["lastSeenTime"].timestamp() >= datetime.datetime.now().timestamp() - 60 * self.get_time():
                    final_data[player_uuid] = data[player_uuid]

            return [x["uuid"] for x in final_data.values()], [x["name"] for x in final_data.values()]
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

    def after_perform_action(self, order: OrderRequest):
        self.shop.api.main.mongo["man10shop_v3"]["iptables"].update_one(
            {"ip": order.player.ip_address},
            {"$set":{
                "accounts." + order.player.uuid: {
                    "uuid": order.player.uuid,
                    "name": order.player.name,
                    "lastSeenTime": datetime.datetime.now()
                }
            }},
            upsert=True
        )
        del IpLimitFunction.ip_tables_cache[order.player.ip_address]


