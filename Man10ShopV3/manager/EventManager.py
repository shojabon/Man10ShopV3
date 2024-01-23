from __future__ import annotations

import datetime
import json
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from copy import copy, deepcopy
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Optional

import humps
import requests
from tqdm import tqdm

from Man10ShopV3.data_class.Sign import Sign
from Man10Socket.data_class.Player import Player
from Man10Socket.utils.connection_handler.Connection import Connection
from menu.action_menu.BuyAndSellActionMenu import BuyAndSellActionMenu

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class EventManager:

    def __init__(self, main: Man10ShopV3):
        self.main = main
        self.socket = self.main.man10_socket

        # @self.socket.event_handler.listener("player_interact_sign", subscribe_to_server=True)
        # def on_player_interact_sign(connection: Connection, message: dict, data: dict, player: dict):
        #     player = self.socket.get_player(player["uuid"])
        #     player.set_data(player)
        #     sign = Sign().from_json({
        #         "x": data["location"]["x"],
        #         "y": data["location"]["y"],
        #         "z": data["location"]["z"],
        #         "world": data["location"]["world"],
        #         "server": message["server"]
        #     })
        #     shop = self.main.api.get_shop_id_from_location(sign)
        #     if shop is None:
        #         return
        #     shop = self.main.api.get_shop(shop)
        #     if shop is None:
        #         return
        #     self.socket.gui_handler.open_gui(player, shop.get_action_menu())
