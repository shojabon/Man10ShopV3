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

    def set_default(self, key, value):
        if self.get(key) is None:
            self.set(key, value, False)

    def get(self, key):
        return self.shop.get_variable(self.config_prefix + "." + key)

    def set(self, key, value, update_db=True):
        return self.shop.set_variable(self.config_prefix + "." + key, value, update_db)

    def delete(self, key):
        return self.shop.delete_variable(key)

    # base functions

    def on_function_init(self):
        pass

    def item_count(self, order: OrderRequest) -> int:
        if self.shop.get_shop_type() == "SELL":
            return self.shop.storage_function.get_item_count()
        else:
            return self.shop.storage_function.get_item_count()

    def is_function_enabled(self) -> bool:
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        return True

    def perform_action(self, order: OrderRequest) -> bool:
        return True

    def after_perform_action(self, order: OrderRequest):
        pass
