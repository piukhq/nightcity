"""Main module for Delamain."""

import socket
import sys

import requests
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class DelamainConfig(BaseSettings):
    """Config for Delamain."""

    nextdns_api_key: str
    nextdns_profile_id: str = "dee4c7"
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_prefix="DELAMAIN_")


config = DelamainConfig()

logger.remove()
logger.add(sys.stdout, level=config.log_level)


def _get_ip_address(host: str) -> str | None:
    try:
        return next(ip[0] for family, _, _, _, ip in socket.getaddrinfo(host, 0) if family == socket.AF_INET)
    except socket.gaierror:
        return None


def _nextdns_get_records() -> list[dict]:
    r = requests.get(
        f"https://api.nextdns.io/profiles/{config.nextdns_profile_id}/rewrites/",
        headers={"X-Api-Key": config.nextdns_api_key},
        timeout=5,
    )
    logger.debug(r.text)
    return r.json()["data"]


def _nextdns_delete_record(next_dns_id: str) -> None:
    r = requests.delete(
        f"https://api.nextdns.io/profiles/{config.nextdns_profile_id}/rewrites/{next_dns_id}",
        headers={"X-Api-Key": config.nextdns_api_key},
        timeout=5,
    ).raise_for_status()
    logger.debug(r.text)


def _nextdns_add_record(host: str, ip: str) -> None:
    r = requests.post(
        f"https://api.nextdns.io/profiles/{config.nextdns_profile_id}/rewrites/",
        headers={"X-Api-Key": config.nextdns_api_key},
        json={"name": host, "content": ip},
        timeout=5,
    )
    logger.debug(r.text)


def run(lookups: str) -> None:
    """Entrypoint for Delamain."""
    nextdns_records = _nextdns_get_records()
    for lookup in lookups.split(","):
        ip_address = _get_ip_address(lookup)
        if ip_address:
            logger.info(f"Found IP address {ip_address} for {lookup}")
            record = next((item for item in nextdns_records if item["name"] == lookup), None)
            if record:
                if ip_address != record["content"]:
                    logger.info(f"Updating {lookup} from {record['content']} to {ip_address}")
                    _nextdns_delete_record(record["id"])
                    _nextdns_add_record(lookup, ip_address)
            else:
                logger.info(f"Adding {lookup} with IP address {ip_address}")
                _nextdns_add_record(lookup, ip_address)
