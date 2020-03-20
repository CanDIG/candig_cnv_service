import uuid
import pytest
import os
import sys

sys.path.append("{}/{}".format(os.getcwd(), "candig_cnv_service"))
sys.path.append(os.getcwd())

from candig_cnv_service import orm
from candig_cnv_service.__main__ import app
from candig_cnv_service.api import operations


@pytest.fixture(name="test_client")
def load_test_client(db_filename="operations.db"):
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

    return context


def test_add_patients(test_client):
    """
    Test add_patients method
    """

    context = test_client
    patient_1, patient_2, patient_3 = load_test_patients()
    
    with context:
        response, code = operations.add_patients(patient_1)
        assert code == 201
        assert response["code"] == 201

        response, code = operations.add_patients(patient_2)
        assert code == 201
        assert response["code"] == 201
        
        # Invalid 'patient_id'
        response, code = operations.add_patients(patient_3)
        assert code == 500
        assert response["code"] == 500


def test_add_same_patient(test_client):
    """
    Test adding same patient twice 
    """
    context  = test_client
    patient_1, _, _ = load_test_patients()

    with context:
        response, code = operations.add_patients(patient_1)
        assert code == 201
        assert response["code"] == 201
        response, code = operations.add_patients(patient_1)
        assert code == 400
        assert response["code"] == 400


def test_get_patient(test_client):
    """
    Test 'get_patient' method 
    """
    context = test_client
    patient_1, patient_2, _ = load_test_patients()

    with context:
        operations.add_patients(patient_1)
        operations.add_patients(patient_2)
        result, code =  operations.get_patients()
        assert len(result) == 2
        assert code == 200

def test_add_samples(test_client):
    """
    Test 'add_samples' method
    """
    context = test_client
    sample_1, sample_2, _,  patient_1 = load_test_samples()

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201

        response, code = operations.add_samples(sample_1)
        assert code == 201
        assert response["code"] == 201
         

def test_add_sample_twice(test_client):
    """
    Test adding the same sample twice
    """
    context = test_client
    sample_1, _, _, patient_1 = load_test_samples()

    with context:
        _, code = operations.add_patients(patient_1)
        assert code == 201

        response, code = operations.add_samples(sample_1)
        assert code == 201
        assert response["code"] == 201
        
        response, code = operations.add_samples(sample_1)
        assert code == 400
        assert response["code"] == 400

def test_add_sample_no_patient(test_client):
    """
    Test adding sample where no patient information 
    is present on patient table 
    """
    
    context = test_client
    _, _, sample, _ = load_test_samples()

    with context:
        response, code = operations.add_samples(sample)
        assert code == 400
        assert response["code"] == 400
        

def test_get_samples(test_client):
    """
    Test 'get_samples' method
    """

    context = test_client

    with context:
        result, code = operations.get_samples()
        assert len(result) == 0 
        assert code == 200

def test_get_segment(test_client):
    """
    Test 'get_segments' method
    """
    context  = test_client

    with context:
        result, code = operations.get_segments()
        assert len(result) == 0 
        assert code == 200
      

def load_test_patients():
    """
    Load some mock patient data
    """
    patient_1_id = uuid.uuid4().hex
    patient_2_id = uuid.uuid4().hex
    patient_3_id = 1

    test_patient_1 = {
        "patient_id":patient_1_id,
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

    patient_1, _, _  = load_test_patients()

    sample_1 = {
        "sample_id": "1",
        "patient_id": patient_1["patient_id"]
    }

    sample_2 = {
        "sample_id": "2",
        "patient_id": patient_1["patient_id"]
    }

    sample_3 = {
        "sample_id": "3"
    }



    return sample_1, sample_2, sample_3, patient_1
