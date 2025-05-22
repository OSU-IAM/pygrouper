"""
pygrouper.client
"""

import requests
from .exceptions import GrouperAPIException, GrouperAPIRequestsException, GrouperAPIError

WS_VERSIONS = [
    'v2_2_000',
    'v2_3_000',
    'v2_4_000',
    'v2_5_000',
    'v4_0_000',
]

class GrouperClient(object):
    def __init__(self, host, user, password, ws_version=None, timeout=60):
        self._host = host
        self._api_user = user
        self._api_pass = password
        self._timeout = timeout

        if ws_version == None:
            self._ws_version = 'v2_2_000'
        else:
            if ws_version in WS_VERSIONS:
                self._ws_version = ws_version
            else:
                raise(GrouperAPIException("Invalid Grouper WS version: {ws_version}"))

    def _uri(self, endpoint):
        return f"https://{self._host}/grouper-ws/servicesRest/json/{self._ws_version}/{endpoint}"

    def _get(self, endpoint):
        uri = self._uri(endpoint)
        try:
            r = requests.get(uri, auth=(self._api_user, self._api_pass), timeout=self._timeout)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        except requests.exceptions.RequestException as err:
            raise(GrouperAPIRequestsException(err))
        return r.json()

    # can probably modify this to take additonal params
    def _put(self, endpoint, data=None):
        if data == None:
            data = {}
        uri = self._uri(endpoint)
        try:
            r = requests.put(uri, json=data, auth=(self._api_user, self._api_pass), timeout=self._timeout)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        except requests.exceptions.RequestException as err:
            raise(GrouperAPIRequestsException(err))
        return r.json()

    def _post(self, endpoint, payload=None):
        if payload == None:
            payload = {}

        headers = None
        if self._ws_version in ['v2_2_000', 'v2_3_000']:
            # override Content-Type header because Grouper WS API < v2.4 is dumb
            # and wants 'text/x-json' instead of the standard 'application/json'
            headers={'Content-Type': 'text/x-json'}

        uri = self._uri(endpoint)
        try:
            r = requests.post(uri, auth=(self._api_user, self._api_pass), json=payload, headers=headers, timeout=self._timeout)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        except requests.exceptions.RequestException as err:
            raise(GrouperAPIRequestsException(err))
        return r.json()

    def _delete(self, endpoint):
        uri = self._uri(endpoint)
        try:
            r = requests.delete(uri, auth=(self._api_user, self._api_pass), timeout=self._timeout)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise(GrouperAPIError(err))
        except requests.exceptions.RequestException as err:
            raise(GrouperAPIRequestsException(err))
        return r.json()

    def _escape(self, instr):
        return instr.replace(':', '%3A')
