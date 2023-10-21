from __future__ import annotations

import datetime
import traceback
from typing import TYPE_CHECKING, Optional, Dict, Any

import humps
from pydantic import BaseModel

from Man10ShopV3.common_variables.common_variables import player_schema, PlayerBaseModel
from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.shop import ShopMethods

class QueueAddTaskRequest(BaseModel):
    player: Optional[PlayerBaseModel]
    key: str
    shopId: str
    data: Dict[str, Any]

class QueueAddTaskMethod:
    def __init__(self, methods: ShopMethods):
        self.methods = methods

        @self.methods.main.app.post("/shop/queue/add")
        async def queue_add(request: QueueAddTaskRequest):
            try:
                if request.player is not None:
                    request.player = humps.decamelize(request.player.dict())
                request.data = humps.decamelize(request.data)
                request_data = request.dict()
                request_data["registered_time"] = datetime.datetime.now()
                # self.methods.main.mongo["man10shop_v3"]["queue"].insert_one(humps.camelize(request_data))
                self.methods.main.main_queue.put(humps.camelize(request_data))
                return self.methods.response_object("success")
            except Exception as e:
                traceback.print_exc()
                return self.methods.response_object("error_internal", {"message": str(e)})