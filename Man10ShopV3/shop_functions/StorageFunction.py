from typing import Optional

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Response import RequestResponse
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class StorageFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    def on_function_init(self):
        self.set_variable("storage_size", 64 * 9)
        self.set_variable("item_count", 0)

        self.shop.register_queue_callback("storage.item.deposit", self.deposit_item)
        self.shop.register_queue_callback("storage.item.withdraw", self.withdraw_item)

    def get_storage_size(self):
        return self.get("storage_size")

    def get_item_count(self):
        return self.get("item_count")

    def set_item_count(self, amount: int):
        return self.set("item_count", amount)

    def add_item_count(self, amount: int):
        return self.set_item_count(self.get_item_count() + amount)

    def remove_item_count(self, amount: int):
        return self.set_item_count(self.get_item_count() - amount)

    # =========

    def deposit_item(self, data):
        player_mode = "player" in data
        if "amount" not in data["data"]: return
        if player_mode:
            player: Player = data["player"]
            take_item_operation = player.item_take(self.shop.target_item_function.get_target_item(), data["data"]["amount"])
            if not take_item_operation.success():
                player.warn_message(take_item_operation.message())
                return

        result = self.add_item_count(data["data"]["amount"])
        if result and player_mode:
            player.success_message("在庫を補充しました 現在: " + str(self.get_item_count()))
        else:
            player.warn_message("在庫の補充に失敗しました")

    def withdraw_item(self, data):
        player_mode = "player" in data
        if "amount" not in data["data"]: return
        if player_mode:
            player: Player = data["player"]
            if self.get_item_count() < data["data"]["amount"]:
                player.warn_message("在庫が不足しています")
                return

        take_money_operation = self.remove_item_count(data["data"]["amount"])
        if not take_money_operation:
            if player_mode: player.warn_message("引き出しに失敗しました")
            return

        if player_mode:
            result = player.item_give(self.shop.target_item_function.get_target_item(), data["data"]["amount"])
            if result.success() and player_mode:
                player.success_message("引き出しに成功しました 現在:" + str(self.get_item_count()))
            else:
                player.warn_message(result.message())

    # =========

    def item_count(self, order: OrderRequest) -> Optional[int]:
        if self.shop.is_admin(): return None
        if self.shop.get_shop_type() == "BUY":
            return self.get_item_count()
        if self.shop.get_shop_type() == "SELL":
            return self.get_storage_size() - self.get_item_count()
        return self.get_storage_size()

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            if order.amount + self.get_item_count() >= self.get_storage_size() and not self.shop.is_admin():
                order.player.warn_message("ショップの倉庫がいっぱいです")
                return False

        if self.shop.get_shop_id() == "BUY":
            if order.amount > self.get_item_count() and not self.shop.is_admin():
                order.player.warn_message("在庫がありません")
                return False
        return True
