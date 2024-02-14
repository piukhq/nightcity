import json

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from nightcity.settings import log, settings


class FreshService:  # noqa: N801
    """Freshservice class."""

    def __init__(self) -> None:
        """Initialize Freshservice class."""
        self.api_key = settings.freshservice_api_key
        self.baseurl = "https://bink.freshservice.com/api/v2"

    def get_all_freshservice_requestors(self) -> dict[str, int]:
        """Get Freshservice requestors."""
        ids = {}
        page_number = 1
        while True:
            try:
                response = requests.get(
                    url=f"{self.baseurl}/requesters",
                    params={
                        "per_page": "100",
                        "page": page_number,
                    },
                    auth=(self.api_key, "X"),
                )
                response.raise_for_status()
                data = json.loads(response.text)
                if data["requesters"] != []:
                    try:
                        for requester in data["requesters"]:
                            if requester["primary_email"] != "null":
                                ids.update({requester["id"]: requester["id"]})
                            else:
                                ids.update({requester["primary_email"]: requester["id"]})
                        page_number += 1
                        log.info(f"Moving onto page {page_number}")
                    except json.JSONDecodeError:
                        log("Failed to decode JSON response.")
                else:
                    break
            except requests.exceptions.RequestException as error:
                log.error("Error:", error)
        return ids

    def get_single_requester(self, email: str) -> dict[str, str] | None:
        """Get a single Freshservice requester."""
        user_name = email.split("@")[0]
        query = f'"primary_email:%27{user_name}%40bink.com%27"&include_agents=true'
        response = requests.get(
            url=f"{self.baseurl}/requesters?query={query}",
            auth=(self.api_key, "X"),
        )
        response.raise_for_status()
        try:
            data = json.loads(response.text)
            if data["requesters"] != []:
                return data
            else:
                log(f"Failed to get user {email}.")
        except requests.exceptions.RequestException as error:
            log.error("Error:", error)

    def forget_users(self, ids: dict | None = None, user_email: str | None = None, all: bool = False) -> None:
        """Forget Freshservice users."""
        if all:
            list_data = self.get_all_freshservice_requestors()
            data = list(list_data.values())
        elif user_email:
            data = {user_email: self.get_single_requester()}
        else:
            data = ids

        print(data)
        for id in data:
            try:
                forget = requests.delete(
                    url=f"{self.baseurl}/requesters/{id}/forget",
                    auth=(self.api_key, "X"),
                )
                log.info(forget.status_code)
                log.info(f"Forgetting user {id}.")
            except requests.exceptions.RequestException as error:
                log.error("Error:", error)

    def create_user(self, email: str, name: str) -> None:
        pass

    def run(self) -> None:
        """Run Freshservice."""
        self.forget_users(all=False)
