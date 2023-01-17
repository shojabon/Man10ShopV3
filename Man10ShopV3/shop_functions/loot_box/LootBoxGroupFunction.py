from threading import Thread
from typing import List

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Response import RequestResponse
from Man10ShopV3.data_class.ShopFunction import ShopFunction
from Man10ShopV3.data_class.loot_box.LootBoxGroupData import LootBoxGroup


class LootBoxGroupFunction(ShopFunction):
    allowed_shop_type = ["LOOT_BOX"]

    def on_function_init(self):
        self.set_variable("groups", []) # LootBoxGroup object

    def get_groups(self) -> List[LootBoxGroup]:
        return [LootBoxGroup().from_json(x) for x in self.get("groups")]
