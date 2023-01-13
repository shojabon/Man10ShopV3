
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
        "endpoint": {
            "type": "string"
        },
        "inventory": {
            "type": "object"
        }
    },
    "required": ["name", "uuid"]
}