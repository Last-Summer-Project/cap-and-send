import logging
from dataclasses import dataclass
import requests
from getpass import getpass
import pathlib
import json


@dataclass
class JWTClient:
    access: str = None
    refresh: str = None
    header_type: str = "Bearer"
    base_endpoint: str = "http://172.30.1.3/api/v1"
    cred_path: pathlib.Path = pathlib.Path("creds.json")
    requestsHold: int = 30
    requests: int = 0

    def __post_init__(self):
        if self.cred_path.exists():
            try:
                data = json.loads(self.cred_path.read_text())
            except Exception as e:
                logging.error("Assuming creds has been tampered with", e)
                data = None
            if data is None:
                self.clear_tokens()
                self.perform_auth()
            else:
                self.access = data.get('access')
                self.refresh = data.get('refresh')
                token_verified = self.verify_token()
                if not token_verified:
                    refreshed = self.perform_refresh()
                    if not refreshed:
                        logging.error("invalid data, login again.")
                        self.clear_tokens()
                        self.perform_auth()
        else:
            self.perform_auth()

    def pre_req(self):
        self.requests += 1
        if self.requests > self.requestsHold:
            self.perform_refresh()
            self.requests = 0

    def get_headers(self, header_type=None):
        _type = header_type or self.header_type
        token = self.access
        if not token:
            return {}
        return {
            "Authorization": f"{_type} {token}"
        }

    def get_endpoint(self, endpoint):
        if self.base_endpoint not in str(endpoint):
            endpoint = f"{self.base_endpoint}/{endpoint}"
        return endpoint.replace("//", "/").replace("http:/", "http://")

    def perform_auth(self):
        endpoint = f"{self.base_endpoint}/auth/login"
        username = input("What is your loginId?\n")
        password = getpass("What is your password?\n")
        r = requests.post(endpoint, json={'loginId': username, 'password': password})
        if r.status_code != 200:
            raise Exception(f"Access not granted: {r.text}")
        logging.info('access granted')
        self.write_creds(r.json())

    def write_creds(self, data: dict):
        if self.cred_path is not None:
            self.access = data.get('data').get('access')
            self.refresh = data.get('data').get('refresh')
            if self.access and self.refresh:
                self.cred_path.write_text(json.dumps(data.get('data')))

    def verify_token(self):
        endpoint = f"{self.base_endpoint}/auth/verify"
        r = requests.get(endpoint, headers=self.get_headers())
        return r.status_code == 200

    def clear_tokens(self):
        self.access = None
        self.refresh = None
        if self.cred_path.exists():
            self.cred_path.unlink()

    def perform_refresh(self):
        logging.info("Refreshing token.")
        headers = self.get_headers()
        data = {
            "refresh": f"{self.refresh}"
        }
        endpoint = f"{self.base_endpoint}/auth/refresh"
        r = requests.post(endpoint, json=data, headers=headers)
        if r.status_code != 200:
            self.clear_tokens()
            return False
        refresh_data = r.json()
        if 'access' not in refresh_data:
            self.clear_tokens()
            return False
        stored_data = {
            'access': refresh_data.get('access'),
            'refresh': refresh_data.get('refresh'),
        }
        self.write_creds(stored_data)
        return True

    def get(self, endpoint):
        self.pre_req()
        r = requests.get(self.get_endpoint(endpoint), headers=self.get_headers())
        if r.status_code != 200:
            raise Exception(f"Request not complete {r.text}")
        data = r.json()
        return data

    def post(self, endpoint, data):
        self.pre_req()
        r = requests.post(self.get_endpoint(endpoint), headers=self.get_headers(), json=data)
        if r.status_code != 200:
            raise Exception(f"Request not complete {r.text}")
        data = r.json()
        return data

    def put(self, endpoint, data):
        self.pre_req()
        r = requests.post(self.get_endpoint(endpoint), headers=self.get_headers(), json=data)
        if r.status_code != 200:
            raise Exception(f"Request not complete {r.text}")
        data = r.json()
        return data


if __name__ == "__main__":
    client = JWTClient(base_endpoint="http://localhost:8080/api/v1")
    print(client.get("device/get"))
