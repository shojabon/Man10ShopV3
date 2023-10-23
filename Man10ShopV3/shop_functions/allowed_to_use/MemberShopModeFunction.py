from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction


class MemberShopModeFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("enabled", False)

    def is_enabled(self):
        return self.get("enabled")

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        if self.is_enabled():
            user_permission = self.shop.permission_function.get_permission(order.player)
            if user_permission == "NONE" or user_permission == "BANNED":
                order.player.warn_message("このメンバー限定ショップを使用することができません")
                return False
        return True