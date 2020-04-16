"""
Provides parsing methods to format Keycloak configuration
"""

import os
import json


def get_config_dict(file_path, logger=None):
    """
    Constructs a python dictonary from supplied schema in ./configs/file_path
    """
    try:
        with open(file_path) as json_file:
            config_dict = json.load(json_file)

            return parse_keycloak_configs(config_dict)
    except FileNotFoundError:
        if logger:
            logger.warning("Unable to find config file. "
                           "Please check spelling or place "
                           "an 'auth.json' at "
                           "{}/configs".format(os.getcwd()))
            exit()
        else:
            raise FileNotFoundError


def parse_keycloak_configs(config_dict, logger=None):
    """
    Sets up all the keycloak endpoints in the keycloak portion of the config
    """
    try:

        keycloak = config_dict["keycloak"]
        server = keycloak["KC_SERVER"]
        realm = keycloak["KC_REALM"]

        for endpoint in keycloak["FORMAT_ENDPOINTS"]:
            keycloak[endpoint] = keycloak[endpoint].format(server, realm)

        return config_dict

    except KeyError as KeyE:
        if logger:
            logger.warning("Error when accessing 'keycloak' "
                           "portion of configs. Check spelling "
                           "of keys. ")
            logger.warning(KeyE)
            exit()
        else:
            raise KeyError
