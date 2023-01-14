from __future__ import annotations
import json
import traceback
import uuid

import requests

from typing import TYPE_CHECKING

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.Response import RequestResponse
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

    def http_request(self, path: str, method: str = "POST", payload: dict = None, return_json: bool = True):
        try:
            req = {}
            if method == "GET":
                req = requests.get(self.main.config["api"]["endpoint"].replace("{endpoint}", self.endpoint) + path,
                                   data=payload, headers={"x-api-key": self.main.config["api"]["key"]})
            if method == "POST":
                req = requests.post(self.main.config["api"]["endpoint"].replace("{endpoint}", self.endpoint) + path,
                                    data=payload, headers={"x-api-key": self.main.config["api"]["key"]})

            if req.status_code != 200:
                return None
            if return_json:
                return json.loads(req.text)
            else:
                return req.text
        except Exception as e:
            traceback.print_exc()
            return None

    def send_message(self, message):
        return self.http_request("/chat/tell", "POST", {
            "message": message,
            "playerUuid": self.uuid
        })

    def item_give(self, item_base64, amount: int):
        command = "mshop itemGive " + self.uuid + " " + item_base64 + " " + str(amount)
        result = self.execute_command_in_server(command)
        if result == "success":
            return True
        return False

    def item_take(self, item_base64, amount: int):
        command = "mshop itemTake " + self.uuid + " " + item_base64 + " " + str(amount)
        result = self.execute_command_in_server(command)
        if result == "success":
            return True
        return False

    def execute_command_in_server(self, command):
        result = self.http_request("/server/exec", "POST", {
            "command": command
        }, False)
        return result

    def success_message(self, message: str):
        return self.send_message("§6[§eMan10Shop§dV3§6]§a§l" + message)

    def warn_message(self, message: str):
        return self.send_message("§6[§eMan10Shop§dV3§6]§c§l" + message)

    def get_player_data(self) -> dict:
        return self.http_request("/players/" + str(self.uuid), "GET")

    # economy

    def get_balance(self) -> float:
        player_data = self.get_player_data()
        return player_data["balance"]

    def give_money(self, amount: float):
        result = self.execute_command_in_server("mshop moneyGive " + self.uuid + " " + str(amount))
        return RequestResponse(result)

    def take_money(self, amount: float):
        result = self.execute_command_in_server("mshop moneyTake " + self.uuid + " " + str(amount))
        return RequestResponse(result)

    def get_uuid_formatted(self):
        return self.uuid.replace("-", "").lower()

    def set_uuid_formatted(self, formatted_uuid: str):
        self.uuid = str(uuid.UUID(hex=formatted_uuid))