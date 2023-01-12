from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from Man10ShopV3.data_class.Shop import Shop

from Man10ShopV3.data_class.OrderRequest import OrderRequest


class ShopFunction(object):

    allowed_shop_type = ["BUY", "SELL"]
    shop: Shop = None
    config_prefix = None

    def __init__(self):
        pass

    # config functions

    def get(self, key):
        return self.shop.get_variable(self.config_prefix + "." + key)

    def set(self, key, value):
        return self.shop.set_variable(self.config_prefix + "." + key, value)

    # base functions

    def item_count(self, order: OrderRequest) -> int:
        pass

    def is_function_enabled(self) -> bool:
        pass

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        pass

    def perform_action(self, order: OrderRequest) -> bool:
        pass

    def after_perform_action(self, order: OrderRequest):
        pass
