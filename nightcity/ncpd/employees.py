import requests
from nightcity.settings import settings
from base64 import b64encode
import json

auth = b64encode(f"{settings.bamboohr_api_key}:x".encode()).decode()

def _get_bamboohr_users():
    """Get all BambooHR users."""
    url = "https://api.bamboohr.com/api/gateway.php/bink/v1/employees/directory"
    headers = {
        "Accept": "application/json",
        "authorization": f"Basic {auth}",
    }

    data = requests.get(url, headers=headers)
    data = json.loads(data.text)
    for key, value in data.items():
        for each in value[]:
            print(each)


_get_bamboohr_users()
