from __future__ import annotations
import json

import requests

from Man10ShopV3.data_class.Player import Player

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Man10ShopV3 import Man10ShopV3


class OrderRequest(object):
    amount = 1
    player: Player = None

    # def __init__(self, main: Man10ShopV3):
    #     self.main = main

