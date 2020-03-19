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


def test_get_patient(test_client):
    context = test_client

    with context:
        result, code =  operations.getPatients()
        assert isinstance(result, list)
        assert code == 200

def test_get_samples(test_client):
    context = test_client

    with context:
        result, code = operations.getSamples()
        assert isinstance(result, list)
        assert code == 200

def test_get_segment(test_client):
    context = test_client

    with context:
        result, code = operations.getSegment()
        assert isinstance(result, list)
        assert code == 200   
