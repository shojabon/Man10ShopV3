from __future__ import annotations

from typing import TYPE_CHECKING
import humps

from Man10ShopV3.data_class.ShopFunction import ShopFunction
from Man10ShopV3.shop_functions.MoneyFunction import MoneyFunction
from Man10ShopV3.shop_functions.NameFunction import NameFunction
from Man10ShopV3.shop_functions.PermissionFunction import PermissionFunction
from Man10ShopV3.shop_functions.PriceFunction import PriceFunction
from Man10ShopV3.shop_functions.StorageFunction import StorageFunction
from Man10ShopV3.shop_functions.TargetItemFunction import TargetItemFunction
from Man10ShopV3.shop_functions.general.CategoryFunction import CategoryFunction
from utils.JsonTools import flatten_dict, unflatten_dict

if TYPE_CHECKING:
    from Man10ShopV3.manager.Man10ShopV3API import Man10ShopV3API

from Man10ShopV3.data_class.OrderRequest import OrderRequest

class Shop(object):

    api: Man10ShopV3API = None

    variable_permissions = {}

    def __init__(self, data):
        self.data = humps.decamelize(data)

        self.functions: dict[str, ShopFunction] = {}

        # general functions

        self.money_function: MoneyFunction = self.register_function("money", MoneyFunction())
        self.storage_function: StorageFunction = self.register_function("storage", StorageFunction())
        self.price_function: PriceFunction = self.register_function("price", PriceFunction())
        self.target_item_function: TargetItemFunction = self.register_function("target_item", TargetItemFunction())
        self.permission_function: PermissionFunction = self.register_function("permission", PermissionFunction())
        self.name_function: NameFunction = self.register_function("name", NameFunction())
        self.category_function: CategoryFunction = self.register_function("category", CategoryFunction())

    def get_export_data(self):
        return humps.camelize(self.data)

    def register_function(self, prefix: str, function: ShopFunction):
        function.shop = self
        function.config_prefix = prefix

        function.on_function_init()
        self.functions[prefix] = function
        return self.functions[prefix]

    # variable

    def get_variable(self, key):
        data = flatten_dict(self.data)
        return data.get(key)

    def set_variable(self, key, value, update_db=True):
        data = flatten_dict(self.data)
        data[key] = value
        self.data = unflatten_dict(data)
        if update_db:
            result = self.api.main.mongo["man10shop_v3"]["shops"].update_one({"shopId": self.get_shop_id()},
                                                                             {"$set": self.data})
            if result.raw_result["ok"] != 1:
                return False
            return True
        else:
            return True

    def delete_variable(self, key):
        data = flatten_dict(self.data)
        if key not in data:
            return False
        del data[key]
        return True

    # base variables

    def get_shop_type(self):
        return self.get_variable("shop_type")

    def get_shop_id(self):
        return self.get_variable("shop_id")

    def is_admin(self) -> bool:
        return self.get_variable("admin")

    def get_price(self) -> int:
        return self.get_variable("price")

    # shop functions

    def set_shop_type(self):
        pass # must do

    def allowed_to_use_shop(self, order: OrderRequest):
        for function in self.functions:
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if self.get_shop_type() not in function.allowed_shop_type: continue
            if not function.is_allowed_to_use_shop(order): return False
        return True

    def perform_action(self, order: OrderRequest):
        if not self.allowed_to_use_shop(order):
            return False

        for function in self.functions:
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if self.get_shop_type() not in function.allowed_shop_type: continue
            if not self.perform_action(order): return False

        for function in self.functions:
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if self.get_shop_type() not in function.allowed_shop_type: continue
            function.after_perform_action(order)

        # send success message?
        # log ?

        return True
