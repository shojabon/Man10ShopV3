import hashlib

from utils.MatResponseWrapper import get_error_message


class Sign(object):
    server = None
    word = None
    x = None
    y = None
    z = None

    def from_json(self, data: dict):
        self.server = data.get("server")
        self.word = data.get("world")
        self.x = data.get("x")
        self.y = data.get("y")
        self.z = data.get("z")
        return self

    def get_json(self):
        return {
            "id": self.location_id(),
            "server": self.server,
            "world": self.word,
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

    def location_id(self):
        md5 = hashlib.md5()
        location_id = str(self.server) + "|" + str(self.word) + "|" + str(self.x) + "|" + str(self.y) + "|" + str(self.z)
        md5.update(location_id.encode("utf-8"))
        return md5.hexdigest()