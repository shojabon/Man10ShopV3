from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

from flask import Blueprint

from Man10ShopV3.methods.instance.sub_methods.Create import InstanceCreateMethod
from Man10ShopV3.methods.instance.sub_methods.List import InstanceListMethod
from Man10ShopV3.methods.instance.sub_methods.Stop import InstanceStopMethod

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class InstanceMethod:

    def __init__(self, main: Man10ShopV3):
        self.main = main
        self.blueprint = Blueprint('instance', __name__, url_prefix="/instance")
        InstanceCreateMethod(self)
        InstanceStopMethod(self)
        InstanceListMethod(self)

        self.main.flask.register_blueprint(self.blueprint)
