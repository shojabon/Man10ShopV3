from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Optional, Callable

from Man10ShopV3.data_class.Player import Player

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

    def set_variable(self, key, value, permission="MODERATOR"):
        self.shop.variable_permissions[self.config_prefix + "." + key] = permission
        if self.get(key) is None:
            self.set(key, value, False)

    def get(self, key):
        return self.shop.get_variable(self.config_prefix + "." + key)

    def set(self, key, value, update_db=True):
        result = self.shop.set_variable(self.config_prefix + "." + key, value, update_db)
        if not result:
            return False
        return result

    def delete(self, key):
        return self.shop.delete_variable(key)

    # base functions

    def on_function_init(self):
        pass

    def item_count(self, player: Player) -> Optional[int]:
        if self.shop.get_shop_type() == "SELL":
            return self.shop.storage_function.get_item_count()
        else:
            return None

    def is_function_enabled(self) -> bool:
        return True

    def is_allowed_to_use_shop(self, order: OrderRequest) -> bool:
        return True

    def perform_action(self, order: OrderRequest) -> bool:
        return True

    def after_perform_action(self, order: OrderRequest):
        pass

    def menu_info(self, player: Player) -> dict:
        pass

    def sign_information(self, sign_info: list) -> list:
        pass

    def log_data(self, order: OrderRequest) -> dict: pass
