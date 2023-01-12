from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from utils.JsonTools import flatten_dict

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class Man10ShopV3API:

    def __init__(self, main: Man10ShopV3):
        self.main = main

        self.shops: dict[str, Shop] = {}

    def get_shop(self, shop_id) -> Shop:
        shop_object = self.main.mongo["man10shop_v3"]["shops"].find_one({"shopId": shop_id})
        del shop_object["_id"]
        shop = Shop(shop_object)
        shop.api = self
        self.shops[shop_id] = shop
        return self.shops[shop_id]

    def create_shop(self, owner: Player, name: str, price: int, shop_type: str, admin: bool):
        shop = Shop({
            "shopId": str(uuid.uuid1()),
            "shopType": shop_type,
            "price": {"price": price},
            "name": {"name": name},
            "admin": admin,
        })
        shop.api = self
        shop.permission_function.set_permission(owner, "OWNER")
        self.main.mongo["man10shop_v3"]["shops"].update_one({"shopId": shop.get_shop_id()}, {"$set": shop.get_export_data()}, upsert=True)

    def get_player_shops(self, player: Player):
        try:
            query = {"permission.users." + player.uuid.replace("-", ""): {"$exists": True}}
            query = self.main.mongo["man10shop_v3"]["shops"].find(query, {"_id": 0, "shopId": 1})
            query = [self.get_shop(x["shopId"]) for x in query]
            return [x for x in query if x is not None]
        except Exception:
            return []

