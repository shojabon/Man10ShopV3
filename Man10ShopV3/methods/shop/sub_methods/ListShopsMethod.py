from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Optional

import docker

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.common_variables.common_variables import player_schema
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class ListShopsMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods
        self.schema = {
            "type": "object",
            "properties": {
                "admin": {
                    "type": "boolean"
                },
                "player": player_schema,
            },
            "required": ["player"]

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("list", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def shop_list(json_body: dict):
            try:
                player = Player().load_from_json(json_body["player"], self.methods.main)
                shops = self.methods.main.api.get_player_shops(player)

                if "admin" in json_body and json_body["admin"]:
                    shops = self.methods.main.api.get_admin_shops()

                results = []
                for shop in shops:
                    permission = shop.permission_function.get_permission(player)
                    if shop.delete_function.is_deleted(): continue
                    if permission is None:
                        permission = "ERROR"
                    results.append({
                        "shopId": shop.get_shop_id(),
                        "name": shop.name_function.get_name(),
                        "shopType": shop.get_shop_type(),
                        "icon": shop.target_item_function.get_target_item(),
                        "permission": permission,
                        "money": shop.money_function.get_money(),
                        "itemCount": shop.storage_function.get_item_count(),
                        "category": shop.category_function.get_category()
                    })
                results = sorted(results, key=lambda x: x["category"] + "-" + x["name"], reverse=False)
                return "success", results
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
