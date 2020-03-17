import flask

from candig_cnv_service.orm import get_session

APP = flask.current_app


def getPatients():
    return [], 200


def getSamples():
    return [], 200


def getSegment():
    return [], 200
