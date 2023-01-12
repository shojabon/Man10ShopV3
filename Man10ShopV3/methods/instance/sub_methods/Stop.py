from __future__ import annotations

from typing import TYPE_CHECKING

import docker
import requests

from utils.JsonSchemaWrapper import flask_json_schema
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.instance import InstanceMethod


class InstanceStopMethod:

    def __init__(self, instance_method: InstanceMethod):
        self.instance_method = instance_method
        self.schema = {
            "type": "object",
            "delete": {
                "properties": {
                    "type": "boolean"
                },
            },
            "containerId": {
                "properties": {
                    "type": "string"
                }
            },
            "deleteOnBungeeCord": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    }
                }
            }

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.instance_method.blueprint.route("", methods=["DELETE"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def instance_stop(json_body):
            try:
                client = docker.from_env()
                container = client.containers.get(json_body["container_id"])

                container_id = container.short_id

                container.stop()

                if "delete" in json_body and json_body["delete"]:
                    container.remove()

                if "delete_on_bungee_cord" in json_body:
                    name = "im-" + container_id
                    if "name" in json_body["delete_on_bungee_cord"]:
                        name = json_body["delete_on_bungee_cord"]["name"]

                    requests.delete(self.instance_method.main.bungee_cord_api_endpoint, json={
                        "name": name
                    }, headers={"x-api-key": self.instance_method.main.bungee_cord_api_key})

                return "success"
            except Exception as e:
                print(e)
                return "error_internal", {"message": str(e)}
