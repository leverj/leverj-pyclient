import json
import time

from leverj.util import bytes_to_hexstring, round_with_precision, sign, to_vrs


def credentials(apikey_file):
    with open(apikey_file) as json_apikey_file:
        config_data = json.load(json_apikey_file)
        print(f'config_data: {config_data}')
        return config_data


def protected_endpoint_request(request_payload, originator_credentials):
    method = request_payload.get('method')
    uri = request_payload.get('uri')
    request_headers = request_payload.get('headers')
    body = request_payload.get('body')
    params = request_payload.get('params')
    retry = request_payload.get('retry')

    request_nonce = None

    nonce = int(time.time()*1000)
    signature = sign(str(nonce), originator_credentials.get('secret'))
    v, r, s = to_vrs(signature)

    auth_header = f"NONCE {originator_credentials.get('accountId')}.{originator_credentials.get('apiKey')}" \
        f".{v}"\
        f".{bytes_to_hexstring(r)}"\
        f".{bytes_to_hexstring(s)}"

    _headers = {"Authorization": auth_header, "Nonce": str(
        nonce), "Content-Type": "application/json"}
    headers = {**_headers, **request_headers}

    data = {"headers": headers, "method": method, "uri": uri,
            "params": params, "body": json.loads(body), "retry": retry}
    protected_request = {
        "event": method + " " + uri,
        "data": data
    }

    return protected_request
