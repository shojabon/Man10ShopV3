from __future__ import annotations
import json

import requests

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class Player(object):
    main: Man10ShopV3 = None

    name: str = None
    uuid: str = None
    balance: int = 0

    endpoint: str = None

    def http_request(self, endpoint: str, path: str, method: str = "POST", payload: dict = None):
        try:
            req = {}
            if method == "GET":
                req = requests.get(self.main.config["api"]["endpoint"].replace("{endpoint}", endpoint) + path,
                                   data=payload, headers={"x-api-key": self.main.config["api"]["key"]})
            if method == "POST":
                req = requests.post(self.main.config["api"]["endpoint"].replace("{endpoint}", endpoint) + path,
                                    data=payload, headers={"x-api-key": self.main.config["api"]["key"]})

            if req.status_code != 200:
                return None
            return json.loads(req.text)
        except Exception:
            return None

    def send_message(self, endpoint, message):
        return self.http_request(endpoint, "/chat/tell", "POST", {
            "message": message,
            "playerUuid": self.uuid
        })

    def success_message(self, message: str):
        return self.send_message(self.endpoint, "§6[§eMan10Shop§dV3§6]§a§l" + message)

    def warn_message(self, message: str):
        return self.send_message(self.endpoint, "§6[§eMan10Shop§dV3§6]§c§l" + message)

    def get_player_data(self):
        return self.http_request(self.endpoint, "/players/" + str(self.uuid), "GET")

    # economy

    def get_balance(self) -> float:
        player_data = self.get_player_data()
        return player_data["balance"]

    def give_money(self, amount: float):
        result = self.http_request(self.endpoint, "/economy/pay", "POST", {
            "uuid": self.uuid,
            "amount": amount
        })
        if result is None:
            return False
        return True

    def take_money(self, amount: float):
        result = self.http_request(self.endpoint, "/economy/debit", "POST", {
            "uuid": self.uuid,
            "amount": amount
        })
        if result is None:
            return False
        return True
