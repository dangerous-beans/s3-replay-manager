import json
import os.path

def load_json_file(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        return json.load(f)


def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

