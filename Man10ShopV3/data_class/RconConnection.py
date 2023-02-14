import datetime
import hashlib
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from mcrcon import MCRcon


class RconConnection(object):

    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

        self.connections: dict[int, MCRcon] = {}
        self.last_tried_to_connect: dict[int, int] = {}
        self.retry_connection_in = 3
        self.thread_pool = ThreadPoolExecutor(max_workers=30)

    def open_connection(self, queue_id: int):
        if queue_id in self.connections:
            return True
        if queue_id in self.last_tried_to_connect and datetime.datetime.now().timestamp() - self.last_tried_to_connect[
            queue_id] < 3:
            return False
        try:
            self.connections[queue_id] = MCRcon(self.host, self.password, self.port)
            self.connections[queue_id].connect()
            return True
        except Exception:
            self.last_tried_to_connect[queue_id] = int(datetime.datetime.now().timestamp())
            traceback.print_exc()
            return False

    def close_connection(self, queue_id: int):
        if queue_id not in self.connections:
            return
        try:
            self.connections[queue_id].disconnect()
            del self.connections[queue_id]
        except Exception:
            traceback.print_exc()
            return

    def execute_command(self, command: str, queue_id: int):
        if queue_id not in self.connections:
            if not self.open_connection(queue_id):
                return None

        try:
            rcon: MCRcon = self.connections[queue_id]
            return rcon.command(command)[:-1]
        except Exception:
            traceback.print_exc()
            self.close_connection(queue_id)
            return None

    def execute_command_async(self, command: str, queue_id: int):
        def task():
            self.execute_command(command, -queue_id)
        self.thread_pool.submit(task)

    @staticmethod
    def get_queue_id_from_text(material: str, max_queue_size: int):
        md5 = hashlib.md5()
        md5.update(material.encode("utf-8"))
        md5 = md5.hexdigest()
        return int.from_bytes(str(md5).encode("utf-8"), "big") % max_queue_size


if __name__ == '__main__':
    test = RconConnection("127.0.0.1", 25575, "testpassword")
    # for x in range(100):
    result = test.execute_command("mshop moneyGet d17c062a-be66-3ad7-ade9-601833350b57", 0)
    print(result)
