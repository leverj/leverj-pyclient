import logging
from collections import deque

import socketio

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)


class WebsocketClient:

    logger = logging.getLogger()

    def __init__(self):
        self.sio = socketio.Client(logger=False, engineio_logger=False)
        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        #self.sio.on("index", self.on_index)
        self.sio.on("order_add", self.on_order_add)
        self.sio.on("order_del", self.on_order_del)
        self.sio.on("order_error", self.on_order_error)
        self.sio.on("margin_error", self.on_margin_error)
        self.sio.on("order_del_all", self.on_order_del_all)
        self.sio.on("order_update", self.on_order_update)
        self.sio.on("order_patch", self.on_order_patch)
        #self.sio.on("orderbook", self.on_orderbook)
        self.sio.on("server_time", self.on_server_time)
        self.sio.on("auth_error", self.on_auth_error)
        self.sio.on("order_closed", self.on_order_closed)
        self.sio.on("order_cancelled", self.on_order_cancelled)
        self.sio.on("order_execution", self.on_order_execution)
        self.start()

    def connect(self):
        self.logger.info("Connected!")

    def connect_error(self):
        self.logger.info("Connection error!")

    def disconnect(self):
        self.logger.info("Disconnected!")

    def on_index(self, data):
        print(f'on_index data: {data}')

    def on_orderbook(self, data):
        print(f'on_orderbook data: {data}')

    def on_order_add(self, data):
        print(f'on_order_add: {data}')

    def on_order_del(self, data):
        print(f'on_order_del: {data}')

    def on_order_error(self, data):
        print(f'on_order_error: {data}')

    def on_margin_error(self, data):
        print(f'margin_error: {data}')

    def on_order_del_all(self, data):
        print(f'order_del_all: {data}')

    def on_order_update(self, data):
        print(f'order_update: {data}')

    def on_order_patch(self, data):
        print(f'order_patch: {data}')

    def on_server_time(self, data):
        print(f'on_server_time: {data}')

    def on_auth_error(self, data):
        print(f'on_auth_error: {data}')

    def on_order_closed(self, data):
        print(f'on_order_closed: {data}')

    def on_order_cancelled(self, data):
        print(f'order_cancelled: {data}')

    def on_order_execution(self, data):
        print(f'on_order_execution: {data}')

    def start(self):
        self.logger.debug(f'starting websocket client')
        self.sio.connect('https://kovan.leverj.io',
                         socketio_path='/futures/socket.io')

    def stop(self):
        self.sio.disconnect()
