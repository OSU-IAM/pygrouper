""" pygrouper.client
"""

import requests

WS_VERSIONS = [
    'v2_2_000'
]

class GrouperClient(object):
    def __init__(self, host, user, password, ws_version=None):
        self._host = host
        self._api_user = user
        self._api_pass = password
        if ws_version == None:
            self._ws_version = 'v2_4_000'
        else:
            if ws_version in WS_VERSIONS:
                self._ws_version = ws_version
            else:
                raise(GrouperAPIException("Invalid Grouper WS version: {ws_version}"))

    def _uri(self, endpoint):
        return f"https://{self._host}/grouper-ws/servicesRest/json/{self._ws_version}/{endpoint}"

    def _get(self, endpoint):
        uri = self._uri(endpoint)
        r = requests.get(uri, auth=(self._api_user, self._api_pass))
        r.raise_for_status()
        return r.json()

    def _put(self, endpoint):
        uri = self._uri(endpoint)
        r = requests.put(uri, auth=(self._api_user, self._api_pass))
        r.raise_for_status()
        return r.json()

    def _post(self, endpoint, payload=None):
        if payload == None:
            payload = {}

        if self._ws_version in ['v2_2_000']:
            # override Content-Type header because Grouper WS API < v2.4 is dumb
            # and wants 'text/x-json' instead of the standard 'application/json'
            headers={'Content-Type': 'text/x-json'}

        uri = self._uri(endpoint)
        r = requests.post(uri, auth=(self._api_user, self._api_pass), json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

    def _delete(self, endpoint):
        uri = self._uri(endpoint)
        r = requests.delete(uri, auth=(self._api_user, self._api_pass))
        r.raise_for_status()
        return r.json()

    def _escape(self, instr):
        return instr.replace(':', '%3A')
