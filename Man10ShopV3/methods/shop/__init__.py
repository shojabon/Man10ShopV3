from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint

from Man10ShopV3.methods.shop.sub_methods.CreateShopMethod import CreateShopMethod
from Man10ShopV3.methods.shop.sub_methods.GetAllShopIdsMethod import GetAllShopIdsMethod
from Man10ShopV3.methods.shop.sub_methods.QueueAddTaskMethod import QueueAddTaskMethod
from Man10ShopV3.methods.shop.sub_methods.SetVariable import SetVariable
from Man10ShopV3.methods.shop.sub_methods.ShopInformationMethod import ShopInformationMethod
from Man10ShopV3.methods.shop.sub_methods.ListShopsMethod import ListShopsMethod

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class ShopMethods:

    def __init__(self, main: Man10ShopV3):
        self.main = main
        self.blueprint = Blueprint('shop', __name__, url_prefix="/shop")
        ListShopsMethod(self)
        ShopInformationMethod(self)
        SetVariable(self)
        CreateShopMethod(self)
        GetAllShopIdsMethod(self)
        QueueAddTaskMethod(self)

        self.main.flask.register_blueprint(self.blueprint)
