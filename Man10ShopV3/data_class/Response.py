from utils.MatResponseWrapper import get_error_message


class RequestResponse(object):

    def __init__(self, status_code: str):
        self.status_code = status_code

    def success(self):
        return self.status_code == "success"

    def message(self):
        return get_error_message(self.status_code)