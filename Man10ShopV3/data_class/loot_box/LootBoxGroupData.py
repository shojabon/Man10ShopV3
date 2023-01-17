from typing import List

from Man10ShopV3.data_class.ItemStack import ItemStack


class LootBoxGroup(object):
    icon: str = "DIAMOND"  # Material Name
    items: List[ItemStack] = []  # ItemStack Object
    item_counts: List[int] = []
    big_win: bool = False
    weight: int = 0  # max 100000000

    def from_json(self, data: dict):
        self.icon = data.get("icon")
        self.big_win = data.get("big_win")

        if "items" not in data: data["items"] = []
        self.items = [ItemStack().from_json(x) for x in data.get("items")]
        self.weight = data.get("weight")
        self.item_counts = data.get("item_counts")
        return self

    def get_json(self):
        return {
            "icon": self.icon,
            "items": [x.get_json() for x in self.items],
            "big_win": self.big_win,
            "weight": self.weight,
            "item_counts": self.item_counts
        }
