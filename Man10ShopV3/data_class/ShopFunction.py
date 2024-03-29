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

    def set_variable(self, key, value, permission="MODERATOR", variable_check: Callable = None, visible_in_json: bool = True):
        self.shop.variable_permissions[self.config_prefix + "." + key] = permission
        if self.get(key) is None:
            self.set(key, value, variable_check=False, update_db=False)
        if variable_check is not None:
            self.shop.variable_check[self.config_prefix + "." + key] = variable_check
        self.shop.visible_in_json[self.config_prefix + "." + key] = visible_in_json

    def get(self, key):
        return self.shop.get_variable(self.config_prefix + "." + key)

    def set(self, key, value, update_db=True, variable_check: bool= True):
        result = self.shop.set_variable(self.config_prefix + "." + key, value, update_db, variable_check=variable_check)
        if not result:
            return False
        return result

    def set_dynamic_variable(self, key: str, value) -> dict:
        return self.shop.set_dynamic_variable(self.config_prefix + "." + key, value)

    # base functions

    def on_function_init(self):
        pass

    def item_count(self, player: Player) -> Optional[int]:
        if self.shop.is_admin():
            return 0
        if self.shop.get_shop_type() == "SELL":
            return self.shop.storage_function.get_storage_size()
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

    def menu_info(self, player: Player) -> dict:
        pass

    def sign_information(self, sign_info: list) -> list:
        pass

    def log_data(self, order: OrderRequest) -> dict: pass

    def per_minute_execution_task(self): pass

