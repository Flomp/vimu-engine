import json
from typing import Any

import requests
from pydantic.json import pydantic_encoder

from models.api import APIResponse


class Pocketbase:
    def __init__(
            self,
            base_url: str,
            admin_user: str,
            admin_password: str
    ):
        self.base_url = base_url
        response = requests.post(base_url + '/api/admins/auth-with-password',
                                 {'identity': admin_user, 'password': admin_password})
        if response.status_code == 200:
            self.token = response.json()['token']
        else:
            raise Exception("Login failed")

    def _send(self, method: str, url: str = "", data: Any = None, params: Any = None):
        if self.token is None:
            raise Exception("Unauthorized")
        response = requests.request(method, self.base_url + url, json=data,
                                    params=params,
                                    headers={'Authorization': self.token,
                                             'content-type': 'application/json; charset=UTF-8'})

        if response.status_code != 200:
            return APIResponse(status="error", data=None, error=response.text)

        return APIResponse(status="success", data=response.json(), error=None)

    def get_first_where(self, collection: str, condition: str):
        response = self._send('GET', '/api/collections/subscriptions/records',
                              params=f"filter={condition}")

        if response.status == "error" or len(response.data['items']) == 0:
            return None

        data = response.data['items'][0]

        return data

    def create(self, collection: str, data: Any) -> APIResponse:
        return self._send('POST', f'/api/collections/{collection}/records',
                          data)

    def update(self, collection: str, data: Any) -> APIResponse:
        return self._send('PATCH', f'/api/collections/{collection}/records/' + data.get('id'),
                          data)

    def delete(self, collection: str, data: any) -> APIResponse:
        return self._send('DELETE', f'/api/collections/{collection}/records/' + data.get('id'))
