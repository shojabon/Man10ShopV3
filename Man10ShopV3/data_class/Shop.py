from __future__ import annotations

from typing import TYPE_CHECKING
import humps

from Man10ShopV3.data_class.ShopFunction import ShopFunction
from Man10ShopV3.shop_functions.MoneyFunction import MoneyFunction
from Man10ShopV3.shop_functions.StorageFunction import StorageFunction
from utils.JsonTools import flatten_dict, unflatten_dict

if TYPE_CHECKING:
    from Man10ShopV3.manager.Man10ShopV3API import Man10ShopV3API

from Man10ShopV3.data_class.OrderRequest import OrderRequest

class Shop(object):

    api: Man10ShopV3API = None

    def __init__(self, data):
        self.data = humps.decamelize(data)

        self.functions: list[ShopFunction] = []

        self.money_function: MoneyFunction = self.register_function("money", MoneyFunction())
        self.storage_function: StorageFunction = self.register_function("storage", StorageFunction())

    def get_export_data(self):
        return humps.camelize(self.data)

    def register_function(self, prefix: str, function: ShopFunction):
        function.shop = self
        function.config_prefix = prefix
        self.functions.append(function)
        return function

    # variable

    def get_variable(self, key):
        data = flatten_dict(self.data)
        return data.get(key)

    def set_variable(self, key, value):
        data = flatten_dict(self.data)
        data[key] = value
        self.data = unflatten_dict(data)
        self.api.main.mongo["man10shop_v3"]["shops"].update_one({"shopId": self.get_shop_id()}, {"$set": self.data})

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
