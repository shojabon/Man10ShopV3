from __future__ import annotations

import glob
import json
import os
from typing import TYPE_CHECKING

import humps
from fastapi.exceptions import RequestValidationError
from flask import Blueprint, Request
from starlette import status
from starlette.responses import JSONResponse

from Man10ShopV3.methods.shop.public_methods.PublicListShopsMethod import PublicListShopsMethod
from Man10ShopV3.methods.shop.sub_methods.CreateShopMethod import CreateShopMethod
from Man10ShopV3.methods.shop.sub_methods.GetAllShopIdsMethod import GetAllShopIdsMethod
from Man10ShopV3.methods.shop.sub_methods.QueueAddTaskMethod import QueueAddTaskMethod
from Man10ShopV3.methods.shop.sub_methods.SetVariable import SetVariable
from Man10ShopV3.methods.shop.sub_methods.ShopInformationMethod import ShopInformationMethod
from Man10ShopV3.methods.shop.sub_methods.ListShopsMethod import ListShopsMethod
from Man10ShopV3.methods.shop.sub_methods.WithdrawBuyShopMoneyMethod import WithdrawBuyShopMoneyMethod

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class ShopMethods:

    def __init__(self, main: Man10ShopV3):

        self.error_codes = {}
        for path in glob.glob("error_codes/*.json"):
            code_name = os.path.basename(path)[:-5]
            file = open(path, "r", encoding="utf-8")
            self.error_codes[code_name] = json.loads(file.read())
            file.close()

        self.main = main
        self.blueprint = Blueprint('shop', __name__, url_prefix="/shop")


        @self.main.app.exception_handler(RequestValidationError)
        async def handler(request: Request, exc: RequestValidationError):
            print(exc)
            return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        ListShopsMethod(self)
        ShopInformationMethod(self)
        SetVariable(self)
        CreateShopMethod(self)
        GetAllShopIdsMethod(self)
        QueueAddTaskMethod(self)
        WithdrawBuyShopMoneyMethod(self)
        PublicListShopsMethod(self)

        self.main.flask.register_blueprint(self.blueprint)

    def convert_response_to_json_response(self, response: str, data = None, language: str = "en"):
        if data is None:
            data = []
        response = (response, data)

        result = {}
        status_name = response[0]
        data = response[1]
        result["data"] = data
        result["status"] = status_name

        if status_name in self.error_codes:
            status_data = self.error_codes[status_name]
        else:
            status_data = self.error_codes["unknown_response"]

        status_code = 206
        if "code" in status_data:
            status_code = status_data["code"]
        if "message" in status_data:
            if language in status_data["message"]:
                result["message"] = status_data["message"][language]
            else:
                result["message"] = status_data["message"]["en"]

        result = humps.camelize(result)
        return result, status_code

    def response_object(self, response_id: str, data = None) -> JSONResponse:
        user_defined_language = "jp"

        result = self.convert_response_to_json_response(response_id, data, user_defined_language)
        return JSONResponse(content=result[0], status_code=result[1])
