#!/usr/bin/env python3

import json
import os.path
import re

from nso_api.nso_api import NSO_API
from nso_api.imink import IMink
from nso_api.nxapi import NXApi


def load_json_file(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, "r") as f:
        return json.load(f)


def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)


def handle_user_data_update(nso, context):
    print(f"User data updated for context '{context}'. Saving...")
    save_json_file("nso_tokens.json", nso.get_user_data())


def handle_global_data_update(data):
    print(f"Global data updated. Saving...")
    save_json_file("nso_global_data.json", data)


def handle_logged_out(nso, context):
    print(f"Client for context '{context}' was logged out.")


def get_codes():
    """
    Extracts codes from a file named 'codes.txt' in the current directory.
    The codes are expected to be in the format XXXX-XXXX-XXXX-XXXX, where X is an uppercase letter or digit.

    Returns:
        list: A list of extracted codes.
    """
    with open("./codes.txt", "r") as file:
        contents = file.read()

    # Regular expression to match the pattern "XXXX-XXXX-XXXX-XXXX" (where X is an uppercase letter or digit)
    pattern = r"\b[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}\b"
    codes = re.findall(pattern, contents)

    return codes


def download_replay(nso, replay_code):
    """Downloads a replay using the provided replay ID."""
    replay_code = replay_code.strip().replace("-", "")
    result = nso.s3.get_replay_info(replay_code)
    if not result:
        print(f"Failed to find replay with code {replay_code}")
        return None
    replay_id = result["data"]["replay"]["id"]
    return nso.s3.download_replay_from_code(replay_id)


# imink = IMink(f"nso-cli.py {NSO_API.get_version()} (discord=jetsurf)")
nsapi = NXApi(
    f"nso-cli.py {NSO_API.get_version()} (discord=jetsurf)"
)  ## For NXApi use instead

# Context is a value of your choice that will be provided to callbacks. If you
#  create multiple client objects, you can use it to tell them apart. If you
#  don't, its value does not matter.
context = 123

# nso = NSO_API(imink, context)
nso = NSO_API(nsapi, context)
# nso.app_version_override = "2.7.1"
nso.on_user_data_update(handle_user_data_update)
nso.on_global_data_update(handle_global_data_update)
nso.on_logged_out(handle_logged_out)

nso.load_global_data(load_json_file("nso_global_data.json"))

keys = load_json_file("nso_tokens.json")
if keys:
    print("I have saved keys, skipping login")
    nso.load_user_data(keys)
else:
    url = nso.get_login_challenge_url()
    print(f"Login challenge URL: {url}")
    user_input = ""
    while not "://" in user_input:
        print("Paste login URL here:")
        user_input = input().rstrip()
    if not nso.complete_login_challenge(user_input):
        print(f"Login failed: {nso.get_error_message()}")
        exit(1)

    print("Login successful")


replay_list = nso.s3.get_replay_list()
# print(replay_list)

for replay_id in get_codes():
    print(f"Downloading replay {replay_id}...")
    replay = download_replay(nso, replay_id)
    if replay is not None:
        print(f"Replay {replay_id} downloaded successfully.")
    else:
        print(f"Failed to download replay {replay_id}: {nso.get_error_message()}")
print("All replays processed.")
