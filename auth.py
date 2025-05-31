#!/usr/bin/env python3

from nso_api.nso_api import NSO_API
from nso_api.nxapi import NXApi

from utils import load_json_file, save_json_file


def handle_user_data_update(nso, context):
    print(f"User data updated for context '{context}'. Saving...")
    save_json_file("nso_tokens.json", nso.get_user_data())


def handle_global_data_update(data):
    print(f"Global data updated. Saving...")
    save_json_file("nso_global_data.json", data)


def handle_logged_out(nso, context):
    print(f"Client for context '{context}' was logged out.")


def get_nso_api() -> NSO_API | None:
    nsapi = NXApi(
        # f"nso-cli.py {NSO_API.get_version()} (discord=jetsurf)"
        # TODO: Replace with your actual user agent string
        f"nso-cli.py {NSO_API.get_version()} (dangerous-beans)",
    )

    context = None
    nso = NSO_API(nsapi, context)
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
            return None

        print("Login successful")

    return nso


