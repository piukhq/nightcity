"""Main module for Delamain."""

import contextlib
import json
import socket
from pathlib import Path

import requests
import yaml
from box import Box

from nightcity.settings import keyvault_client, log


class NextDNS:
    """Manages NextDNS."""

    def __init__(self) -> None:
        """Initialise NextDNS."""
        self.nextdns: dict = json.loads(keyvault_client.get_secret("nextdns").value)
        self.profile_id: str = self.nextdns["profile_id"]
        self.api_key: str = self.nextdns["api_key"]
        self.headers: dict = {"X-Api-Key": self.api_key}
        self.timeout: int = 5

    def get_rewrites(self) -> list[dict]:
        """Get Rewrites from NextDNS."""
        r = requests.get(
            f"https://api.nextdns.io/profiles/{self.profile_id}/rewrites/",
            headers=self.headers,
            timeout=self.timeout,
        )
        r.raise_for_status()
        log.debug(r.text)
        return r.json()["data"]

    def delete_rewrite(self, next_dns_id: str) -> None:
        """Delete a rewrite from NextDNS."""
        r = requests.delete(
            f"https://api.nextdns.io/profiles/{self.profile_id}/rewrites/{next_dns_id}",
            headers=self.headers,
            timeout=self.timeout,
        )
        r.raise_for_status()
        log.debug(r.text)

    def add_rewrite(self, name: str, content: str) -> None:
        """Add a rewrite to NextDNS."""
        r = requests.post(
            f"https://api.nextdns.io/profiles/{self.profile_id}/rewrites/",
            json={"name": name, "content": content},
            headers=self.headers,
            timeout=self.timeout,
        )
        r.raise_for_status()
        log.debug(r.text)


def _get_ip_address(host: str) -> str | None:
    try:
        return next(ip[0] for family, _, _, _, ip in socket.getaddrinfo(host, 0) if family == socket.AF_INET)
    except socket.gaierror:
        return None


def load_config() -> Box:
    """Load the configuration file."""
    config_file = Path("/var/config/delamain.yaml")
    if config_file.exists():
        return Box(yaml.safe_load(config_file.read_text()))
    return Box(yaml.safe_load(Path("delamain.yaml").read_text()))


def run() -> None:
    """Entrypoint for Delamain."""
    nextdns = NextDNS()
    config = load_config()

    nextdns_rewrites = nextdns.get_rewrites()

    for cname in config.dns_rewrites.cname:
        rewrite = None
        with contextlib.suppress(StopIteration):
            rewrite = next(rewrite for rewrite in nextdns_rewrites if rewrite["name"] == cname.name)
        if rewrite and rewrite["content"] != cname.record:
            log.info(f"Updating '{cname.name}' from '{rewrite['content']}' to '{cname.record}'")
            nextdns.delete_rewrite(rewrite["id"])
            nextdns.add_rewrite(cname.name, cname.record)
        if not rewrite:
            log.info(f"Setting '{cname.name}' to '{cname.record}'")
            nextdns.add_rewrite(cname.name, cname.record)

    for record in config.dns_rewrites.a:
        rewrite = None
        ip_address = _get_ip_address(record)
        if not ip_address:
            log.warning(f"Couldn't resolve '{record}'")
            continue
        with contextlib.suppress(StopIteration):
            rewrite = next(rewrite for rewrite in nextdns_rewrites if rewrite["name"] == record)
        if rewrite and rewrite["content"] != ip_address:
            log.info(f"Updating '{record}' from '{rewrite['content']}' to '{ip_address}'")
            nextdns.delete_rewrite(rewrite["id"])
            nextdns.add_rewrite(record, ip_address)
        if not rewrite:
            log.info(f"Setting '{record}' to '{ip_address}'")
            nextdns.add_rewrite(record, ip_address)
