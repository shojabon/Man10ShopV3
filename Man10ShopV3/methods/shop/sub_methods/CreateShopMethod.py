from __future__ import annotations

import json
import traceback
from typing import TYPE_CHECKING, Optional

import humps

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.common_variables.common_variables import player_schema, location_schema, PlayerBaseModel
from Man10ShopV3.data_class.Sign import Sign
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper
from pydantic import BaseModel

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class CreateShopRequest(BaseModel):
    player: PlayerBaseModel
    name: str
    admin: Optional[bool] = False


class CreateShopMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods

        @self.methods.main.app.post("/shop/create")
        async def create_shop(request: CreateShopRequest, lang: Optional[str] = "jp"):
            try:
                request.player = humps.decamelize(request.player.dict())

                if request.admin:
                    if not self.methods.main.api.create_shop(None, "BUY", request.name, True):
                        return self.methods.response_object("error_internal")
                    return self.methods.response_object("success")

                player = None
                if request.player:
                    player = Player().load_from_json(request.player, self.methods.main)

                if not self.methods.main.api.create_shop(player, "BUY", request.name, False):
                    return self.methods.response_object("error_internal")
                return self.methods.response_object("success")
            except Exception as e:
                traceback.print_exc()
                return self.methods.response_object("error_internal")
