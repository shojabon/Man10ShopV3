from __future__ import annotations

import datetime
import traceback
from typing import TYPE_CHECKING, Optional

import humps

from Man10ShopV3.common_variables.common_variables import player_schema
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods


class QueueAddTaskMethod:

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
                },
                "data":{
                    "type": "object"
                }
            },
            "required": ["shopId", "key", "data"]

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.methods.blueprint.route("/queue/add", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def queue_add(json_body: dict):
            try:
                json_body["registered_time"] = datetime.datetime.now()
                # self.methods.main.mongo["man10shop_v3"]["queue"].insert_one(humps.camelize(json_body))
                self.methods.main.main_queue.put(humps.camelize(json_body))
                return "success"
            except Exception as e:
                traceback.print_exc()
                return "error_internal", {"message": str(e)}
