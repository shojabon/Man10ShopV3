from __future__ import annotations

import json
import traceback
import uuid
from typing import TYPE_CHECKING, Optional

import requests

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.data_class.Sign import Sign
from utils.JsonTools import flatten_dict

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class Man10ShopV3API:

    def __init__(self, main: Man10ShopV3):
        self.main = main

        self.shops: dict[str, Shop] = {}

    def get_shop_id_from_location(self, sign: Sign):
        query = {"sign.signs." + str(sign.location_id()): {"$exists": True}}
        query = self.main.mongo["man10shop_v3"]["shops"].find_one(query, {"_id": 0, "shopId": 1})
        if query is None:
            return None
        return query["shopId"]

    def get_shop(self, shop_id) -> Optional[Shop]:
        if shop_id in self.shops:
            shop = self.shops[shop_id]
            return shop
        shop_object = self.main.mongo["man10shop_v3"]["shops"].find_one({"shopId": shop_id})
        if shop_object is None:
            return None
        del shop_object["_id"]
        shop = Shop(self)
        shop.from_json(shop_object)
        self.shops[shop_id] = shop
        return self.shops[shop_id]

    def create_shop(self, owner: Player, shop_type: str, name: str, admin: bool) -> bool:
        try:
            shop = Shop(self)
            shop.from_json({
                "shopId": str(uuid.uuid1()),
                "shopType": shop_type,
                "admin": admin,
            })
            shop.name_function.set_name(name)
            if owner is not None:
                shop.permission_function.set_permission(owner, "OWNER")
            self.main.mongo["man10shop_v3"]["shops"].update_one({"shopId": shop.get_shop_id()},
                                                                {"$set": shop.get_export_data()}, upsert=True)
            return True
        except Exception:
            traceback.print_exc()
            return False

    def get_player_shops(self, player: Player):
        try:
            query = {"permission.users." + player.uuid.replace("-", ""): {"$exists": True}}
            query = self.main.mongo["man10shop_v3"]["shops"].find(query, {"_id": 0, "shopId": 1})
            query = [self.get_shop(x["shopId"]) for x in query]
            return [x for x in query if x is not None]
        except Exception:
            traceback.print_exc()
            return []

    def get_admin_shops(self):
        try:
            query = {"admin": True}
            query = self.main.mongo["man10shop_v3"]["shops"].find(query, {"_id": 0, "shopId": 1})
            query = [self.get_shop(x["shopId"]) for x in query]
            return [x for x in query if x is not None]
        except Exception:
            return []

    def http_request(self, endpoint: str, path: str, method: str = "POST", payload: dict = None, return_json: bool = True):
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
            if return_json:
                return json.loads(req.text)
            else:
                return req.text
        except Exception as e:
            traceback.print_exc()
            return None

    def execute_command_in_server(self, endpoint, command):
        result = self.main.api.http_request(endpoint, "/server/exec", "POST", {
            "command": command
        }, False)
        print("executing command", command, "result", result)
        return result
