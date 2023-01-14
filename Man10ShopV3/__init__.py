import json
import time
import traceback
from threading import Thread

from flask import Flask
from pymongo import MongoClient

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.manager.Man10ShopV3API import Man10ShopV3API
from Man10ShopV3.methods.shop import ShopMethods


class Man10ShopV3:

    def process_queue(self):
        while self.running:
            try:
                completed_task = []
                result = self.mongo["man10shop_v3"]["queue"].find({}).limit(1)
                result = [x for x in result]
                for request in result:
                    if "player" in request:
                        player_data = request["player"]
                        request["player"] = Player().load_from_json(player_data, self)
                    completed_task.append(request["_id"])
                    shop = self.api.get_shop(request["shopId"])
                    if shop is None:
                        continue

                    shop.execute_queue_callback(request["key"], request)

                self.mongo["man10shop_v3"]["queue"].delete_many({"_id": {"$in": completed_task}})
                time.sleep(0.1)

            except Exception:
                traceback.print_exc()
                continue

    def __init__(self):
        # variables
        self.flask = Flask(__name__)
        self.running = True
        self.flask.url_map.strict_slashes = False
        self.config = {}
        # load config

        config_file = open("config.json", encoding="utf-8")
        self.config = json.loads(config_file.read())
        config_file.close()

        self.mongo = MongoClient(self.config["mongodbConnectionString"])

        # print([x for x in self.mongo["man10shop_v3"]["shops"].find({})])

        # load api

        self.api = Man10ShopV3API(self)

        self.shop_method = ShopMethods(self)

        Thread(target=self.process_queue).start()

        # self.shop = InstanceMethod(self)
        player = Player()
        player.name = "Sho0"
        player.uuid = "ffa9b4cb-ada1-4597-ad24-10e318f994c8"
        player.main = self

        # print(self.api.get_player_shops(player)[1].category_function.set_category("aaa"))
        # self.api.create_shop(player, "1", 1000, "BUY", False)
        # self.api.create_shop(player, "2", 1000, "BUY", False)
        # self.api.create_shop(player, "3", 1000, "BUY", False)
        # shop = self.api.get_shop("c83bab75-9216-11ed-a3b6-803253476232")
        # shop.money_function.set("account", 1000)
        # print(shop.money_function.get("account"))
        #
        # order = OrderRequest(self)
        # order.player = Player()
        # order.player.uuid = "ffa9b4cb-ada1-4597-ad24-10e318f994c8"
        # order.player.name = "Sho0"
        # order.player.balance = 100
        # order.player.main = self
        # order.player.endpoint = "man10"

        # print(order.player.send_message("hello"))

        self.flask.run("0.0.0.0", self.config["hostPort"], threaded=True)
        self.running = False