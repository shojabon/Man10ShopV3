from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Optional

import docker

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.schema_defenetions.player_schema import player_schema
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class ShopMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods
        self.schema = {
            "type": "object",
            "properties": {
                "player": player_schema,
            },
            "required": ["player"]

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("", methods=["GET"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def shop_information(json_body: dict):
            try:
                player = Player().load_from_json(json_body["player"])
                shops = self.methods.main.api.get_player_shops(player)

                results = []
                for shop in shops:
                    permission = shop.permission_function.get_permission(player)
                    if permission is None:
                        permission = "ERROR"
                    results.append({
                        "shopId": shop.get_shop_id(),
                        "name": shop.name_function.get_name(),
                        "permission": permission,
                        "money": shop.money_function.get_money(),
                        "itemCount": shop.storage_function.get_item_count()
                    })

                return "success", results
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
