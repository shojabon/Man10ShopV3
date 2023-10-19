from typing import Optional

from pydantic import BaseModel, Field

player_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "uuid": {
            "type": "string",
            "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            "maxLength": 36,
            "minLength": 36
        },
        "balance": {
            "type": "integer"
        },
        "server": {
            "type": "string"
        },
        "inventory": {
            "type": "object"
        }
    },
    "required": ["name", "uuid"]
}

location_schema = {
    "type": "object",
    "properties": {
        "server": {
            "type": "string"
        },
        "world": {
            "type": "string"
        },
        "x": {
            "type": "integer"
        },
        "y": {
            "type": "integer"
        },
        "z": {
            "type": "integer"
        },
    },
    "required": ["server", "world", "x", "y", "z"]
}


class PlayerBaseModel(BaseModel):
    name: str
    uuid: str
    balance: Optional[int] = None
    server: Optional[str] = None
    inventory: Optional[dict] = None
    ipAddress: Optional[str] = None


class LocationBaseModel(BaseModel):
    server: str
    world: str
    x: int
    y: int
    z: int
