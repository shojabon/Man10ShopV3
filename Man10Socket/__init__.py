import time
import typing
from threading import Thread

from Man10Socket.utils.connection_handler.Connection import Connection
from Man10Socket.utils.connection_handler.ConnectionHandler import ConnectionHandler
from Man10Socket.utils.socket_functions.ReplyFunction import ReplyFunction
from Man10Socket.utils.socket_functions.RequestFunction import RequestFunction


class Man10Socket:

    def __init__(self, session_name: str, host: str, port: int):
        self.session_name = None
        self.host = host
        self.port = port

        self.connection_handler: ConnectionHandler = ConnectionHandler()

        self.custom_request = RequestFunction()

        def register_functions(connection: Connection):
            connection.register_socket_function(self.custom_request)
            connection.register_socket_function(ReplyFunction())

        self.connection_handler.register_function_on_connect = register_functions

        self.connection_handler.socket_open_server("Man10Socket", host, port)
        def check_open_socket_count_thread():
            while True:
                open_sockets = [x for x in self.connection_handler.sockets.values() if x.name == "Man10Socket"]
                if len(open_sockets) < 1:
                    print("Opening socket")
                    # open sockets until there are enough
                    open_socket = self.connection_handler.socket_open_server("Man10Socket", host, port)
                    if open_socket is None:
                        print("Failed to open socket")
                        continue
                    self.set_session_name(session_name)
                time.sleep(1)

        self.check_open_socket_count_thread = Thread(target=check_open_socket_count_thread)
        self.check_open_socket_count_thread.daemon = True
        self.check_open_socket_count_thread.start()

        self.set_session_name(session_name)

    def send_message(self, message: dict, reply: bool = False, callback: typing.Callable = None, reply_timeout: int = 1,
                     reply_arguments: typing.Tuple = None):
        return self.connection_handler.get_socket("Man10Socket").send_message(message, reply, callback, reply_timeout, reply_arguments)

    def set_session_name(self, session_name: str):
        self.session_name = session_name
        self.send_message({"type": "set_name", "name": session_name})

    def register_route(self, path: str, callback: typing.Callable[[dict], typing.Tuple]):
        self.custom_request.register_route(path, callback)