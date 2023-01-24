from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class GetAllShopIdsMethod:

    def __init__(self, methods: ShopMethods):
        self.methods = methods

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("/allIds", methods=["POST"])
        @flask_json_schema({})
        @flask_mat_response_wrapper()
        def get_shop_ids():
            try:
                results = self.methods.main.mongo["man10shop_v3"]["shops"].find({}, {"_id": 0, "shopId": 1})
                results = [x["shopId"] for x in results]
                return "success", results
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}

