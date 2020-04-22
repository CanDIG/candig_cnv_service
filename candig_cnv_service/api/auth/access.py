"""
Auth module for service
"""

import flask
import requests
import jwt

from candig_cnv_service.api.logging import structured_log as struct_log
from candig_cnv_service.api.logging import logger
from candig_cnv_service.api.auth import get_kc_handler
from candig_cnv_service.api.exceptions import HandlerError

_ACCESSHANDLER = None


def _report_proxy_auth_error(key, **kwargs):
    """
    Generate standard log message for warning:
    API access without
    :param **kwargs: arbitrary keyword parameters
    """
    message = 'Attempt to access with invalid proxy/api key: ' + key
    logger().warning(struct_log(action=message, **kwargs))


def auth_key(api_key, required_scopes=None):
    fc = flask.current_app.config
    # Allow CanDIG API gateway to handle auth (not for standalone use)
    if fc.get('AUTH_METHOD') == 'GATEWAY':
        # TODO: use gateway client certificate instead
        fh = flask.request.headers
        if not fh["Host"] == fc.get('GATEWAY_HOST'):
            _report_proxy_auth_error(api_key)
            return None
    # For now, any api_key to local app should work
    # TODO: refine auth methods
    return {}


def decode():
    fh = flask.request.headers
    if not fh.get("Authorization"):
        _report_proxy_auth_error("NO AUTH HEADER")

    token = fh["Authorization"].split("Bearer ")[1]
    decoded = get_kc_handler().decode_token(token)
    return decoded


def get_access_from_authz(dataset):
    decoded = decode()
    payload = {
        "issuer": decoded["iss"],
        "username": decoded["sub"],
        "dataset": dataset
    }

    url = "http://0.0.0.0:8885/authz/access"
    headers = flask.request.headers
    request_handle = requests.Session()
    resp = request_handle.get(
        "{}".format(url),
        headers=headers,
        params=payload,
        timeout=5
        )

    return resp


class Access_Handler:
    def __init__(self):
        self.alist = {}

    def verify(self, level, dataset):
        try:
            decoded = decode()
            # TODO invalidate data if token is expired
            user_level = self.get_level(decoded["sub"], dataset)
            if (user_level >= level):
                print(self.alist)
                return [True]
        except jwt.DecodeError:
            return [False, "Decode"]
        return [False, "Level"]

    def get_level(self, username, dataset):
        try:
            user = self.alist[username]
            level = user[dataset]

            return level

        except KeyError:
            # No info on user or dataset
            access = get_access_from_authz(dataset)
            self.alist[username] = access
            return access[dataset]


def get_access_handler():
    global _ACCESSHANDLER
    if not _ACCESSHANDLER:
        raise HandlerError("Access")
    return _ACCESSHANDLER


def create_access_handler():
    global _ACCESSHANDLER
    _ACCESSHANDLER = Access_Handler()
