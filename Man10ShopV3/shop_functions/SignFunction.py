from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.data_class.ShopFunction import ShopFunction
from Man10ShopV3.data_class.Sign import Sign


class SignFunction(ShopFunction):
    allowed_shop_type = []

    def on_function_init(self):
        self.set_variable("signs", {})

        self.shop.register_queue_callback("sign.register", self.register_sign)
        self.shop.register_queue_callback("sign.unregister", self.un_register_sign)

    def get_signs(self):
        return self.get("signs")

    def add_sign(self, sign: Sign):
        signs = self.get_signs()
        signs[sign.location_id()] = sign.get_json()
        return self.set("signs", signs)

    def remove_sign(self, sign: Sign):
        signs = self.get_signs()
        if sign.location_id() not in signs:
            return
        del signs[sign.location_id()]
        return self.set("signs", signs)

    # queue tasks

    def register_sign(self, data: dict):
        for key in data["data"].keys():
            if key not in ["server", "world", "x", "y", "z"]:
                return

        sign = Sign().from_json(data["data"])
        self.add_sign(sign)
        if "player" in data:
            player: Player = data["player"]
            player.success_message("看板を作成しました")

    def un_register_sign(self, data: dict):
        for key in data["data"].keys():
            if key not in ["server", "world", "x", "y", "z"]:
                return

        sign = Sign().from_json(data["data"])
        self.remove_sign(sign)
