"""
Auth module for service
"""

import flask

import jwt
# from jwt.algorithms import RSAAlgorithm
# from keycloak import KeycloakOpenID
import requests

from candig_cnv_service.api.logging import structured_log as struct_log
from candig_cnv_service.api.logging import logger
from candig_cnv_service.api.auth import get_handler

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


def get_access_level(dataset):
    fh = flask.request.headers
    if not fh.get("Authorization"):
        _report_proxy_auth_error("NO AUTH HEADER")

    token = fh["Authorization"].split("Bearer ")[1]
    decode = get_handler().decode_token(token)

    
    payload = {
        "issuer": decode["iss"],
        "username": decode["sub"],
        "dataset": dataset
    }

    url = "http://0.0.0.0:8885/authz/access"
    headers = fh
    request_handle = requests.Session()
    resp = request_handle.get("{}".format(url), headers=headers, params=payload, timeout=5)

    return resp
