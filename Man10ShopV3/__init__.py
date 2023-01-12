import json

from flask import Flask
from pymongo import MongoClient

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.manager.Man10ShopV3API import Man10ShopV3API
from Man10ShopV3.methods.instance import InstanceMethod


class Man10ShopV3:

    def __init__(self):
        # variables
        self.flask = Flask(__name__)
        self.flask.url_map.strict_slashes = False
        self.config = {}
        # load config

        config_file = open("config.json", encoding="utf-8")
        self.config = json.loads(config_file.read())
        config_file.close()

        self.mongo = MongoClient(self.config["mongodbConnectionString"])

        # load api

        self.api = Man10ShopV3API(self)

        # self.instance = InstanceMethod(self)

        # self.api.create_shop("a", "ショップ", 1000, "BUY", False)
        # shop = self.api.get_shop("c83bab75-9216-11ed-a3b6-803253476232")
        # shop.money_function.set("account", 1000)
        # print(shop.money_function.get("account"))

        order = OrderRequest(self)
        order.player = Player()
        order.player.uuid = "ffa9b4cb-ada1-4597-ad24-10e318f994c8"
        order.player.name = "Sho0"
        order.player.balance = 100
        order.player.main = self
        order.player.endpoint = "man10"

        print(order.player.take_money(10000))

        # self.flask.run("0.0.0.0", self.config["hostPort"])