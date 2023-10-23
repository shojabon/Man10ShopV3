from __future__ import annotations

import json
import traceback
from typing import TYPE_CHECKING, Optional

import humps
from pydantic import BaseModel

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.common_variables.common_variables import player_schema, PlayerBaseModel
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class WithdrawBuyShopMoneyRequest(BaseModel):
    player: PlayerBaseModel


class WithdrawBuyShopMoneyMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods

        @self.methods.main.app.post("/shop/withdraw_buy_shop_money")
        async def withdraw_buy_shop_money(request: WithdrawBuyShopMoneyRequest, lang: Optional[str] = "jp"):
            try:

                request.player = humps.decamelize(request.player.dict())

                player = Player().load_from_json(request.player, self.methods.main)
                shops = self.methods.main.api.get_player_shops(player)

                results = []
                for shop in shops:
                    if shop.delete_function.is_deleted(): continue
                    if shop.get_shop_type() != "BUY": continue
                    permission = shop.permission_function.get_permission(player)
                    if not shop.permission_function.has_permission_at_least("ACCOUNTANT", permission):
                        continue
                    results.append(shop)

                for shop in results:
                    if shop.money_function.get_money() <= 0: continue
                    self.methods.main.main_queue.put({
                        "key": "money.withdraw",
                        "shopId": shop.get_shop_id(),
                        "data": {
                            "amount": shop.money_function.get_money(),
                        },
                        "player": player.get_json(),
                    })

                return self.methods.response_object("success")
            except Exception as e:
                traceback.print_exc()
                return self.methods.response_object("error_internal", {"message": str(e)})

