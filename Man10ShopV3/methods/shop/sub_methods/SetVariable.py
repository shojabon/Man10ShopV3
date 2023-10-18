from __future__ import annotations

import json
import traceback
from threading import Thread
from typing import TYPE_CHECKING, Optional, Any

import humps
from pydantic import BaseModel

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.common_variables.common_variables import player_schema, PlayerBaseModel
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class SetVariableRequest(BaseModel):
    player: Optional[PlayerBaseModel]
    key: str
    shopId: str
    value: Any


class SetVariable:

    def __init__(self, methods: ShopMethods):
        self.methods = methods

        @self.methods.main.app.post("/shop/variable/set")
        async def variable_set(request: SetVariableRequest, lang: Optional[str] = "jp"):
            try:
                owning_permission = "OWNER"
                required_permission = "MODERATOR"
                shop = self.methods.main.api.get_shop(request.shopId)
                player = None
                if shop is None:
                    return "shop_invalid"

                request.key = humps.decamelize(request.key)

                if request.player:
                    player = Player().load_from_json(json.loads(request.player.json()), self.methods.main)
                    owning_permission = shop.permission_function.get_permission(player)

                if request.key in shop.variable_permissions:
                    required_permission = shop.variable_permissions[request.key]

                if not shop.is_admin() and not shop.permission_function.has_permission_at_least(required_permission, owning_permission):
                    return "permission_insufficient"
                if not shop.set_variable(request.key, request.value, True, player=player):
                    return "error_internal"

                def update_signs():
                    shop.sign_function.update_signs()

                Thread(target=update_signs).start()

                return self.methods.response_object("success")
            except Exception as e:
                traceback.print_exc()
                return self.methods.response_object("error_internal", {"message": str(e)})