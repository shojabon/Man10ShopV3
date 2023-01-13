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


class ShopInformationMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods
        self.schema = {
            "type": "object",
            "properties": {
                "shopId": {
                    "type": "string"
                },
                "requestPlayer": player_schema
            },
            "required": ["shopId"]

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("info", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def shop_information(json_body: dict):
            try:
                shop = self.methods.main.api.get_shop(json_body["shop_id"])
                if shop is None:
                    return "shop_invalid",
                result = shop.get_export_data()

                if "player" in json_body:
                    player = Player().load_from_json(json_body["player"])
                    result["playerPermission"] = shop.permission_function.get_permission(player)

                return "success", result
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
