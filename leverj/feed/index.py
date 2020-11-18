from queue import Queue
import json
import logging
import threading
import time
from decimal import *
from operator import neg
from typing import Optional

import socketio

sio = socketio.Client(logger=True, engineio_logger=True)

logger = logging.getLogger()


# Initializing a queue
btcusd_index_queue = Queue(maxsize=15)
ethusd_index_queue = Queue(maxsize=15)


def get_btcusd_index_queue():
    return btcusd_index_queue


def get_ethusd_index_queue():
    return ethusd_index_queue


@sio.event
def connect():
    logger.info("Connected!")


@sio.event
def connect_error():
    logger.info("Connection error!")


@sio.event
def disconnect():
    logger.info("Disconnected!")


@sio.on("index")
def on_index(data):
    logger.info(f'data: {data}')
    if data['topic'] == 'index_BTCUSD':
        btcusd_index_queue.put(data)
    elif data['topic'] == 'index_ETHUSD':
        ethusd_index_queue.put(data)
    else:
        pass


def connect_and_start():
    sio.connect('https://kovan.leverj.io', socketio_path='/futures/socket.io')
