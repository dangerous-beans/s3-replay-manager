#!/usr/bin/env python3

import re

from nso_api.nso_api import NSO_API

from auth import get_nso_api

def get_codes() -> list[str]:
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


def download_replay(nso: NSO_API, replay_code: str):
    """Downloads a replay using the provided NSO API instance and replay code.
    Args:
        nso (NSO_API): The NSO API instance.
        replay_code (str): The replay code to download.
    Returns:"""
    replay_code = replay_code.strip().replace("-", "")
    result = nso.s3.get_replay_info(replay_code)
    if not result or "data" not in result or "replay" not in result["data"] or not result["data"]["replay"]:
        return None
    replay_id = result["data"]["replay"]["id"]
    return nso.s3.download_replay_from_code(replay_id)


def download_all_replays(nso: NSO_API):
    """Downloads all replays using the provided NSO API instance."""
    for replay_code in get_codes():
        print(f"Downloading replay {replay_code}...")
        result = download_replay(nso, replay_code)
        if result is not None:
            print(f"Replay {replay_code} successfully queued for download.")
        else:
            print(f"Failed to find replay with code {replay_code} (maybe the code is wrong?): {nso.get_error_message()}")
    print("All replays processed.")


if __name__ == "__main__":
    nso = get_nso_api()
    if nso is None:
        print("Failed to initialize NSO API.")
    else:
        download_all_replays(nso)
