from web3.auto import w3
from eth_account.messages import defunct_hash_message


def round_with_precision(value, precision):
    val = round(float(value), precision)
    if precision == 0:
        return int(val)
    else:
        return val


def sign(data, secret):
    data = defunct_hash_message(primitive=bytes(data, 'utf-8'))
    signed_message = w3.eth.account.signHash(data, secret)
    return signed_message.signature.hex()


def to_vrs(signature):
    signature_hex = signature[2:]
    r = bytes.fromhex(signature_hex[0:64])
    s = bytes.fromhex(signature_hex[64:128])
    v = ord(bytes.fromhex(signature_hex[128:130]))

    return v, r, s


def bytes_to_hexstring(value):
    if isinstance(value, bytes) or isinstance(value, bytearray):
        return "0x" + "".join(map(lambda b: format(b, "02x"), value))
    elif isinstance(value, str):
        b = bytearray()
        b.extend(map(ord, value))
        return "0x" + "".join(map(lambda b: format(b, "02x"), b))
    else:
        raise AssertionError
