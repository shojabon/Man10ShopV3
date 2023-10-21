from __future__ import annotations

import time
import traceback
import json
from typing import TYPE_CHECKING, Optional

import humps
from pydantic import BaseModel

from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.Shop import Shop
from Man10ShopV3.common_variables.common_variables import PlayerBaseModel, LocationBaseModel
from Man10ShopV3.data_class.Sign import Sign

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class ShopInformationRequest(BaseModel):
    shopId: Optional[str] = None
    player: Optional[PlayerBaseModel] = None
    sign: Optional[LocationBaseModel] = None


class ShopInformationMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods

        @self.methods.main.app.post("/shop/info")
        async def shop_information(request: ShopInformationRequest, lang: Optional[str] = "jp"):
            try:
                if request.player is not None:
                    request.player = humps.decamelize(request.player.dict())
                if request.sign is not None:
                    request.sign = humps.decamelize(request.sign.dict())

                shop_id = request.shopId
                if request.sign:
                    sign = Sign()
                    sign.from_json(request.sign)
                    shop_id = self.methods.main.api.get_shop_id_from_location(sign)

                if shop_id is None:
                    return self.methods.response_object("shop_invalid")

                shop = self.methods.main.api.get_shop(shop_id)
                if shop is None:
                    return self.methods.response_object("shop_invalid")

                result = shop.get_export_data()
                player = None

                if request.player:
                    player = Player().load_from_json(request.player, self.methods.main)
                    result["playerPermission"] = shop.permission_function.get_permission(player)

                menu_info = shop.get_menu_info(player)
                result["menu_info"] = menu_info
                result["menu_info"]["trade_item_count"] = shop.get_item_count(player)

                result["sign_info"] = shop.get_sign_info()
                return self.methods.response_object("success", result)
            except Exception as e:
                traceback.print_exc()
                return self.methods.response_object("error_internal", {"message": str(e)})