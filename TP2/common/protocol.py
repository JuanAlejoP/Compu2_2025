import struct
from common.serialization import to_json, from_json

def build_message(data: dict) -> bytes:
    payload = to_json(data).encode('utf-8')
    length = struct.pack('!I', len(payload))
    return length + payload

def parse_message(data: bytes) -> dict:
    # data should be the full payload (after reading length)
    return from_json(data.decode('utf-8'))
