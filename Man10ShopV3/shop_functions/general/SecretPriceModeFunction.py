from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class SecretPriceModeFunction(ShopFunction):
    allowed_shop_type = ["BUY", "SELL"]

    def on_function_init(self):
        self.set_variable("enabled", False)

    def set_enabled(self, enabled: bool):
        return self.set("enabled", enabled)

    def get_enabled(self):
        return self.get("enabled")

    def sign_information(self, sign_info: list) -> list:
        if self.get_enabled():
            return [
            "",
            "§b??????円",
            "",
            ""
            ]

