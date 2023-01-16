from __future__ import annotations

import traceback
from threading import Thread
from typing import TYPE_CHECKING, Optional

import docker
import humps

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.common_variables.common_variables import player_schema
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class SetVariable:

    def __init__(self, methods: ShopMethods):
        self.methods = methods
        self.schema = {
            "type": "object",
            "properties": {
                "player": player_schema,
                "key": {
                    "type": "string"
                },
                "shopId": {
                    "type": "string"
                }
            },
            "required": ["shopId", "key", "value"]

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("/variable/set", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def variable_set(json_body: dict):
            try:
                owning_permission = "OWNER"
                required_permission = "MODERATOR"
                shop = self.methods.main.api.get_shop(json_body["shop_id"])
                if shop is None:
                    return "shop_invalid"

                json_body["key"] = humps.decamelize(json_body["key"])

                if "player" in json_body:
                    player = Player().load_from_json(json_body["player"], self.methods.main)
                    owning_permission = shop.permission_function.get_permission(player)

                if json_body["key"] in shop.variable_permissions:
                    required_permission = shop.variable_permissions[json_body["key"]]

                if not shop.permission_function.has_permission_at_least(required_permission, owning_permission):
                    return "permission_insufficient"

                if not shop.set_variable(json_body["key"], json_body["value"], True, player=player):
                    return "error_internal"

                def update_signs():
                    shop.sign_function.update_signs()
                Thread(target=update_signs).start()

                return "success"
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
