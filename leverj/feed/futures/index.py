import logging
from collections import deque

import socketio

#logging.getLogger('socketio').setLevel(logging.ERROR)
#logging.getLogger('engineio').setLevel(logging.ERROR)


class LeverjFuturesIndexClient:

    logger = logging.getLogger()

    def __init__(self):
        self.sio = socketio.Client(logger=False, engineio_logger=False)
        # Initializing a queue
        self.btcusd_index_queue = deque(maxlen=15)
        self.ethusd_index_queue = deque(maxlen=15)
        self._latest_btcusd_value = None
        self._latest_ethusd_value = None
        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)
        self.sio.on("index", self.on_index)
        self.start()

    def connect(self):
        self.logger.info("Connected!")

    def connect_error(self):
        self.logger.info("Connection error!")

    def disconnect(self):
        self.logger.info("Disconnected!")

    def on_index(self, data):
        #self.logger.info(f'data: {data}')
        topic = data['topic']
        if 'price' in data:
            if topic == 'index_BTCUSD':
                self.btcusd_index_queue.append(data)
                self._latest_btcusd_value = data
            elif topic == 'index_ETHUSD':
                self.ethusd_index_queue.append(data)
                self._latest_ethusd_value = data
            else:
                self.logger.info(f'unrecognized index: {topic}')
        else:
            self.logger.info(f'no price data in this event: {data}')

    def start(self):
        self.sio.connect('https://ropsten.leverj.io',
                         socketio_path='/futures/socket.io')

    def stop(self):
        self.sio.disconnect()

    def get_btcusd_index_queue(self):
        return self.btcusd_index_queue

    def get_ethusd_index_queue(self):
        return self.ethusd_index_queue

    def get_value(self, index_name):
        if index_name.upper() == "BTCUSD":
            return self._get_latest_btcusd_index_value()
        elif index_name.upper() == "ETHUSD":
            return self._get_latest_ethusd_index_value()
        else:
            self.logger.info(f'no value available for: {index_name}')

    def get_price(self, index_name):
        latest_value = self.get_value(index_name)
        return latest_value

    def _get_latest_btcusd_index_value(self):
        if self.btcusd_index_queue:
            return self.btcusd_index_queue.pop()
        else:
            return self._latest_btcusd_value

    def _get_latest_ethusd_index_value(self):
        if self.ethusd_index_queue:
            return self.ethusd_index_queue.pop()
        else:
            return self._latest_ethusd_value

    def _clear_index_queue(self):
        self.btcusd_index_queue.clear()
        self.ethusd_index_queue.clear()
