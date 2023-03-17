from __future__ import annotations
import json
import traceback
import uuid

import humps
import requests

from typing import TYPE_CHECKING

from Man10ShopV3.data_class.Response import RequestResponse
from utils.JsonTools import flatten_dict

if TYPE_CHECKING:
    from Man10ShopV3.data_class.ShopFunction import ShopFunction
    from Man10ShopV3 import Man10ShopV3

class Player(object):
    main: Man10ShopV3 = None

    name: str = None
    uuid: str = None
    ip_address: str = None

    server: str = None

    player_data_cache = {}

    def load_from_json(self, data: dict, main: Man10ShopV3):
        self.name = data.get("name")
        self.main = main
        self.uuid = data.get("uuid")
        self.ip_address = data.get("ip_address")
        self.server = data.get("server")
        if self.server is None:
            self.server = "man10"

        self.inventory = data.get("inventory")
        return self

    def get_json(self):
        data = {
            "uuid": self.uuid,
            "name": self.name,
            "server": self.server,
            "ip_address": self.ip_address
        }
        return data

    # ======= data store =========
    def set_data(self, shop_function: ShopFunction, key: str, data):
        key = shop_function.shop.get_shop_id() + "." + shop_function.config_prefix + "." + key
        if self.uuid in Player.player_data_cache:
            current_data = Player.player_data_cache[self.uuid]
            current_data[humps.camelize(key)] = data

        def task():
            if data is None:
                self.main.mongo["man10shop_v3"]["player_data"].update_one({
                    "uuid": self.uuid
                }, {humps.camelize(key): {"$unset": True}})
                return True
            else:
                result = self.main.mongo["man10shop_v3"]["player_data"].update_one({
                    "uuid": self.uuid,
                }, {"$set": {humps.camelize(key): data}}, upsert=True)
                if result.raw_result["ok"] != 1:
                    return False
                return True

        self.main.thread_pool.submit(task)


    def get_data(self, shop_function: ShopFunction, key: str, default = None):
        if self.uuid not in Player.player_data_cache:
            result = self.main.mongo["man10shop_v3"]["player_data"].find_one({"uuid": self.uuid})
            if result is None:
                if default is not None:
                    self.set_data(shop_function, key, default)
            result = flatten_dict(result, max_depth=2)
            Player.player_data_cache[self.uuid] = result

        result = Player.player_data_cache[self.uuid]
        if result is None:
            result = {}
        key = shop_function.shop.get_shop_id() + "." + shop_function.config_prefix + "." + key
        key = humps.camelize(key)
        if key not in result:
            if default is not None:
                return default
            return None
        return result.get(key)

    # ======= minecraft functions ========
    def send_message(self, message):
        return self.main.api.http_request(self.server, "/chat/tell", "POST", {
            "message": message,
            "playerUuid": self.uuid
        })

    def execute_command_in_server(self, command: str, execute_async: bool = False, s_command: bool = True):
        result = self.main.api.execute_command_in_server(self.server, command, execute_async, s_command=s_command)
        return RequestResponse(result)

    def item_give(self, item_base64, amount: int):
        command = "mshop itemGive " + self.uuid + " " + item_base64 + " " + str(amount)
        return self.execute_command_in_server(command)

    def item_take(self, item_base64, amount: int):
        command = "mshop itemTake " + self.uuid + " " + item_base64 + " " + str(amount)
        return self.execute_command_in_server(command)

    def has_inventory_space(self):
        command = "mshop inventoryHasSpace " + self.uuid
        return self.execute_command_in_server(command)

    def item_check(self, item_base64, amount: int):
        command = "mshop itemCheck " + self.uuid + " " + item_base64 + " " + str(amount)
        return self.execute_command_in_server(command)

    def success_message(self, message: str):
        return self.send_message("§6[§eMan10Shop§dV3§6]§a§l" + message)

    def warn_message(self, message: str):
        return self.send_message("§6[§eMan10Shop§dV3§6]§c§l" + message)

    # economy

    def get_balance(self) -> float | None:
        command = "mshop moneyGet " + self.uuid
        result = self.main.api.execute_command_in_server(self.server, command)
        result = result.split(",")
        if result[0] != "success":
            return None
        return float(result[1])

    def give_money(self, amount: float):
        return self.execute_command_in_server("mshop moneyGive " + self.uuid + " " + str(amount))

    def take_money(self, amount: float):
        return self.execute_command_in_server("mshop moneyTake " + self.uuid + " " + str(amount))

    # uuid tools
    def get_uuid_formatted(self):
        return self.uuid.replace("-", "").lower()

    def set_uuid_formatted(self, formatted_uuid: str):
        self.uuid = str(uuid.UUID(hex=formatted_uuid))