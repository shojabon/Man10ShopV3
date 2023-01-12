from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from Man10ShopV3.data_class.Shop import Shop

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class Man10ShopV3API:

    def __init__(self, main: Man10ShopV3):
        self.main = main

        self.shops = {}

    def get_shop(self, shop_id) -> Shop:
        shop_object = self.main.mongo["man10shop_v3"]["shops"].find_one({"shopId": shop_id})
        del shop_object["_id"]
        shop = Shop(shop_object)
        shop.api = self
        self.shops[shop_id] = shop
        return self.shops[shop_id]

    def create_shop(self, owner: str, name: str, price: int, shop_type: str, admin: bool):
        shop = Shop({
            "shopId": str(uuid.uuid1()),
            "name": name,
            "shopType": shop_type,
            "price": price,
            "admin": admin,
        })
        self.main.mongo["man10shop_v3"]["shops"].insert_one(shop.get_export_data())



