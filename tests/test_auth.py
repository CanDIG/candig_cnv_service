import string
import random
import uuid
import pytest
import os
import sys

import requests
from unittest.mock import Mock, patch

from werkzeug.datastructures import Headers
from test_data.structs import goodHeader, badHeader, access_list
sys.path.append("{}/{}".format(os.getcwd(), "candig_cnv_service"))
sys.path.append(os.getcwd())

from candig_cnv_service import orm
from candig_cnv_service.__main__ import app
from candig_cnv_service.api import operations
from candig_cnv_service.api import auth
from candig_cnv_service.tools.parser import get_config_dict


def mocked_authz(*args, **kwargs):    
    auth_params = kwargs["params"]

    access = access_list[(auth_params["username"], auth_params["issuer"])]
    response = {}
    response[auth_params["dataset"]] = access[auth_params["dataset"]]
    return response


@pytest.fixture(name="test_client")
def load_test_client(db_filename="auth.db"):
    try:
        orm.close_session()
        os.remove(db_filename)
    except FileNotFoundError:
        pass
    except OSError:
        pass

    context = app.app.app_context()

    with context:
        orm.init_db("sqlite:///" + db_filename)
        app.app.config["BASE_DL_URL"] = "http://127.0.0.1"
        configs = get_config_dict("./configs/auth.json")
        auth.create_handler(configs["keycloak"])
    return context


@patch('candig_cnv_service.api.auth.access.requests.Session.get', side_effect=mocked_authz)
def test_correct_authorization(mock_session, test_client):
    """
    Test add_patients method
    """

    context = test_client
    patient_1, patient_2, patient_3 = load_test_patients()

    with context:
        with app.app.test_request_context(
            headers=goodHeader.headers
        ):
            response = auth.access.get_access_level("TF4CN")
            print(response)
            assert response["TF4CN"] == 4


def load_test_patients():
    """
    Load some mock patient data
    """
    patient_1_id = uuid.uuid4().hex
    patient_2_id = uuid.uuid4().hex
    patient_3_id = 1

    test_patient_1 = {
        "patient_id": patient_1_id,
    }

    test_patient_2 = {
        "patient_id": patient_2_id,
    }

    test_patient_3 = {
        "patient_id": patient_3_id,
    }

    return test_patient_1, test_patient_2, test_patient_3


def load_test_samples():
    """
    Return some mock sample data
    """
    samp = lambda x: "".join(
        random.choice(string.ascii_lowercase) for i in range(x)
    )

    patient_1, _, _ = load_test_patients()

    sample_1 = {"sample_id": samp(5), "patient_id": patient_1["patient_id"], "description": patient_1["patient_id"] + "sample_1"}

    sample_2 = {"sample_id": samp(5), "patient_id": patient_1["patient_id"], "description": patient_1["patient_id"] + "sample_2"}

    sample_3 = {"sample_id": samp(5)}

    return sample_1, sample_2, sample_3, patient_1


def load_test_samples_with_tags():
    """
    Return some mock sample data with tags
    """
    samp = lambda x: "".join(
        random.choice(string.ascii_lowercase) for i in range(x)
    )

    patient_1, _, _ = load_test_patients()

    sample_1 = {
        "sample_id": samp(5),
        "patient_id": patient_1["patient_id"],
        "tags": ["Canadian", "Ovarian"],
        "description": "sample_1",
    }

    sample_2 = {
        "sample_id": samp(5),
        "patient_id": patient_1["patient_id"],
        "tags": ["Canadian", "Liver", "Adult"],
        "description": "sample_2",
    }

    return sample_1, sample_2, patient_1


def load_test_segment():
    """
    Return some mock segments data
    """

    sample_1, _, _, patient_1 = load_test_samples()

    segment_1 = {
        "patient_id": patient_1["patient_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome_number": "5",
                "start_position": 12523,
                "end_position": 23425,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    segment_2 = {
        "patient_id": patient_1["patient_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome_number": "5",
                "start_position": 23426,
                "end_position": 34326,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    segment_3 = {
        "patient_id": patient_1["patient_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome_number": "5",
                "start_position": 34327,
                "end_position": 44296,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    return patient_1, sample_1, segment_1, segment_2, segment_3


