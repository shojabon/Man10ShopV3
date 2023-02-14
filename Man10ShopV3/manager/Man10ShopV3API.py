from __future__ import annotations

import datetime
import json
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from copy import copy, deepcopy
from threading import Thread
from typing import TYPE_CHECKING, Optional

import humps
import requests
from tqdm import tqdm

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.RconConnection import RconConnection
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.data_class.Sign import Sign

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class Man10ShopV3API:

    def __init__(self, main: Man10ShopV3):
        self.main = main

        self.shops: dict[str, Shop] = {}

        self.base_shop_object = Shop(self)
        self.base_shop_object.api = None
    def get_shop_id_from_location(self, sign: Sign):
        query = {"sign.signs." + str(sign.location_id()): {"$exists": True}}
        query = self.main.mongo["man10shop_v3"]["shops"].find_one(query, {"_id": 0, "shopId": 1})
        if query is None:
            return None
        return query["shopId"]

    def get_shop(self, shop_id) -> Optional[Shop]:
        if shop_id in self.shops:
            shop = self.shops.get(shop_id)
            return shop
        shop_object = self.main.mongo["man10shop_v3"]["shops"].find_one({"shopId": shop_id})
        if shop_object is None:
            return None
        del shop_object["_id"]
        shop = self.create_shop_instance()
        shop.from_json(shop_object)
        self.shops[shop_id] = shop
        return self.shops.get(shop_id)

    def create_shop(self, owner: Player, shop_type: str, name: str, admin: bool) -> bool:
        try:
            shop = self.create_shop_instance()
            shop_id = str(uuid.uuid4())
            shop.from_json({
                "shopId": shop_id,
                "shopType": shop_type,
                "admin": admin,
            })
            shop.name_function.set_name(name)
            if owner is not None:
                shop.permission_function.set_permission(owner, "OWNER", False)
            data = shop.get_export_data()
            self.main.mongo["man10shop_v3"]["shops"].update_one({"shopId": shop.get_shop_id()},
                                                                {"$set": data}, upsert=True)
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
        except Exception:
            traceback.print_exc()
            return []
        result = []
        for query_data in query:
            try:
                result.append(self.get_shop(query_data["shopId"]))
            except Exception:
                traceback.print_exc()
                continue

        return [x for x in result if x is not None]

    def http_request(self, endpoint: str, path: str, method: str = "POST", payload: dict = None, return_json: bool = True):
        try:
            req = {}
            print("req endpoint", self.main.config["api"]["endpoint"].replace("{endpoint}", endpoint) + path)
            if method == "GET":
                req = requests.get(self.main.config["api"]["endpoint"].replace("{endpoint}", endpoint) + path,
                                   data=payload, headers={"x-api-key": self.main.config["api"]["key"]}, verify=False)
            if method == "POST":
                req = requests.post(self.main.config["api"]["endpoint"].replace("{endpoint}", endpoint) + path,
                                    data=payload, headers={"x-api-key": self.main.config["api"]["key"]}, verify=False)

            if req.status_code != 200:
                return None
            if return_json:
                return json.loads(req.text)
            else:
                return req.text
        except Exception as e:
            traceback.print_exc()
            return None

    def execute_command_in_server(self, endpoint, command, execute_async: bool = False, queue_key: str = None):
        if execute_async:
            return self.main.command_queue.get(endpoint).execute_command_async(command, RconConnection.get_queue_id_from_text(queue_key, 10))
        return self.main.command_queue.get(endpoint).execute_command(command, RconConnection.get_queue_id_from_text(queue_key, 10))
        result = self.main.api.http_request(endpoint, "/server/exec", "POST", {
            "command": command
        }, False)
        print("executing command", command, "in server", endpoint, "result", result)
        return result

    def update_log(self, log_id: str, data: dict):
        try:
            self.main.mongo["man10shop_v3"]["trade_log"].update_one({"logId": log_id}, {"$set": humps.camelize(data)})
            return True
        except Exception:
            traceback.print_exc()
            return False

    def create_shop_instance(self) -> Shop:
        shop = deepcopy(self.base_shop_object)
        shop.api = self
        return shop

    def load_all_shops(self):
        start = datetime.datetime.now().timestamp()
        shops_query = self.main.mongo["man10shop_v3"]["shops"].find({})
        for shop in tqdm(shops_query):
            del shop["_id"]
            copy_shop: Shop = self.create_shop_instance()
            copy_shop.from_json(shop)
            self.shops[copy_shop.get_shop_id()] = copy_shop
        print("all shops loaded in ", datetime.datetime.now().timestamp() - start)


