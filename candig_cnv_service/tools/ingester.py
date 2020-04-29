"""
The ingester module provides methods to ingest entire CNV files
"""

import os
import sys
import json
import datetime

import requests
from sqlalchemy.exc import IntegrityError

sys.path.append(os.getcwd())

from candig_cnv_service.api.exceptions import FileTypeError  # noqa: E402
from candig_cnv_service.api.exceptions import KeyExistenceError  # noqa: E402
from candig_cnv_service.api.exceptions import HeaderError  # noqa: E402
from candig_cnv_service.orm import init_db, get_engine  # noqa: E402
from candig_cnv_service.orm.models import CNV, Sample, Dataset  # noqa: E402
from candig_cnv_service import orm

class Ingester_CNV:
    """
    This is a collection of methods to facilitate ingesting entire CNV files

    :param database: Location of the database to ingest the CNV file
    :type database: str
    :param dataset: Dataset ID that the CNV file belongs to
    :type dataset: UUID
    :param sample: Sample ID that the CNV file belongs to
    :type sample: str
    :param cnv_file: Location of the CNV file to ingest
    :type cnv_file: str
    """
    def __init__(self, database, dataset, sample, cnv_file):
        """Constructor method
        """
        self.db = "sqlite:///" + database
        self.dataset = dataset.replace("-", "")
        self.sample = sample
        self.cnv_file = cnv_file
        self.file_type = self.get_type()
        self.engine = self.db_setup()
        self.segments = []
        self.required_headers = [
            'chromsome',
            'start_position',
            'end_position',
            'copy_number',
            'copy_number_ploidy_corrected'
            ]
        self.ingests = {
            "csv": self.ingest_csv,
            "tsv": self.ingest_tsv
        }

    def get_type(self):
        """
        Searches the given cnv_file and returns the type if valid (csv or tsv)

        :raises: FileTypeError
        :return: csv or tsv
        :rtype: str

        """
        if (self.cnv_file.find(".csv") != -1):
            return "csv"
        elif (self.cnv_file.find(".tsv") != -1):
            return "tsv"
        # elif (self.cnv_file.find(".txt") != -1):
        #     return "txt"

        raise FileTypeError(self.cnv_file)

    def db_setup(self):
        """
        Connects to the database given using SQLAlchemy Core and
        attempts to query the Sample ID provided. Returns the
        engine if successful or an error if the Sample cannot
        be located.

        :raises: KeyExistenceError
        :return: engine object
        :rtype: `~sqlalchemy.engine.Engine`
        """
        init_db(self.db)
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(
                "select * from sample where sample_id=\"{}\""
                .format(self.sample)).first()
            if self.dataset != result[1]:
                raise KeyExistenceError(self.sample)
        return engine

    def ingest_tsv(self):
        """
        Ingests the provided CNV file as a .tsv and
        appends each row to be uploaded. If the file
        does not have the headers contained in self.headers,
        a HeaderError will be raised.

        :raises: HeaderError
        :return: None
        """
        with open(self.cnv_file) as cnv:
            header = cnv.readline()
            stripped = header.strip("\n").split("\t")
            if not stripped == self.required_headers:
                raise HeaderError(self.required_headers)
            for line in cnv:
                data = line.strip("\n").split("\t")
                segment = dict(zip(self.required_headers, data))
                segment['sample_id'] = self.sample
                self.segments.append(segment)

    def ingest_csv(self):
        """
        Ingests the provided CNV file as a .csv and
        appends each row to be uploaded. If the file
        does not have the headers contained in self.headers,
        a HeaderError will be raised.

        :raises: HeaderError
        :return: None
        """
        with open(self.cnv_file) as cnv:
            header = cnv.readline()
            stripped = header.strip("\n").split(",")
            if not stripped == self.required_headers:
                raise HeaderError(self.required_headers)
            for line in cnv:
                data = line.strip("\n").split(",")
                segment = dict(zip(self.required_headers, data))
                segment['sample_id'] = self.sample
                self.segments.append(segment)

    def upload(self):
        """
        Uploads the collected CNV data using SQLAlchemy Core
        functions to mass ingest the data.

        :raises: IntegrityError
        :return
        """
        self.ingests[self.file_type]()
        with self.engine.connect() as connection:
            connection.execute(
                CNV.__table__.insert(),
                self.segments
            )

    def upload_sequential(self):
        """
        Attempts to upload the CNV data in a sequential
        manner rather than a single upload. This allows
        for a partial ingest as well as error checking
        for each row.

        Should only be called if an integrity error
        in upload() is encountered and --sequential is
        set to true
        """
        with self.engine.connect() as connection:
            for segment in self.segments:
                try:
                    connection.execute(
                        CNV.__table__.insert(),
                        segment
                    )
                except IntegrityError as IE:
                    print(IE.args, IE.params)


class Ingester:
    """
    This is a collection of methods to facilitate ingesting data files
    to add Datasets or Samples to the CNV service.

    :param database: Location of the database to ingest the data file
    :type database: str
    :param datafile: Location of the data file to ingest
    :type datafile: str
    :param dss: Address of local CanDIG Datasets Service
    :type dss: str

    """

    def __init__(self, database, datafile, dss):
        """Constructor method
        """
        self.db = "sqlite:///" + database
        self.df = datafile
        self.dss = dss
        self.data = []

    def read_data(self, mode):
        with open(self.df) as ds:
            data = json.load(ds)
            self.data.extend(data[mode])



    def verify_datasets(self):

        dataset_ids = self.data
        url = "http://{}/v2/datasets/verify".format(self.dss)
        args = {"datasets": dataset_ids}
        request_handle = requests.Session()
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "content-type": "application/json",
            "federation": "false",
            "Authorization": "Bearer " + "iZTFhLTRiZDItODdk"
            }

        try:
            resp = request_handle.post("{}".format(url), headers=headers, json=args)
            verified = resp.json()

            if len(verified) != len(dataset_ids):
                print(
                    "Not able to verify all datasets.\n"
                    "Verfied and Adding: {}".format(verified)
                )

            verified_datasets = []
            for v in verified:
                for dataset in dataset_ids:
                    if dataset["dataset_id"] == v:
                        verified_datasets.append(dataset)
            
            return verified_datasets
        except requests.exceptions.ConnectionError:
            print(
                "Cannot establish connection to local Dataset service at "
                "{}.\nMake sure it is operational and try again.".
                format(url)
            )
            quit()
        except json.JSONDecodeError:
            print(resp.status_code, resp.text)

    def add_samples(self):
        orm.init_db(self.db)
        session = orm.get_session()
        try:
            session.bulk_save_objects(
                [
                    Sample(
                        dataset_id=sample["dataset_id"],
                        sample_id=sample["sample_id"],
                        access_level=sample["access_level"],
                        description=sample["description"],
                        created=datetime.datetime.utcnow()
                    )
                    for sample in self.data
                ],
            )
            session.commit()
        except IntegrityError as IE:
            print(IE.args, IE.params)

    def add_datasets(self, datasets):
        orm.init_db(self.db)
        session = orm.get_session()
        try:
            session.bulk_save_objects(
                [
                    Dataset(
                        dataset_id=dataset["dataset_id"],
                        name=dataset["name"],
                    )
                    for dataset in datasets
                ],
            )
            session.commit()
        except IntegrityError as IE:
            print(IE.args, IE.params)


    def dataset_protocol(self):
        self.read_data("datasets")
        v = self.verify_datasets()
        self.add_datasets(v)

    def sample_protocol(self):
        self.read_data("samples")
        self.add_samples()