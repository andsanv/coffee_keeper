import json
from config import data_path

def write_data(obj: dict):
    with open(data_path, 'w') as fout:
        json.dump(obj, fout)

def read_data():
    with open(data_path, 'r') as fin:
        try:
            loaded = json.load(fin)
            new = {}

            for key, val in loaded.items():
                new[int(key)] = val

            return new
        except:
            return {}