from threading import Thread

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Response import RequestResponse
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class MoneyFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    def on_function_init(self):
        self.set_variable("money", 0)

        self.shop.register_queue_callback("money.deposit", self.deposit_money)
        self.shop.register_queue_callback("money.withdraw", self.withdraw_money)

    # variables

    def get_money(self):
        return self.get("money")

    def set_money(self, value: int):
        return self.set("money", value)

    def add_money(self, amount: int):
        return self.set_money(self.get_money() + amount)

    def remove_money(self, amount: int):
        return self.set_money(self.get_money() - amount)

    # ==== queue functions =====

    def deposit_money(self, data):
        player_mode = "player" in data
        if "amount" not in data["data"]: return
        if player_mode:
            player: Player = data["player"]
            take_money_operation = player.take_money(data["data"]["amount"])
            if not take_money_operation.success():
                player.warn_message(take_money_operation.message())
                return

        result = self.add_money(data["data"]["amount"])
        if result and player_mode:
            player.success_message("入金に成功しました")
        else:
            player.warn_message("入金に失敗しました")

    def withdraw_money(self, data):
        player_mode = "player" in data
        if "amount" not in data["data"]: return
        if player_mode:
            player: Player = data["player"]
            if self.get_money() < data["data"]["amount"]:
                player.warn_message(RequestResponse("balance_lacking").message())
                return

        take_money_operation = self.remove_money(data["data"]["amount"])
        if not take_money_operation:
            if player_mode: player.warn_message("出金に失敗しました")
            return

        if player_mode:
            result = player.give_money(data["data"]["amount"])
            if result and player_mode:
                player.success_message("出金に成功しました")
            else:
                player.warn_message("出金に失敗しました")


    # =========

    def item_count(self, player: Player) -> int:
        if self.shop.is_admin(): return 0
        if self.shop.get_shop_type() == "SELL":
            if self.shop.get_price() == 0: return super().item_count(player)
            return self.get_money() // self.shop.get_price()
        return super().item_count(player)

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.shop.get_shop_type() == "SELL":
            if self.get_money() < self.shop.get_price() and not self.shop.is_admin():
                order.player.warn_message("ショップ残金不足してます")
                return False
        return True
