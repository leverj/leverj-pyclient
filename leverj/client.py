import json
import logging
import time
from decimal import *

import requests
from leverj_ordersigner import futures, spot

from util import bytes_to_hexstring, round_with_precision, sign, to_vrs

ENDPOINTS = {
    'ALL_INFO': '/all/info',
    'ALL_CONFIG': '/all/config',
    'ORDER': '/order',
    'BALANCE': '/account/balance',
    'POSITION': '/account/position',
    'EXECUTION': '/account/execution?count=200',
    'ALL_TRADES': '/instrument/1/trade'
}

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)

MAX_INDEX_VARIANCE = 0.0085


class Client():

    def __init__(self, config_file):
        self.config = self._parse_config(config_file)
        self.api_url = None
        self.ENDPOINTS = ENDPOINTS

    def _parse_config(self, config_file):
        with open(config_file) as json_config_file:
            config_data = json.load(json_config_file)
            logging.debug(f'config_data: {config_data}')
            return config_data

    def set_api_url(self, api_url):
        self.api_url = api_url

    # Exchange and Instrument Endpoints

    def get_all_info(self):
        if self.api_url is None:
            logging.error('api_url is not set')
        response = requests.get(self.api_url+self.ENDPOINTS.get('ALL_INFO'))
        logging.debug(f'response: {response}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def get_all_config(self):
        if self.api_url is None:
            logging.error('api_url is not set')
        response = requests.get(self.api_url+self.ENDPOINTS.get('ALL_CONFIG'))
        logging.debug(f'response: {response}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def get_instrument_info(self, instrument_id):
        pass

    def create_spot_order(self, side, price, quantity, orderInstrument, orderAccountId, secret):
        price_precision = orderInstrument.get('quoteSignificantDigits')
        quantity_precision = orderInstrument.get('baseSignificantDigits')
        order = {
            'orderType': 'LMT',
            'side': side,
            'price': round(float(price), price_precision),
            'quantity': round(float(quantity), quantity_precision),
            'timestamp': int(time.time()*1000000),
            'accountId': orderAccountId,
            'token': orderInstrument['base']['address'],
            'instrument': orderInstrument['id']
        }
        order['signature'] = spot.sign_order(order, orderInstrument, secret)
        return order

    def post_spot_order(self, side, price, quantity, orderInstrument, orderAccountId, secret):
        order = self.create_spot_order(
            side, price, quantity, orderInstrument, orderAccountId, secret)
        data = json.dumps([order], separators=(',', ':'))
        nonce = int(time.time()*1000)
        signature = sign(str(nonce), secret)
        v, r, s = to_vrs(signature)

        auth_header = f"NONCE {orderAccountId}.{self.config.get('apiKey')}"\
            f".{v}"\
            f".{bytes_to_hexstring(r)}"\
            f".{bytes_to_hexstring(s)}"

        headers = {"Authorization": auth_header, "Nonce": str(
            nonce), "Content-Type": "application/json"}
        logging.debug(f'headers: {headers}, data: {data}')
        response = requests.post(
            self.api_url+self.ENDPOINTS.get('ORDER'), headers=headers, data=data)
        logging.debug(f'response: {response.content}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def get_orders(self, accountId, apiKey, secret):
        nonce = int(time.time()*1000)
        signature = sign(str(nonce), secret)
        v, r, s = to_vrs(signature)

        auth_header = f"NONCE {accountId}.{self.config.get('apiKey')}"\
            f".{v}"\
            f".{bytes_to_hexstring(r)}"\
            f".{bytes_to_hexstring(s)}"

        headers = {"Authorization": auth_header, "Nonce": str(
            nonce), "Content-Type": "application/json"}
        #logging.debug(f'headers: {headers}')
        response = requests.get(
            self.api_url+self.ENDPOINTS.get('ORDER'), headers=headers)
        logging.debug(f'get_balances, response: {response.content}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def get_order_details(self, orderId, accountId, apiKey, secret):
        nonce = int(time.time()*1000)
        signature = sign(str(nonce), secret)
        v, r, s = to_vrs(signature)

        auth_header = f"NONCE {accountId}.{self.config.get('apiKey')}"\
            f".{v}"\
            f".{bytes_to_hexstring(r)}"\
            f".{bytes_to_hexstring(s)}"

        headers = {"Authorization": auth_header, "Nonce": str(
            nonce), "Content-Type": "application/json"}
        #logging.debug(f'headers: {headers}')
        response = requests.get(
            self.api_url+self.ENDPOINTS.get('ORDER')+"/"+orderId, headers=headers)
        logging.debug(f'get_orders, response: {response.content}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def get_margin_per_fraction(self, orderInstrument, price, leverage):
        estimated_entry_price = price
        max_leverage = orderInstrument['maxLeverage']
        if leverage > max_leverage:
            self.logger.info(
                f'You have specified a leverage of {leverage} but the max leverage allowed on this instrument is {max_leverage}.')
        base_significant_digits = orderInstrument['baseSignificantDigits']
        decimals = orderInstrument['quote']['decimals']
        multiplier = Decimal(
            pow(Decimal(10), Decimal(decimals - base_significant_digits)))
        intermediate_value = Decimal((Decimal(
            estimated_entry_price) * multiplier) / Decimal(leverage)).to_integral_exact()
        return int(Decimal(intermediate_value) * Decimal(pow(Decimal(10), Decimal(base_significant_digits))))

    def create_futures_order(self, side, price, triggerPrice, quantity, orderInstrument, orderType, leverage, orderAccountId, originatorApiKey, secret, reduceOnly=False):
        price_precision = orderInstrument.get('quoteSignificantDigits')
        quantity_precision = orderInstrument.get('baseSignificantDigits')
        # default leverage is set to 1.0 which means you aren't using any leverage. If you want 5K DAI position to control 10K DAI worth of BTC, use leverage of 2
        order = {
            'accountId': orderAccountId,
            'originator': originatorApiKey,
            'instrument': orderInstrument['id'],
            'price': round_with_precision(price, price_precision),
            'quantity': round_with_precision(quantity, quantity_precision),
            'marginPerFraction': str(self.get_margin_per_fraction(orderInstrument, price, leverage)),
            'side': side,
            'orderType': orderType,
            'timestamp': int(time.time()*1000000),
            'quote': orderInstrument['quote']['address'],
            'isPostOnly': False,
            'reduceOnly': reduceOnly,
            'clientOrderId': 1,
            'triggerPrice': round_with_precision(triggerPrice, price_precision),
            'indexSanity': MAX_INDEX_VARIANCE
        }
        order['signature'] = futures.sign_order(
            order, orderInstrument, secret)
        return order

    def post_futures_order(self, side, price, triggerPrice, quantity, orderInstrument, orderAccountId, originatorApiKey, secret):
        order = self.create_futures_order(
            side, price, triggerPrice, quantity, orderInstrument, orderAccountId, originatorApiKey, secret)
        data = json.dumps([order], separators=(',', ':'))
        nonce = int(time.time()*1000)
        signature = sign(str(nonce), secret)
        v, r, s = to_vrs(signature)

        auth_header = f"NONCE {orderAccountId}.{self.config.get('apiKey')}"\
            f".{v}"\
            f".{bytes_to_hexstring(r)}"\
            f".{bytes_to_hexstring(s)}"

        headers = {"Authorization": auth_header, "Nonce": str(
            nonce), "Content-Type": "application/json"}
        logging.debug(f'headers: {headers}, data: {data}')
        response = requests.post(
            self.api_url+self.ENDPOINTS.get('ORDER'), headers=headers, data=data)
        logging.debug(f'response: {response.content}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def get_balances(self, accountId, apiKey, secret):
        nonce = int(time.time()*1000)
        signature = sign(str(nonce), secret)
        v, r, s = to_vrs(signature)

        auth_header = f"NONCE {accountId}.{self.config.get('apiKey')}"\
            f".{v}"\
            f".{bytes_to_hexstring(r)}"\
            f".{bytes_to_hexstring(s)}"

        headers = {"Authorization": auth_header, "Nonce": str(
            nonce), "Content-Type": "application/json"}
        #logging.debug(f'headers: {headers}')
        response = requests.get(
            self.api_url+self.ENDPOINTS.get('BALANCE'), headers=headers)
        logging.debug(f'get_balances, response: {response.content}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def get_positions(self, accountId, apiKey, secret):
        nonce = int(time.time()*1000)
        signature = sign(str(nonce), secret)
        v, r, s = to_vrs(signature)

        auth_header = f"NONCE {accountId}.{self.config.get('apiKey')}"\
            f".{v}"\
            f".{bytes_to_hexstring(r)}"\
            f".{bytes_to_hexstring(s)}"

        headers = {"Authorization": auth_header, "Nonce": str(
            nonce), "Content-Type": "application/json"}
        #logging.debug(f'headers: {headers}')
        response = requests.get(
            self.api_url+self.ENDPOINTS.get('POSITION'), headers=headers)
        logging.debug(f'get_positions, response: {response.content}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def get_trades(self, accountId, apikey, secret):
        nonce = int(time.time()*1000)
        signature = sign(str(nonce), secret)
        v, r, s = to_vrs(signature)

        auth_header = f"NONCE {accountId}.{self.config.get('apiKey')}"\
            f".{v}"\
            f".{bytes_to_hexstring(r)}"\
            f".{bytes_to_hexstring(s)}"

        headers = {"Authorization": auth_header, "Nonce": str(
            nonce), "Content-Type": "application/json"}
        #logging.debug(f'headers: {headers}')
        response = requests.get(
            self.api_url+self.ENDPOINTS.get('ALL_TRADES'), headers=headers)
        logging.debug(f'get_positions, response: {response.content}')
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
