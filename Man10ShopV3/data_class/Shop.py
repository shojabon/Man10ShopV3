from __future__ import annotations

import datetime
import traceback
import uuid
from typing import TYPE_CHECKING, Callable, Any
import humps

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction
from Man10ShopV3.shop_functions.MoneyFunction import MoneyFunction
from Man10ShopV3.shop_functions.agent.MoneyRefillFunction import MoneyRefillFunction
from Man10ShopV3.shop_functions.allowed_to_use.DisabledFromFunction import DisabledFromFunction
from Man10ShopV3.shop_functions.allowed_to_use.EnabledFromFunction import EnabledFromFunction
from Man10ShopV3.shop_functions.barter.SetBarterFunction import SetBarterFunction
from Man10ShopV3.shop_functions.general.RandomPriceFunction import RandomPriceFunction
from Man10ShopV3.shop_functions.general.SecretPriceModeFunction import SecretPriceModeFunction
from Man10ShopV3.shop_functions.loot_box.LootBoxBigWinFunction import LootBoxBigWinFunction
from Man10ShopV3.shop_functions.loot_box.LootBoxGroupFunction import LootBoxGroupFunction
from Man10ShopV3.shop_functions.loot_box.LootBoxPaymentFunction import LootBoxPaymentFunction
from Man10ShopV3.shop_functions.tradeAmount.IpLimitFunction import IpLimitFunction
from Man10ShopV3.shop_functions.tradeAmount.LimitUseFunction import LimitUseFunction
from Man10ShopV3.shop_functions.allowed_to_use.WeekDayToggleFunction import WeekDayToggleFunction
from Man10ShopV3.shop_functions.general.DeleteShopFunction import DeleteShopFunction
from Man10ShopV3.shop_functions.general.NameFunction import NameFunction
from Man10ShopV3.shop_functions.PermissionFunction import PermissionFunction
from Man10ShopV3.shop_functions.general.PriceFunction import PriceFunction
from Man10ShopV3.shop_functions.SignFunction import SignFunction
from Man10ShopV3.shop_functions.general.ShopEnabledFunction import ShopEnabledFunction
from Man10ShopV3.shop_functions.storage.StorageCapFunction import StorageCapFunction
from Man10ShopV3.shop_functions.storage.StorageFunction import StorageFunction
from Man10ShopV3.shop_functions.TargetItemFunction import TargetItemFunction
from Man10ShopV3.shop_functions.general.CategoryFunction import CategoryFunction
from Man10ShopV3.shop_functions.storage.StorageRefillFunction import StorageRefillFunction
from Man10ShopV3.shop_functions.tradeAmount.CoolDownFunction import CoolDownFunction
from Man10ShopV3.shop_functions.tradeAmount.PerMinuteCoolDownFunction import PerMinuteCoolDownFunction
from Man10ShopV3.shop_functions.tradeAmount.SingleTransactionModeFunction import SingleTransactionModeFunction
from Man10ShopV3.shop_functions.tradeAmount.TotalPerMinuteCoolDownFunction import TotalPerMinuteCoolDownFunction
from utils.JsonSchemaWrapper import merge_dictionaries
from utils.JsonTools import flatten_dict, unflatten_dict

if TYPE_CHECKING:
    from Man10ShopV3.manager.Man10ShopV3API import Man10ShopV3API

from Man10ShopV3.data_class.OrderRequest import OrderRequest


class Shop(object):
    api: Man10ShopV3API = None

    variable_permissions = {}
    variable_check = {}
    dynamic_variables = {}

    def __init__(self, main: Man10ShopV3API):
        self.api = main
        self.data = {}
        self.functions: dict[str, ShopFunction] = {}
        self.queue_callbacks: dict[str, list[Callable]] = {}

        # general functions

        self.money_function: MoneyFunction = self.register_function("money", MoneyFunction())
        self.storage_function: StorageFunction = self.register_function("storage", StorageFunction())
        self.target_item_function: TargetItemFunction = self.register_function("target_item", TargetItemFunction())
        self.permission_function: PermissionFunction = self.register_function("permission", PermissionFunction())

        # general

        self.name_function: NameFunction = self.register_function("name", NameFunction())
        self.secret_price_mode_function: SecretPriceModeFunction = self.register_function("secret_price_mode",
                                                                                          SecretPriceModeFunction())
        self.sign_function: SignFunction = self.register_function("sign", SignFunction())
        self.category_function: CategoryFunction = self.register_function("category", CategoryFunction())
        self.delete_function: DeleteShopFunction = self.register_function("delete", DeleteShopFunction())
        self.price_function: PriceFunction = self.register_function("price", PriceFunction())
        self.shop_enabled_function: ShopEnabledFunction = self.register_function("shop_enabled", ShopEnabledFunction())
        self.random_price_function: RandomPriceFunction = self.register_function("random_price", RandomPriceFunction())

        # allowed to use
        self.disabled_from_function: DisabledFromFunction = self.register_function("disabled_from",
                                                                                   DisabledFromFunction())
        self.enabled_from_function: EnabledFromFunction = self.register_function("enabled_from", EnabledFromFunction())
        self.limit_use_function: LimitUseFunction = self.register_function("limit_use", LimitUseFunction())
        self.weekday_toggle: WeekDayToggleFunction = self.register_function("weekday_toggle", WeekDayToggleFunction())

        # storage
        self.storage_cap_function: StorageCapFunction = self.register_function("storage_cap", StorageCapFunction())
        self.storage_refill_function: StorageRefillFunction = self.register_function("storage_refill",
                                                                                     StorageRefillFunction())

        # trade amount
        self.cool_down_function: CoolDownFunction = self.register_function("cool_down", CoolDownFunction())
        self.single_transaction_mode: SingleTransactionModeFunction = self.register_function("single_transaction_mode",
                                                                                             SingleTransactionModeFunction())
        self.per_minute_cool_down_function: PerMinuteCoolDownFunction = self.register_function("per_minute_cool_down",
                                                                                               PerMinuteCoolDownFunction())
        self.total_per_minute_cool_down_function: TotalPerMinuteCoolDownFunction = self.register_function(
            "total_per_minute_cool_down", TotalPerMinuteCoolDownFunction())

        self.ip_limit_function: IpLimitFunction = self.register_function(
            "ip_limit", IpLimitFunction())

        # barter
        self.set_barter_function: SetBarterFunction = self.register_function("set_barter", SetBarterFunction())

        # loot box
        self.loot_box_group_function: LootBoxGroupFunction = self.register_function("loot_box_group", LootBoxGroupFunction())
        self.loot_box_payment_function: LootBoxPaymentFunction = self.register_function("loot_box_payment", LootBoxPaymentFunction())
        self.loot_box_big_win_function: LootBoxBigWinFunction = self.register_function("loot_box_big_win", LootBoxBigWinFunction())

        # agent
        self.money_refill_function: MoneyRefillFunction = self.register_function("money_refill", MoneyRefillFunction())


        self.register_queue_callback("shop.order", self.accept_order)

    def from_json(self, data: dict):
        self.data = merge_dictionaries(self.data, humps.decamelize(data))

    def get_export_data(self):
        return humps.camelize(merge_dictionaries(self.data, self.dynamic_variables))

    def register_function(self, prefix: str, function: ShopFunction) -> Any:
        function.shop = self
        function.config_prefix = prefix

        function.on_function_init()
        self.functions[prefix] = function
        return self.functions[prefix]

    def register_queue_callback(self, key: str, function: Callable):
        if key not in self.queue_callbacks:
            self.queue_callbacks[key] = []
        self.queue_callbacks[key].append(function)

    def execute_queue_callback(self, key: str, data: dict):
        if key not in self.queue_callbacks:
            return
        for function in self.queue_callbacks[key]:
            try:
                function(data)
            except Exception:
                traceback.print_exc()
                pass

    # variable

    def get_variable(self, key):
        data = flatten_dict(self.data)
        return data.get(key)

    def set_variable(self, key, value, update_db=True, player: Player = None, variable_check: bool = True):
        if variable_check and key in self.variable_check:
            try:

                if not self.variable_check[key](self, player, value):
                    return False
            except Exception:
                traceback.print_exc()
                return False

        data = flatten_dict(self.data)
        data[key] = value
        self.data = unflatten_dict(data)

        if update_db:
            result = self.api.main.mongo["man10shop_v3"]["shops"].update_one({"shopId": self.get_shop_id()},
                                                                             {"$set": humps.camelize(self.data)})
            if result.raw_result["ok"] != 1:
                return False
            return True
        else:
            return True

    def set_dynamic_variable(self, key: str, value):
        data = flatten_dict(self.dynamic_variables)
        data[key] = value
        self.dynamic_variables = unflatten_dict(data)
        return True

    # base variables

    def get_shop_type(self):
        return self.get_variable("shop_type")

    def get_shop_type_string(self):
        shop_type = self.get_shop_type()
        if shop_type == "SELL":
            return "買取りショップ"
        if shop_type == "BUY":
            return "販売ショップ"
        if shop_type == "BARTER":
            return "トレードショップ"
        if shop_type == "LOOT_BOX":
            return "ガチャショップ"

    def set_shop_type(self, shop_type: str):
        return self.set_variable("shop_type", shop_type, True)

    def get_shop_id(self):
        return self.get_variable("shop_id")

    def is_admin(self) -> bool:
        return self.get_variable("admin")

    # queue task

    def accept_order(self, data):
        if "amount" not in data["data"]:
            return

        order = OrderRequest()
        order.amount = data["data"]["amount"]
        order.player = data["player"]
        order.log_id = str(uuid.uuid1())
        if not self.perform_action(order):
            return

        if self.get_shop_type() == "BUY":
            order.player.success_message(str(order.amount) + "個の購入に成功しました")
        if self.get_shop_type() == "SELL":
            order.player.success_message(str(order.amount) + "個の売却に成功しました")
        if self.get_shop_type() == "BARTER":
            order.player.success_message("トレードに成功しました")



        self.log_order(order)

    # shop functions

    def allowed_to_use_shop(self, order: OrderRequest):
        for function in self.functions.values():
            function: ShopFunction = function
            if not function.is_function_enabled():
                continue
            if len(function.allowed_shop_type) != 0 and self.get_shop_type() not in function.allowed_shop_type:
                continue
            if not function.is_allowed_to_use_shop(order):
                print("out", function)
                return False
        return True

    def execute_per_minute_execution_task(self):
        for function in self.functions.values():
            function: ShopFunction = function
            if not function.is_function_enabled():
                continue
            if len(function.allowed_shop_type) != 0 and self.get_shop_type() not in function.allowed_shop_type:
                continue
            function.per_minute_execution_task()
        return True

    def perform_action(self, order: OrderRequest):
        if not self.allowed_to_use_shop(order):
            return False

        for function in self.functions.values():
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if len(function.allowed_shop_type) != 0 and self.get_shop_type() not in function.allowed_shop_type: continue
            if not function.perform_action(order): return False

        for function in self.functions.values():
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if len(function.allowed_shop_type) != 0 and self.get_shop_type() not in function.allowed_shop_type: continue
            function.after_perform_action(order)

        return True

    def get_item_count(self, player: Player):
        result = self.storage_function.get_storage_size()

        for function in self.functions.values():
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if len(function.allowed_shop_type) != 0 and self.get_shop_type() not in function.allowed_shop_type: continue
            count = function.item_count(player)
            if count is None: continue
            if count < result:
                print("item count", function, count)
                result = count

        return abs(result)

    def get_menu_info(self, player: Player):
        result = {}
        for function in self.functions.values():
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if len(function.allowed_shop_type) != 0 and self.get_shop_type() not in function.allowed_shop_type: continue
            info = function.menu_info(player)
            if info is None: continue
            result = merge_dictionaries(result, info)
        return result

    def get_sign_info(self):
        result = [
            "ショップ",
            "",
            "",
            ""
        ]
        if self.get_shop_type() == "BUY":
            result[0] = "§a§l販売ショップ"

        if self.get_shop_type() == "SELL":
            result[0] = "§c§l買取ショップ"

        if self.get_shop_type() == "BARTER":
            result[0] = "§b§lトレードショップ"

        if self.get_shop_type() == "LOOT_BOX":
            result[0] = "§d§lガチャ"

        for function in self.functions.values():
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if len(function.allowed_shop_type) != 0 and self.get_shop_type() not in function.allowed_shop_type: continue
            info = function.sign_information(result)
            if info is None: continue
            for x in range(len(result)):
                if info[x] == "" or info[x] is None: continue
                result[x] = info[x]
        return result

    def get_log_data(self, order: OrderRequest):
        result = {}
        for function in self.functions.values():
            function: ShopFunction = function
            if not function.is_function_enabled(): continue
            if len(function.allowed_shop_type) != 0 and self.get_shop_type() not in function.allowed_shop_type: continue
            info = function.log_data(order)
            if info is None: continue
            result = merge_dictionaries(result, info)
        return result

    def log_order(self, order: OrderRequest):
        log_object = {
            "log_id": order.log_id,
            "shop_id": self.get_shop_id(),
            "shop_type": self.get_shop_type(),
            "player": order.player.get_json(),
            "order_data": self.get_log_data(order),
            "time": datetime.datetime.now()
        }
        log_object = humps.camelize(log_object)
        self.api.main.mongo["man10shop_v3"]["trade_log"].insert_one(log_object)
