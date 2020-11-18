import json
import logging
from web3.auto import w3
import json
import time

from leverj.client import Client
from leverj.feed.futures.index import LeverjFuturesIndexClient


def get_index_data():
    leverj_futures_index_client = LeverjFuturesIndexClient()
    while True:
        time.sleep(1)
        btcusd_index_value = leverj_futures_index_client.get_price("BTCUSD")
        logging.info(f'btcusd_index_value: {btcusd_index_value}')
        ethusd_index_value = leverj_futures_index_client.get_price("ethUSD")
        logging.info(f'ethusd_index_value: {ethusd_index_value}')


def get_position(positions, coin: str):
    assert(isinstance(coin, str))
    #positions = self.get_positions()
    for index, position in enumerate(positions):
        if position['instrument'] == _get_instrument_id_by_asset_name(coin.upper()):
            return position['size']


def _get_instrument_id_by_asset_name(name: str):
    asset_name_to_instrument_id_map = {'BTC': '1', 'ETH': '2'}
    return asset_name_to_instrument_id_map[name]


if __name__ == "__main__":
    # connect to a testnet: kovan.leverj.io or ropsten.leverj.io to test the features
    # please register and download the api key from your wallet
    # create two directories resources/config/kovan.leverj.io and resources/config/ropsten.leverj.io
    # within this project folder for the testnet environments
    # copy the downloaded api keys to these corresponding testnet folders

    # connect to kovan
    #client = Client('./resources/config/kovan.leverj.io/<api-key>.json')
    # client.set_api_url('https://kovan.leverj.io/futures/api/v1')

    # connect to ropsten
    #client = Client('./resources/config/ropsten.leverj.io/<api_key>.json')
    # client.set_api_url('https://ropsten.leverj.io/futures/api/v1')

    # get all info
    #all_info = client.get_all_info()
    #logging.debug(f'all info: {all_info}')

    # get all config
    #all_config = client.get_all_config()
    #logging.debug(f'all info: {all_config}')

    # create a spot order (IMPORTANT: Remember to initialize the client with the spot url)
    #instruments = all_config.get('instruments')
    #L2_instrument = instruments.get('L2TH')
    #client.create_spot_order('buy', 0.0001229, 1, L2_instrument, (client.config).get('accountId'), (client.config).get('secret'))
    #client.post_spot_order('buy', 0.0001229, 1, L2_instrument, (client.config).get('accountId'), (client.config).get('secret'))

    # create a futures order
    #instruments = all_config.get('instruments')
    #BTCDAI_instrument = instruments.get('1')
    #logging.debug(f'BTCDAI_instrument: {BTCDAI_instrument}')
    #futures_order = client.create_futures_order('buy', 17855, 17855, 0.1309, BTCDAI_instrument, (client.config).get('accountId'), (client.config).get('apiKey'), (client.config).get('secret'))
    #logging.debug(f'futures_order: {futures_order}')
    #client.post_futures_order('buy', 17850, 17850, 0.0021, BTCDAI_instrument, (client.config).get('accountId'), (client.config).get('apiKey'), (client.config).get('secret'))

    # get index data via websockets
    # get_index_data()

    # get balances
    #balances = client.get_balances((client.config).get('accountId'), (client.config).get('apiKey'), (client.config).get('secret'))
    #logging.debug(f'balances: {balances}')

    # get positions
    #positions = client.get_positions((client.config).get('accountId'), (client.config).get('apiKey'), (client.config).get('secret'))
    #position_btc = get_position(positions, "btc")
    #logging.debug(f'position_btc: {position_btc}')

    # get trades
    #trades = client.get_trades((client.config).get('accountId'), (client.config).get('apiKey'), (client.config).get('secret'))
    #logging.debug(f'trades: {trades}')
