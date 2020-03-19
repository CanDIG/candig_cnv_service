import flask

from candig_cnv_service import orm
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

    report = typename + " search failed"
    message = "Internal error searching for {}s".format(typename)

    logger().error(struct_log(action=report, exception=str(exception), **kwargs))
    return dict(message=message, code=500)
    

def getPatients():
    """
    Return all individuals
    """
    try:
        q = Patient().query.all()
    except orm.ORMException as e:
        err = _report_search_failed("patient", e, patient_id="all")
        return err, 500

    return [orm.dump(p) for p in q], 200


def getSamples():
    return [], 200


def getSegment():
    return [], 200
