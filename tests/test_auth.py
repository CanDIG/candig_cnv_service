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
        auth.create_kc_handler(configs["keycloak"])
        app.app.config["auth_flag"] = True
    return context


@patch('candig_cnv_service.api.auth.access.requests.Session.get', side_effect=mocked_authz)
def test_correct_authorization(mock_session, test_client):
    """
    Test access level verification
    """

    context = test_client
    dataset_1, dataset_2, dataset_3 = load_test_datasets()

    with context:
        with app.app.test_request_context(
            headers=goodHeader.headers
        ):
            auth.access.create_access_handler()
            ah = auth.access.get_access_handler()
            res = ah.verify(dataset="TF4CN", level=4)
            assert res[0] == True


@patch('candig_cnv_service.api.auth.access.requests.Session.get', side_effect=mocked_authz)
def test_invalid_token_decode(mock_session, test_client):
    """
    Test access level verification
    """

    context = test_client
    dataset_1, dataset_2, dataset_3 = load_test_datasets()

    with context:
        with app.app.test_request_context(
            headers=badHeader.headers
        ):
            auth.access.create_access_handler()
            ah = auth.access.get_access_handler()
            res = ah.verify(dataset="TF4CN", level=4)
            assert res[0] == False
            assert res[1] == "Decode"


@patch('candig_cnv_service.api.auth.access.requests.Session.get', side_effect=mocked_authz)
def test_invalid_authz_level(mock_session, test_client):
    """
    Test access level verification
    """

    context = test_client
    dataset_1, dataset_2, dataset_3 = load_test_datasets()

    with context:
        with app.app.test_request_context(
            headers=goodHeader.headers
        ):
            auth.access.create_access_handler()
            ah = auth.access.get_access_handler()
            res = ah.verify(dataset="PROFYLE", level=4)
            assert res[0] == False
            assert res[1] == "Level"


@patch('candig_cnv_service.api.auth.access.requests.Session.get', side_effect=mocked_authz)
def test_get_samples(test_client):
    """
    Test 'get_samples' method
    """

    context = test_client

    sample_1, sample_2, _, dataset_1 = load_test_samples()
    sample_3, sample_4, _, dataset_2 = load_test_samples()

    with context:
        with app.app.test_request_context(
            headers=goodHeader.headers
        ):
            _, code = operations.add_datasets(dataset_1)
            assert code == 201
            _, code = operations.add_datasets(dataset_2)
            assert code == 201

            _, code = operations.add_samples(sample_1)
            assert code == 201
            _, code = operations.add_samples(sample_2)
            assert code == 201

            _, code = operations.add_samples(sample_3)
            assert code == 201
            _, code = operations.add_samples(sample_4)
            assert code == 201

            response, code = operations.get_samples(dataset_1["dataset_id"])
            samples = [s["sample_id"] for s in response["samples"]]
            descriptions = [s["description"] for s in response["samples"]]
            assert code == 200
            assert len(samples) == 1
            assert sample_1["sample_id"] in samples
            assert sample_1["description"] in descriptions


@patch('candig_cnv_service.api.auth.access.requests.Session.get', side_effect=mocked_authz)
def test_get_samples_using_description(test_client):
    """
    Test 'get_samples' method using a description
    """

    context = test_client

    sample_1, sample_2, _, dataset_1 = load_test_samples()
    sample_3, sample_4, _, dataset_2 = load_test_samples()

    with context:
        with app.app.test_request_context(
            headers=goodHeader.headers
        ):
            _, code = operations.add_datasets(dataset_1)
            assert code == 201
            _, code = operations.add_datasets(dataset_2)
            assert code == 201

            _, code = operations.add_samples(sample_1)
            assert code == 201
            _, code = operations.add_samples(sample_2)
            assert code == 201

            _, code = operations.add_samples(sample_3)
            assert code == 201
            _, code = operations.add_samples(sample_4)
            assert code == 201

            response, code = operations.get_samples(dataset_1["dataset_id"], description=sample_1["description"])
            assert code == 200
            assert response["dataset_id"] == sample_1["dataset_id"] 


@patch('candig_cnv_service.api.auth.access.requests.Session.get', side_effect=mocked_authz)
def test_get_samples_with_tags(test_client):
    """
    Test 'get_samples' using tags
    """
    context = test_client
    sample_1, sample_2, dataset_1 = load_test_samples_with_tags()
    dataset_id = dataset_1["dataset_id"]
    tags = sample_1["tags"]

    with context:
        with app.app.test_request_context(
            headers=goodHeader.headers
        ):
            _, code = operations.add_datasets(dataset_1)
            assert code == 201

            _, code = operations.add_samples(sample_1)
            assert code == 201
            _, code = operations.add_samples(sample_2)
            assert code == 201

            response, code = operations.get_samples(dataset_id, tags)
            assert code == 200
            assert response["dataset_id"] == dataset_id
            assert len(response["samples"]) == 1

            response, code = operations.get_samples(dataset_id, ["Canadian"])
            assert code == 200
            assert response["dataset_id"] == dataset_id
            assert len(response["samples"]) == 1

            response, code = operations.get_samples(
                dataset_id, ["Non existent tag"]
            )
            assert code == 200
            assert not response


@patch('candig_cnv_service.api.auth.access.requests.Session.get', side_effect=mocked_authz)
def test_get_segment_auth(test_client):
    """
    Test 'get_segments' method
    """

    context = test_client

    dataset_1, sample_1, segment_1, segment_2, segment_3 = load_test_segment()
    dataset_2, sample_2, segment_4, segment_5, segment_6 = load_test_segment()

    dataset_id = segment_1["dataset_id"]
    sample_id = segment_1["sample_id"]
    chromosome = segment_1["segments"][0]["chromosome"]
    start_position = segment_1["segments"][0]["start_position"]
    end_position = segment_1["segments"][0]["end_position"]
    copy_number = segment_1["segments"][0]["copy_number"]
    copy_number_ploidy_corrected = segment_1["segments"][0][
        "copy_number_ploidy_corrected"
    ]

    with context:
        with app.app.test_request_context(
            headers=goodHeader.headers
        ):
            response, code = operations.add_datasets(dataset_1)
            assert code == 201
            assert response["code"] == 201
            response, code = operations.add_datasets(dataset_2)
            assert code == 201
            assert response["code"] == 201

            response, code = operations.add_samples(sample_1)
            assert code == 201
            assert response["code"] == 201
            response, code = operations.add_samples(sample_2)
            assert code == 201
            assert response["code"] == 201

            response, code = operations.add_segments(segment_1)
            assert code == 201
            assert response["code"] == 201

            response, code = operations.add_segments(segment_2)
            assert code == 201
            assert response["code"] == 201

            response, code = operations.add_segments(segment_3)
            assert code == 201
            assert response["code"] == 201

            response, code = operations.add_segments(segment_4)
            assert code == 201
            assert response["code"] == 201

            response, code = operations.add_segments(segment_5)
            assert code == 201
            assert response["code"] == 201

            response, code = operations.add_segments(segment_6)
            assert code == 201
            assert response["code"] == 201

            response, code = operations.get_segments(
                dataset_id,
                sample_id,
                chromosome,
                start_position,
                end_position,
            )
            assert len(response) == 1
            assert code == 200

            assert response[0]["chromosome"] == chromosome
            assert response[0]["start_position"] == start_position
            assert response[0]["end_position"] == end_position
            assert response[0]["copy_number"] == copy_number
            assert (
                response[0]["copy_number_ploidy_corrected"]
                == copy_number_ploidy_corrected
            )

            response, code = operations.get_segments(
                dataset_id,
                sample_id,
                chromosome,
                start_position=12522,
                end_position=34326,
            )
            
            assert code == 200
            assert len(response) == 2


def load_test_datasets():
    """
    Load some mock dataset data
    """
    dataset_1_id = uuid.uuid4().hex
    dataset_2_id = uuid.uuid4().hex
    dataset_3_id = 1

    test_dataset_1 = {
        "dataset_id": dataset_1_id,
        "name": "TEST1"
    }

    test_dataset_2 = {
        "dataset_id": dataset_2_id,
        "name": "TEST2"
    }

    test_dataset_3 = {
        "dataset_id": dataset_3_id,
        "name": "TEST3"
    }

    return test_dataset_1, test_dataset_2, test_dataset_3


def load_test_samples():
    """
    Return some mock sample data
    """
    samp = lambda x: "".join(
        random.choice(string.ascii_lowercase) for i in range(x)
    )

    dataset_1, _, _ = load_test_datasets()

    sample_1 = {"sample_id": samp(5), "dataset_id": dataset_1["dataset_id"], "description": dataset_1["dataset_id"] + "sample_1", "access_level": 1}

    sample_2 = {"sample_id": samp(5), "dataset_id": dataset_1["dataset_id"], "description": dataset_1["dataset_id"] + "sample_2", "access_level": 2}

    sample_3 = {"sample_id": samp(5)}

    return sample_1, sample_2, sample_3, dataset_1


def load_test_samples_with_tags():
    """
    Return some mock sample data with tags
    """
    samp = lambda x: "".join(
        random.choice(string.ascii_lowercase) for i in range(x)
    )

    dataset_1, _, _ = load_test_datasets()

    sample_1 = {
        "sample_id": samp(5),
        "dataset_id": dataset_1["dataset_id"],
        "tags": ["Canadian", "Ovarian"],
        "description": "sample_1",
        "access_level": 1,
    }

    sample_2 = {
        "sample_id": samp(5),
        "dataset_id": dataset_1["dataset_id"],
        "tags": ["Canadian", "Liver", "Adult"],
        "description": "sample_2",
        "access_level": 2,
    }

    return sample_1, sample_2, dataset_1


def load_test_segment():
    """
    Return some mock segments data
    """

    sample_1, _, _, dataset_1 = load_test_samples()

    segment_1 = {
        "dataset_id": dataset_1["dataset_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome": "5",
                "start_position": 12523,
                "end_position": 23425,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    segment_2 = {
        "dataset_id": dataset_1["dataset_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome": "5",
                "start_position": 23426,
                "end_position": 34326,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    segment_3 = {
        "dataset_id": dataset_1["dataset_id"],
        "sample_id": sample_1["sample_id"],
        "segments": [
            {
                "chromosome": "5",
                "start_position": 34327,
                "end_position": 44296,
                "copy_number": -0.16,
                "copy_number_ploidy_corrected": 0,
            }
        ],
    }

    return dataset_1, sample_1, segment_1, segment_2, segment_3


