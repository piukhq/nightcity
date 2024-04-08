"""Quickhack for Stonegate SMB to Boreas API.

Disclaimer: Security is not a concern for this quickhack as this is a temporary solution.
"""

import json
import os
from typing import Generator

import requests
from azure.storage.fileshare import ShareClient

from nightcity.settings import log

client = ShareClient.from_connection_string(
    conn_str="DefaultEndpointsProtocol=https;AccountName=sggtactical;AccountKey=5isH1DYwAaWftB5SHlQQLsliQk6h09SH5tBMscAtSFltca4YD29NdBB2ak8urXvuylK6kZHWM0pi+AStpWAzNA==;EndpointSuffix=core.windows.net",
    share_name="transactions",
)


def checkly_heartbeat() -> None:
    """Inform Checkly that the job has completed."""
    url = "https://ping.checklyhq.com/ba868f10-ca0d-41ab-a61b-2325492b3954"
    requests.get(url, timeout=5)


def list_files(dir_path: str = "") -> Generator[str, None, None]:
    """List all files in the Stonegate SMB directory."""
    directory_client = client.get_directory_client(dir_path)
    for file in directory_client.list_directories_and_files():
        name, is_directory = file["name"], file["is_directory"]
        path = os.path.join(dir_path, name)  # noqa: PTH118
        if is_directory:
            childrens = list_files(
                dir_path=path,
            )
            yield from childrens
        else:
            yield path


def send_to_boreas(payload: dict) -> None:
    """Send data to Boreas API."""
    request = requests.post(
        "http://boreas-api.olympus/retailers/stonegate/transactions",
        headers={"X-API-Key": "3694954aaf9acce7452a1b54d6960a0d"},
        json=payload,
        timeout=5,
    )
    request.raise_for_status()


def run() -> None:
    """Fetch Stonegate SMB files and upload to Boreas API."""
    checkly_heartbeat()
    for file in list_files():
        try:
            file_client = client.get_file_client(file)
            data = file_client.download_file()
            payload = [json.loads(data.readall().decode("utf-8"))]
            send_to_boreas(payload)
            file_client.delete_file()
            log.info(f"Uploaded {file} to Boreas API.")
        except (json.decoder.JSONDecodeError, requests.exceptions.HTTPError, UnicodeDecodeError):  # noqa: PERF203
            log.error(f"Failed to upload {file} to Boreas API, will retry later.")
            continue
