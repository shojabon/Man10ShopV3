from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Optional

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.common_variables.common_variables import player_schema, location_schema
from Man10ShopV3.data_class.Sign import Sign
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class CreateShopMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods
        self.schema = {
            "type": "object",
            "properties": {
                "player": player_schema,
                "admin": {
                    "type": "boolean"
                },
                "name": {
                    "type": "string"
                }
            },
            "required": ["player", "name"]

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("create", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def create_shop(json_body: dict):
            try:

                if "admin" in json_body and json_body["admin"]:
                    if not self.methods.main.api.create_shop(None, "BUY", json_body["name"], True):
                        return "error_internal"
                    return "success"

                player = None

                if "player" in json_body:
                    player = Player().load_from_json(json_body["player"], self.methods.main)

                if not self.methods.main.api.create_shop(player, "BUY", json_body["name"], False):
                    return "error_internal"
                return "success"
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
