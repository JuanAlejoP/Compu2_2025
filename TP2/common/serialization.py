import json
import pickle

def to_json(data: dict) -> str:
    return json.dumps(data)

def from_json(data: str) -> dict:
    return json.loads(data)

def to_pickle(data: dict) -> bytes:
    return pickle.dumps(data)

def from_pickle(data: bytes) -> dict:
    return pickle.loads(data)
