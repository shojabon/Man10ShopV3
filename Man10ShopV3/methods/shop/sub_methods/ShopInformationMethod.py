from __future__ import annotations

import time
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


class ShopInformationMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods
        self.schema = {
            "type": "object",
            "properties": {
                "shopId": {
                    "type": "string"
                },
                "requestPlayer": player_schema,
                "sign": location_schema
            }

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("info", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def shop_information(json_body: dict):
            try:
                shop_id = None
                if "shop_id" in json_body:
                    shop_id = json_body["shop_id"]
                if "sign" in json_body:
                    sign = Sign()
                    sign.from_json(json_body["sign"])
                    shop_id = self.methods.main.api.get_shop_id_from_location(sign)

                if shop_id is None:
                    return "shop_invalid"

                shop = self.methods.main.api.get_shop(shop_id)
                if shop is None:
                    return "shop_invalid"
                result = shop.get_export_data()
                player = None

                if "player" in json_body:
                    player = Player().load_from_json(json_body["player"], self.methods.main)
                    result["playerPermission"] = shop.permission_function.get_permission(player)

                menu_info = shop.get_menu_info(player)
                result["menu_info"] = menu_info
                result["menu_info"]["trade_item_count"] = shop.get_item_count(player)

                result["sign_info"] = shop.get_sign_info()
                return "success", result
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
