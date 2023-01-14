from __future__ import annotations
import json
import traceback
import uuid

import humps
import requests

from typing import TYPE_CHECKING

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.Response import RequestResponse
from utils.JsonTools import flatten_dict
from utils.MatResponseWrapper import get_error_message

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class Player(object):
    main: Man10ShopV3 = None

    name: str = None
    uuid: str = None
    balance: int = 0

    endpoint: str = None

    inventory: dict[str, ItemStack] = None

    def load_from_json(self, data: dict, main: Man10ShopV3):
        self.name = data.get("name")
        self.main = main
        self.uuid = data.get("uuid")
        self.balance = data.get("balance")
        self.endpoint = data.get("endpoint")
        if self.endpoint is None:
            self.endpoint = "man10"

        self.inventory = data.get("inventory")
        return self

    # ======= data store =========
    def set_data(self, shop_id: str, key:str, data):
        key = shop_id + "." + key
        if data is None:
            self.main.mongo["man10shop_v3"]["player_data"].update_one({
                "uuid": self.uuid
            }, {humps.camelize(key): {"$unset": True}})
            return True
        else:
            result = self.main.mongo["man10shop_v3"]["player_data"].update_one({
                "shopId": shop_id,
            }, {humps.camelize(key): data})
            if result.raw_result["ok"] != 1:
                return False
            return True

    def get_data(self, shop_id: str, key: str):
        result = self.main.mongo["man10shop_v3"]["player_data"].find_one({"uuid": self.uuid})
        if result is None:
            return None
        key = shop_id + "." + key
        key = humps.camelize(key)
        result = flatten_dict(result)
        if key not in result:
            return None
        return result[key]

    # ======= minecraft functions ========
    def send_message(self, message):
        return self.main.api.http_request(self.endpoint, "/chat/tell", "POST", {
            "message": message,
            "playerUuid": self.uuid
        })

    def item_give(self, item_base64, amount: int):
        command = "mshop itemGive " + self.uuid + " " + item_base64 + " " + str(amount)
        result = self.main.api.execute_command_in_server(self.endpoint, command)
        return RequestResponse(result)

    def item_take(self, item_base64, amount: int):
        command = "mshop itemTake " + self.uuid + " " + item_base64 + " " + str(amount)
        result = self.main.api.execute_command_in_server(self.endpoint, command)
        return RequestResponse(result)

    def item_check(self, item_base64, amount: int):
        command = "mshop itemCheck " + self.uuid + " " + item_base64 + " " + str(amount)
        result = self.main.api.execute_command_in_server(self.endpoint, command)
        return RequestResponse(result)

    def success_message(self, message: str):
        return self.send_message("§6[§eMan10Shop§dV3§6]§a§l" + message)

    def warn_message(self, message: str):
        return self.send_message("§6[§eMan10Shop§dV3§6]§c§l" + message)

    def get_player_data(self) -> dict:
        return self.main.api.http_request(self.endpoint, "/players/" + str(self.uuid), "GET")

    # economy

    def get_balance(self) -> float:
        player_data = self.get_player_data()
        return player_data["balance"]

    def give_money(self, amount: float):
        result = self.main.api.execute_command_in_server(self.endpoint, "mshop moneyGive " + self.uuid + " " + str(amount))
        return RequestResponse(result)

    def take_money(self, amount: float):
        result = self.main.api.execute_command_in_server(self.endpoint, "mshop moneyTake " + self.uuid + " " + str(amount))
        return RequestResponse(result)

    # uuid tools
    def get_uuid_formatted(self):
        return self.uuid.replace("-", "").lower()

    def set_uuid_formatted(self, formatted_uuid: str):
        self.uuid = str(uuid.UUID(hex=formatted_uuid))