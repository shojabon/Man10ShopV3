from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class ShopEnabledFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("enabled", True)

    def is_enabled(self):
        return self.get("enabled")

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if not self.is_enabled():
            order.player.warn_message("現在このショップは停止しています")
            return False
        return True

    def sign_information(self, sign_info: list) -> list:
        if not self.is_enabled():
            return [
                "",
                "§c取引停止中",
                "",
                ""
            ]