import sys
import os
import argparse
import textwrap

from sqlalchemy.exc import IntegrityError

from ingester import Ingester_CNV, Ingester
from parser import get_config_dict
from candig_cnv_service.api.exceptions import FileTypeError



def main(args=None):
    """
    Main script for ingesting CNV files through the CLI. Call this script
    along with all the arguments needed, depending on the mode.
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        "Run Candig CNV Ingest Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
            File Formatting:
                Mode 1: JSON containing datasets to ingest
                Mode 2: JSON containing samples to ingest
                Mode 3: TSV/CSV containing samples to ingest
        '''))
    parser.add_argument("--dataset", help="Dataset UUID")
    parser.add_argument("--sample", help="Sample ID", )
    parser.add_argument("file", help="Location of ingest file")
    parser.add_argument(
        "--database",
        help="Location of database",
        default=os.getcwd()+"/data/cnv_service.db"
        )
    parser.add_argument(
        "--sequential",
        help="Enables sequential uploading on ingest failure",
        default=False
        )
    parser.add_argument(
        "--mode",
        help=textwrap.dedent('''\
            Ingest Mode:
            1 - Add Dataset. File param required.
            2 - Add Sample. Dataset/File params required.
            3 - Add CNV. Dataset/Sample/File params required.
        '''),
        default=1,
        type=int,
        choices=[1, 2, 3]
    )
    args, _ = parser.parse_known_args()

    if args.mode == 1:
        config = get_config_dict("./configs/services.json")
        dss = config["candig_services"]["datasets"]
        ingest = Ingester(
            database=args.database,
            datafile=args.file,
            dss=dss)
        ingest.dataset_protocol()

    elif args.mode == 2:
        config = get_config_dict("./configs/services.json")
        dss = config["candig_services"]["datasets"]
        ingest = Ingester(
            database=args.database,
            datafile=args.file,
            dss=dss)
        ingest.sample_protocol()
    elif args.mode == 3:
        try:
            CNV = Ingester_CNV(
                database=args.database,
                dataset=args.dataset,
                sample=args.sample,
                cnv_file=args.file
                )
        except FileTypeError as FTE:
            print(FTE.args[0])
            quit()
        except TypeError:
            print("Invalid DB location")
            quit()

        try:
            CNV.upload()
        except IntegrityError as IE:
            print(IE.args)
            if args.sequential:
                print("Running Sequential Upload")
                CNV.upload_sequential()


if __name__ == "__main__":
    main()
