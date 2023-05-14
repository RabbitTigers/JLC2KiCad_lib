import requests
import json
import logging
import argparse

from .__version__ import __version__
from . import helper
from .footprint.footprint import create_footprint, get_footprint_info
from .symbol.symbol import create_symbol


def add_component(component_id, args):
    logging.info(f"creating library for component {component_id}")
    data = json.loads(
        requests.get(
            f"https://easyeda.com/api/products/{component_id}/svgs"
        ).content.decode()
    )

    if not data["success"]:
        logging.error(
            f"failed to get component uuid for {component_id}\nThe component # is probably wrong. Check a possible typo and that the component exists on easyEDA"
        )
        return ()

    footprint_component_uuid = data["result"][-1]["component_uuid"]
    symbol_component_uuid = [i["component_uuid"] for i in data["result"][:-1]]

    if args.footprint_creation:
        footprint_name, datasheet_link = create_footprint(
            footprint_component_uuid=footprint_component_uuid,
            component_id=component_id,
            footprint_lib=args.footprint_lib,
            output_dir=args.output_dir,
            model_base_variable=args.model_base_variable,
            skip_existing=args.skip_existing,
        )
    else:
        _, datasheet_link, _, _ = get_footprint_info(footprint_component_uuid)
        footprint_name = ""

    if args.symbol_creation:
        create_symbol(
            symbol_component_uuid=symbol_component_uuid,
            footprint_name=footprint_name,
            datasheet_link=datasheet_link,
            library_name=args.symbol_lib,
            output_dir=args.output_dir,
            component_id=component_id,
            skip_existing=args.skip_existing,
        )


def main():
    parser = argparse.ArgumentParser(
        description="take a JLCPCB part # and create the according component's kicad's library",
        epilog="exemple use : \n	python3 JLC2KiCad_lib.py C1337258 C24112 -dir My_lib -symbol_lib My_Symbol_lib --no_footprint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "components",
        metavar="JLCPCB_part_#",
        type=str,
        nargs="+",
        help="list of JLCPCB part # from the components you want to create",
    )

    parser.add_argument(
        "-dir",
        dest="output_dir",
        type=str,
        default="JLC2KiCad_lib",
        help="base directory for output library files",
    )

    parser.add_argument(
        "--no_footprint",
        dest="footprint_creation",
        action="store_false",
        help="use --no_footprint if you do not want to create the footprint",
    )

    parser.add_argument(
        "--no_symbol",
        dest="symbol_creation",
        action="store_false",
        help="use --no_symbol if you do not want to create the symbol",
    )

    parser.add_argument(
        "-symbol_lib",
        dest="symbol_lib",
        type=str,
        default=None,
        help='set symbol library name, default is "default_lib"',
    )

    parser.add_argument(
        "-footprint_lib",
        dest="footprint_lib",
        type=str,
        default="footprint",
        help='set footprint library name,  default is "footprint"',
    )

    parser.add_argument(  # argument to skip already existing files and symbols
        "--skip_existing",
        dest="skip_existing",
        action="store_true",
        help="use --skip_existing if you want do not want to replace already existing footprints and symbols",
    )

    parser.add_argument(
        "-model_base_variable",
        dest="model_base_variable",
        type=str,
        default="",
        help="use -model_base_variable if you want to specifie the base path of the 3D model using a path variable",
    )

    parser.add_argument(
        "-logging_level",
        dest="logging_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="set logging level. If DEBUG is used, the debug logs are only written in the log file if the option  --log_file is set ",
    )

    parser.add_argument(
        "--log_file",
        dest="log_file",
        action="store_true",
        help="use --log_file if you want logs to be written in a file",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Print versin number and exit",
    )

    args = parser.parse_args()

    helper.set_logging(args.logging_level, args.log_file)

    for component in args.components:
        add_component(component, args)


if __name__ == "__main__":
    main()
