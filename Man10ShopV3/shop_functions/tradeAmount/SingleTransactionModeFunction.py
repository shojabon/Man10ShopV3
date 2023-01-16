from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class SingleTransactionModeFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    def on_function_init(self):
        self.set_variable("enabled", False)

    def set_enabled(self, enabled: bool):
        return self.set("enabled", enabled)

    def get_enabled(self):
        return self.get("enabled")

    def is_function_enabled(self) -> bool:
        return self.get_enabled()

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.is_function_enabled() and order.amount != 1:
            order.player.warn_message("取引数は1でなくてはなりません")
            return False
        return True

