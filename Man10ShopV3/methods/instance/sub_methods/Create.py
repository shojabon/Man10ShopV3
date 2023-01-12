from __future__ import annotations

import json
from typing import TYPE_CHECKING

import docker
import requests

from utils.JsonSchemaWrapper import flask_json_schema, merge_dictionaries
from utils.MatResponseWrapper import flask_mat_response_wrapper

if TYPE_CHECKING:
    from Man10ShopV3.methods.instance import InstanceMethod


class InstanceCreateMethod:

    def __init__(self, instance_method: InstanceMethod):
        self.instance_method = instance_method
        self.schema = {
            "type": "object",
            "properties": {
                "properties": {
                    "type": "object"
                },
                "template": {
                    "type": "string"
                },
                "assignPort": {
                    "type": "array"
                },
                "registerOnBungeeCord": {
                    "type": "object",
                    "properties": {
                        "host": {
                            "type": "string",
                            "format": "ip-address"
                        },
                        "name": {
                            "type": "string"
                        }
                    },
                    "required": ["host"]
                }
            },
            "anyOf": [
                {
                    "required": ["properties"]
                },
                {
                    "required": ["template"]
                }
            ]

        }

        self.register_endpoint()

    def register_endpoint(self):
        @self.instance_method.blueprint.route("", methods=["POST"])
        @flask_mat_response_wrapper()
        @flask_json_schema(self.schema)
        def instance_create(json_body):
            try:
                client = docker.from_env()
                properties = {}
                ports_property = {}

                if "template" in json_body:  # load template as base
                    template_name = json_body["template"]
                    if template_name not in self.instance_method.main.templates:
                        return "template_invalid"
                    properties = merge_dictionaries(properties,
                                                    self.instance_method.main.templates[template_name].copy())

                if "properties" in json_body:  # merged current properties with inline properties
                    properties = merge_dictionaries(properties, json_body["properties"])

                if "assign_ports" in json_body:  # assign available port
                    # find ports currently used by docker
                    ports = [x.attrs["NetworkSettings"]["Ports"] for x in client.containers.list(all=True)]
                    tcp = []
                    udp = []
                    for port_object in ports:
                        for key in port_object.keys():
                            if str(key).count("/tcp") != 0:
                                tcp.append(int(port_object[key][0]["HostPort"]))
                                continue
                            if str(key).count("/udp") != 0:
                                udp.append(int(port_object[key][0]["HostPort"]))
                                continue

                    currently_available_tcp = [x for x in self.instance_method.main.tcp_ports.copy() if x not in tcp]
                    currently_available_udp = [x for x in self.instance_method.main.udp_ports.copy() if x not in udp]

                    for port in json_body["assign_ports"]:
                        port = str(port)
                        if port.count("/tcp") != 0:
                            if len(currently_available_tcp) == 0:
                                return "port_exhaust"
                            ports_property[port] = currently_available_tcp.pop(0)
                            continue
                        if port.count("/udp") != 0:
                            if len(currently_available_udp) == 0:
                                return "port_exhaust"
                            ports_property[port] = currently_available_udp.pop(0)
                            continue

                    properties["ports"] = ports_property

                container = client.containers.run(**properties)

                if "register_on_bungee_cord" in json_body: # register server on bungee
                    name = "im-" + container.short_id
                    if "name" in json_body["register_on_bungee_cord"]:
                        name = json_body["register_on_bungee_cord"]["name"]

                    bungee_register_request = requests.post(self.instance_method.main.bungee_cord_api_endpoint, json={
                        "name": name,
                        "host": json_body["register_on_bungee_cord"]["host"],
                        "port": ports_property.get("25565/tcp")
                    }, headers={"x-api-key": self.instance_method.main.bungee_cord_api_key})

                    if bungee_register_request.status_code != 200:
                        container.stop()
                        container.remove()
                        return "bungee_register_failed"

                return "success", {
                    "id": container.id,
                    "short_id": container.short_id,
                    "status": container.status,
                    "name": container.name,
                    "port": container.attrs["HostConfig"]["PortBindings"]
                }
            except Exception as e:
                return "error_internal", {"message": str(e)}
