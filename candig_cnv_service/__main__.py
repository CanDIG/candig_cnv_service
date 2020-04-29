import sys
import os
import json
import argparse
import logging

import connexion

from tornado.options import define
import candig_cnv_service.orm
from candig_cnv_service.tools.parser import get_config_dict
import candig_cnv_service.api.auth as auth


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser("Run Candig CNV  service")
    parser.add_argument("--port", default=8880)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--database", default="./data/cnv_service.db")
    parser.add_argument("--logfile", default="./log/cnv_service.log")
    parser.add_argument("--services", default="./configs/services.json")
    parser.add_argument(
        "--loglevel",
        default="INFO",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )
    parser.add_argument("--name", default="candig_service")
    parser.add_argument("--noauth", default=False)

    args, _ = parser.parse_known_args()
    try:
        log_handler = logging.FileHandler(args.logfile)
    except FileNotFoundError:
        os.mkdir(os.getcwd()+"/log")
        log_handler = logging.FileHandler(args.logfile)

    numeric_loglevel = getattr(logging, args.loglevel.upper())
    log_handler.setLevel(numeric_loglevel)

    app.app.logger.addHandler(log_handler)
    app.app.logger.setLevel(numeric_loglevel)

    app.app.config["name"] = args.name
    app.app.config["self"] = "http://{}:{}".format(args.host, args.port)

    define("dbfile", default=args.database)
    candig_cnv_service.orm.init_db()
    db_session = candig_cnv_service.orm.get_session()

    app.app.config["auth_flag"] = args.noauth

    if not args.noauth:
        print("In auth")
        app.app.config.update(get_config_dict(args.services))
        print(app.app.config)
        #auth.create_kc_handler(app.app.config["keycloak"])
        #auth.access.create_access_handler()

    @app.app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app, args.port


def configure_app():
    app = connexion.FlaskApp(
        __name__, server="tornado", options={"swagger_url": "/"}
    )
    api_def = "./api/api_definition.yaml"

    app.add_api(api_def, strict_validation=True, validate_responses=True)

    @app.app.after_request
    def rewrite_bad_request(response):
        if (
            response.status_code == 400
            and response.data.decode("utf-8").find('"title":') != -1
        ):
            original = json.loads(response.data.decode("utf-8"))
            response.data = json.dumps(
                {"code": 400, "message": original["detail"]}
            )
            response.headers["Content-Type"] = "application/json"

        return response

    return app


app = configure_app()

application = app.app

if __name__ == "__main__":
    APPLICATION, PORT = main()
    APPLICATION.app.logger.info(
        "{} running at {}".format(
            APPLICATION.app.config["name"], APPLICATION.app.config["self"]
        )
    )
    APPLICATION.run(port=PORT)
