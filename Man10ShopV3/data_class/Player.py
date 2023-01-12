from __future__ import annotations
import json
import traceback

import requests

from typing import TYPE_CHECKING

from Man10ShopV3.data_class.ItemStack import ItemStack

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class Player(object):
    main: Man10ShopV3 = None

    name: str = None
    uuid: str = None
    balance: int = 0

    endpoint: str = None

    inventory: dict[str, ItemStack] = None

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
            return None

    def send_message(self, message):
        return self.http_request("/chat/tell", "POST", {
            "message": message,
            "playerUuid": self.uuid
        })

    def item_give(self, item: ItemStack, amount: int):
        command = "mshop itemGive " + self.uuid + " " + item.base64_type + " " + str(amount)
        result = self.execute_command_in_server(command)
        if result == "success":
            return True
        return False

    def item_take(self, item: ItemStack, amount: int):
        command = "mshop itemTake " + self.uuid + " " + item.base64_type + " " + str(amount)
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

    def get_player_data(self):
        return self.http_request("/players/" + str(self.uuid), "GET")

    # economy

    def get_balance(self) -> float:
        player_data = self.get_player_data()
        return player_data["balance"]

    def give_money(self, amount: float):
        result = self.http_request("/economy/pay", "POST", {
            "uuid": self.uuid,
            "amount": amount
        })
        if result is None:
            return False
        return True

    def take_money(self, amount: float):
        result = self.http_request("/economy/debit", "POST", {
            "uuid": self.uuid,
            "amount": amount
        })
        if result is None:
            return False
        return True
