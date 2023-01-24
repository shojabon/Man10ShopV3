import json
import queue
import time
import traceback
import uuid
from threading import Thread

import humps
from flask import Flask
from pymongo import MongoClient

from Man10ShopV3.data_class.OrderRequest import OrderRequest
from Man10ShopV3.data_class.Player import Player
from Man10ShopV3.manager.Man10ShopV3API import Man10ShopV3API
from Man10ShopV3.methods.shop import ShopMethods


class Man10ShopV3:

    def sub_queue_process(self, queue_id: int):
        queue_object = self.sub_queue[queue_id]
        while self.running:
            try:
                while not queue_object.empty():
                    request = queue_object.get()
                    if request == "END":
                        return
                    # completed_task.append(request["_id"])
                    shop = self.api.get_shop(request["shop_id"])
                    if shop is None:
                        continue

                    shop.execute_queue_callback(request["key"], request)

                time.sleep(0.1)

            except Exception:
                traceback.print_exc()
                continue

    def main_queue_process(self):
        while self.running:
            try:
                while not self.main_queue.empty():
                    request = self.main_queue.get()
                    if request == "END":
                        return
                    request: dict = humps.decamelize(request)
                    if "player" in request:
                        player_data = request["player"]
                        request["player"] = Player().load_from_json(player_data, self)

                    queue_id = uuid.UUID(request["shop_id"]).int%self.config["queue"]["size"]
                    self.sub_queue[queue_id].put(request)

                time.sleep(0.1)

            except Exception:
                traceback.print_exc()
                continue

    def process_per_minute_execution_task(self):
        timer = 0
        while self.running:
            time.sleep(1)
            timer += 1
            if timer % 60 != 0:
                continue
            try:
                for shop in self.api.shops.values():
                    shop.execute_per_minute_execution_task()
            except Exception:
                traceback.print_exc()

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
        self.api.load_all_shops()

        self.shop_method = ShopMethods(self)

        self.main_queue = queue.Queue(maxsize=0)
        self.sub_queue = {}
        Thread(target=self.main_queue_process).start()
        for x in range(self.config["queue"]["size"]):
            self.sub_queue[x] = queue.Queue(maxsize=0)
            Thread(target=self.sub_queue_process, args=(x,)).start()

        Thread(target=self.process_per_minute_execution_task).start()

        self.flask.run("0.0.0.0", self.config["hostPort"], threaded=True)
        self.running = False
        self.main_queue.put("CLOSE")
        for x in range(self.config["queue"]["size"]):
            self.sub_queue[x].put("CLOSE")

