"""
Methods to handle incoming CNV service requests
"""

import flask

from sqlalchemy import exc

from candig_cnv_service.orm import get_session, ORMException, dump
from candig_cnv_service.orm.models import Patient
from candig_cnv_service.api.logging import apilog, logger
from candig_cnv_service.api.logging import structured_log as struct_log

APP = flask.current_app

def _report_search_failed(typename, exception, **kwargs):
    """
    Generate standard log message + request error for error:
    Internal error performing search
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + ' search failed'
    message = 'Internal error searching for '+typename+'s'
    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    return dict(message=message, code=500)


def _report_object_exists(typename, **kwargs):
    """
    Generate standard log message + request error for warning:
    Trying to POST an object that already exists
    :param typename: name of type involved
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + ' already exists'
    logger().warning(struct_log(action=report, **kwargs))
    return dict(message=report, code=405)


def _report_update_failed(typename, exception, **kwargs):
    """
    Generate standard log message + request error for error:
    Internal error performing update (PUT)
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = typename + ' updated failed'
    message = 'Internal error updating '+typename+'s'
    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    return dict(message=message, code=500)


def _report_conversion_error(typename, exception, **kwargs):
    """
    Generate standard log message + request error for warning:
    Trying to POST an object that already exists
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = 'Could not convert '+typename+' to ORM model'
    message = typename + ': failed validation - could not convert to internal representation'
    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    return dict(message=message, code=400)


def _report_write_error(typename, exception, **kwargs):
    """
    Generate standard log message + request error for error:
    Error writing to DB
    :param typename: name of type involved
    :param exception: exception thrown by ORM
    :param **kwargs: arbitrary keyword parameters
    :return: Connexion Error() type to return
    """
    report = 'Internal error writing '+typename+' to DB'
    message = typename + ': internal error saving ORM object to DB'
    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    err = dict(message=message, code=500)
    return err


def getPatients():
    return [], 200


def getSamples():
    return [], 200


def getSegment():
    return [], 200

@apilog
def addPatients(body):
    """
    Creates a new patient following the Patient
    schema defined in datasets.yaml


    :param body: POST request body
    :type body: object

    :returns: message, 201 on success, error code on failure
    :rtype: object, int 

    .. note::
        Refer to the OpenAPI Spec for a proper schemas of dataset_ingest and dataset objects.

    """

    db_session = get_session()

    if not body.get('samples'):
        # No Samples

        try:
            orm_patient = Patient(patient_id=body.get('patientID'))
        except TypeError as e:
            err = _report_conversion_error('patient', e, **body)
            return err, 400
        
        try:
            db_session.add(orm_patient)
            db_session.commit()
        except exc.IntegrityError:
            db_session.rollback()
            err = _report_object_exists('patient: ' + body['patientID'], **body)
            return err, 405
        except ORMException as e:
            db_session.rollback()
            err = _report_write_error('patient', e, **body)
            return err, 500
        
        return {"code": 201, "message": "Patient successfully added"}, 201
    
    return [], 200

def addSamples(body):
    return [], 200

def addCNV(body):
    return [], 200

