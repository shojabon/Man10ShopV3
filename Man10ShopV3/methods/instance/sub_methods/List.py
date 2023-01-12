from __future__ import annotations

from typing import TYPE_CHECKING

import docker

from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.instance import InstanceMethod


class InstanceListMethod:

    def __init__(self, instance_method: InstanceMethod):
        self.instance_method = instance_method
        self.schema = {
            # "type": "object",
            # "delete": {
            #     "properties": {
            #         "type": "boolean"
            #     },
            # },
            # "containerId": {
            #     "properties": {
            #         "type": "string"
            #     }
            # },
            # "required": ["containerId"]

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.instance_method.blueprint.route("", methods=["GET"])
        @flask_mat_response_wrapper()
        def instance_list():
            try:
                client = docker.from_env()

                result = []

                for container in client.containers.list(all=True):

                    result.append({
                        "id": container.id,
                        "short_id": container.short_id,
                        "status": container.status,
                        "name": container.name,
                        "port": container.attrs["HostConfig"]["PortBindings"]
                    })

                return "success", result
            except Exception as e:
                return "error_internal", {"message": str(e)}
