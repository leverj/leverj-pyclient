import json
import logging
import uuid

from leverj.client import Client
from leverj.websocket.client import WebsocketClient
from leverj.websocket.util import credentials, protected_endpoint_request


def create_order(originator_credentials):
    client = Client('./resources/config/kovan.leverj.io/c21b18-64bdd3.json')
    client.set_api_url('https://kovan.leverj.io/futures/api/v1')
    all_config = client.get_all_config()
    logging.debug(f'all info: {all_config}')
    instruments = all_config.get('instruments')
    BTCDAI_instrument = instruments.get('1')
    print(f'BTCDAI_instrument: {BTCDAI_instrument}')
    futures_order = client.create_futures_order('buy', 53863, 53863, 0.02, BTCDAI_instrument, 'LMT', 2.0, originator_credentials.get(
        'accountId'), originator_credentials.get('apiKey'), originator_credentials.get('secret'))
    print(f'futures_order: {futures_order}')
    body = json.dumps([futures_order], separators=(',', ':'))
    request = {
        "method": "POST",
        "uri": "/order",
        "headers": {"requestid": str(uuid.uuid4())},
        "body": body,
        "params": {"instrument": BTCDAI_instrument.get('id')}
    }
    return request


def cancel_order(uuids, originator_credentials):
    client = Client('./resources/config/kovan.leverj.io/c21b18-64bdd3.json')
    client.set_api_url('https://kovan.leverj.io/futures/api/v1')
    all_config = client.get_all_config()
    instruments = all_config.get('instruments')
    BTCDAI_instrument = instruments.get('1')
    request_body = [{"op": "remove", "value": uuids}]
    request = {
        "method": "PATCH",
        "uri": "/order",
        "headers": {"requestid": str(uuid.uuid4())},
        "body": json.dumps(request_body),
        "params": {"instrument": BTCDAI_instrument.get('symbol')}
    }
    return request


def update_order(originator_credentials):
    pass


def register(originator_credentials):
    request_body = {"accountId": originator_credentials.get(
        'accountId'), "apiKey": originator_credentials.get('apiKey')}
    request = {
        "method": "GET",
        "uri": "/register",
        "headers": {},
        "body": json.dumps(request_body),
        "params": {}
    }
    return request


def unregister(originator_credentials):
    request_body = {"accountId": originator_credentials.get(
        'accountId'), "apiKey": originator_credentials.get('apiKey')}
    request = {
        "method": "GET",
        "uri": "/unregister",
        "headers": {},
        "body": json.dumps(request_body),
        "params": {}
    }
    return request


if __name__ == "__main__":
    print(f'running websocket client example')
    # instantiate a client
    websocket_client = WebsocketClient()
    # load credentials from the downloaded Gluon APIKey file
    originator_credentials = credentials(
        'resources/config/kovan.leverj.io/c21b18-64bdd3.json')

    uuids = ['9c8e9a00-a304-11eb-be7d-fc18fda03052']

    # call relevant method to generate request
    # use protected_endpoint_request util method to generate an authenticated request
    request = create_order(originator_credentials)

    # protected_endpoint_request util method adds required signature headers and formats the request
    protected_request_payload = protected_endpoint_request(
        request, originator_credentials)
    print(protected_request_payload)

    # emit from client to the connected websocket
    websocket_client.sio.emit(protected_request_payload.get(
        'event'), protected_request_payload.get('data'))
