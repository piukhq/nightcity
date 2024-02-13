import requests
from nightcity.settings import settings
from base64 import b64encode
import json

class freshservice:
    """Freshservice class."""
    def __init__(self) -> None:
        self.api_key = settings.freshservice_api_key
        # self.auth = f"{settings.freshservice_api_key} : 'x'"
        self.baseurl = "https://bink.freshservice.com/api/v2"

    def get_all_freshservice_requestors(self):
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
                if response.status_code == 200 and data['requesters'] != []:
                    try:
                        for requester in data['requesters']:
                            ids.update({requester['primary_email']: requester['id']})
                            print(f"email {requester['primary_email']} with id {requester['id']} has been added to the list.")
                        page_number += 1
                        print(f"Moving onto page {page_number}")
                    except json.JSONDecodeError:
                        print("Failed to decode JSON response.")
                else:
                    break
            except requests.exceptions.RequestException as error:
                print("Error:", error)
        return(ids)

    def get_single_requester(self, email: str|None = None):
        """Get a single Freshservice requester."""
        user_name = email.split('@')[0]
        query= f'"primary_email:%27{user_name}%40bink.com%27"&include_agents=true',
        response = requests.get(
            url=f'{self.baseurl}/requesters?query={query[0]}',
            auth=(self.api_key, "X"),
        )
        try:
            data = json.loads(response.text)
            if response.status_code == 200 and data['requesters'] != []:
                return(data)
            else:
                print(f"Failed to get user {email}. With status code: {response.status_code} for reason: {response.text}")
        except requests.exceptions.RequestException as error:
            print("Error:", error)

    def forget_users(self, ids: dict|None = None, user_email: str|None = None, all: bool = False):
        """Forget Freshservice users."""
        if all:
            list_data=self.get_all_freshservice_requestors()
            data = list(list_data.values())
            print(data)
        elif user_email:
            data = {user_email: self.get_single_requester()}
            print(data)
        else:
            data=ids
            print(data)

        while True:
            try:
                if data == []:
                    break
                forget = requests.delete(
                    url=f"{self.baseurl}/requesters/{data[0]}/forget",
                    auth=(self.api_key, "X"),
                )
                if forget.status_code == 200:
                    print(f"User {data[0]} has been forgotten.")
                    data.pop(0)
                else:
                    print(f"Failed to forget user {data[0]}. With status code: {requests.status_codes}")
            except requests.exceptions.RequestException as error:
                print("Error:", error)
