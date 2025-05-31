#!/usr/bin/env python3

from nso_api.nso_api import NSO_API
from nso_api.nxapi import NXApi

from utils import load_json_file, save_json_file


NSO_TOKENS_FILE = "nso_tokens.json"
NSO_GLOBAL_DATA_FILE = "nso_global_data.json"

# TODO: Replace with your actual user agent string
USER_AGENT = f"nso-cli.py {NSO_API.get_version()} (dangerous-beans)"


def handle_user_data_update(nso: NSO_API, context: str):
    print(f"User data updated for context '{context}'. Saving...")
    save_json_file(NSO_TOKENS_FILE, nso.get_user_data())


def handle_global_data_update(data: dict) -> None:
    print(f"Global data updated. Saving...")
    save_json_file(NSO_GLOBAL_DATA_FILE, data)


def handle_logged_out(nso: NSO_API, context: str) -> None:
    print(f"Client for context '{context}' was logged out.")


def login_from_cli() -> NSO_API | None:
    """
    CLI login function for NSO API.
    Prompts the user to paste the login URL and handles the login process.
    """

    nso = get_nso_api()
    if nso is None:
        print("Failed to initialize NSO API.")
        return None

    keys = load_json_file(NSO_TOKENS_FILE)
    if keys:
        print("I have saved keys, skipping login")
        nso.load_user_data(keys)
        return nso
    
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

def get_nso_api() -> NSO_API | None:
    context = None

    nsapi = NXApi(
        # f"nso-cli.py {NSO_API.get_version()} (discord=jetsurf)"
        USER_AGENT,
    )

    nso = NSO_API(nsapi, context)
    nso.on_user_data_update(handle_user_data_update)
    nso.on_global_data_update(handle_global_data_update)
    nso.on_logged_out(handle_logged_out)
    nso.load_global_data(load_json_file(NSO_GLOBAL_DATA_FILE))

    return nso
