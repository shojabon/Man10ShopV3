from typing import Optional

from Man10ShopV3.data_class.ItemStack import ItemStack
from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction
from Man10ShopV3.data_class.loot_box.LootBoxGroupData import LootBoxGroup


class LootBoxBigWinFunction(ShopFunction):
    allowed_shop_type = ["LOOT_BOX"]

    def on_function_init(self):

        self.shop.register_queue_callback("lootBox.win", self.big_win_notification)

    def big_win_notification(self, data):
        player: Player = data["player"]
        item = ItemStack().from_json(data["data"]["item"])

        group: LootBoxGroup = self.shop.loot_box_group_function.get_groups()[data["data"]["group_id"]]
        if group.big_win:
            player.execute_command_in_server("broadcast §e§l" + player.name + "さん§a§lは" + self.shop.name_function.get_name() + "で『" + item.display_name + "』§a§lが当たりました!", s_command=False)


