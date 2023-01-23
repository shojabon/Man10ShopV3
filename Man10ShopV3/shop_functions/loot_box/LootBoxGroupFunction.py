from threading import Thread
from typing import List

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Response import RequestResponse
from Man10ShopV3.data_class.ShopFunction import ShopFunction
from Man10ShopV3.data_class.loot_box.LootBoxGroupData import LootBoxGroup


class LootBoxGroupFunction(ShopFunction):
    allowed_shop_type = ["LOOT_BOX"]

    def on_function_init(self):
        self.set_variable("groups", []) # LootBoxGroup object

        self.shop.register_queue_callback("lootBox.win", self.log_loot_box_win_task)
        self.shop.register_queue_callback("lootBox.win", self.give_item_task)

    def get_groups(self) -> List[LootBoxGroup]:
        return [LootBoxGroup().from_json(x) for x in self.get("groups")]

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if sum([x.weight for x in self.get_groups()]) != 100000000:
            order.player.warn_message("重量設定の合計値が正しくありません")
            return False
        return True

    def after_perform_action(self, order: OrderRequest):
        order.player.execute_command_in_server("mshopv3 lootBoxPlay " + self.shop.get_shop_id() + " " + order.player.uuid + " " + order.log_id)

    # queue task
    def log_loot_box_win_task(self, data):
        item = ItemStack().from_json(data["data"]["item"])
        self.shop.api.update_log(data["data"]["log_id"], {
            "loot_box_win_item": item.get_json()
        })

    def give_item_task(self, data):
        player: Player = data["player"]
        item = ItemStack().from_json(data["data"]["item"])
        request_give_item = player.item_give(item.type_base64, item.amount)
        if not request_give_item.success():
            player.warn_message(request_give_item.message())
            player.warn_message("エラーコード: " + data["data"]["log_id"])
        player.success_message("§a§lおめでとうございます『" + item.display_name + "』§a§lが当たりました!")

    def sign_information(self, sign_info: list) -> list:
        return [
            "",
            " " if self.shop.shop_enabled_function.is_enabled() else "",
            "",
            ""
        ]