"""This module implements functions that handle the command line interface of the program."""
import argparse
import logging
from argparse import Namespace


# Get Arguments from Commandline
def get_args() -> Namespace:
    """Creates and configures an argparser for the command line interface and returns the arguments given by the user as a dictionary.

    Returns:
        Namespace: The arguments given in the command line.

    """
    # Get argparser
    argparser = argparse.ArgumentParser(
        prog="inventurgui",
        description="A web app to display the content of an .ods (Libre Office Calc) file in a nice way.",
    )
    # Add arguments to argparser
    argparser.add_argument("-c", dest="config_file", help="specify path to config, defaults to config.yml")
    argparser.add_argument("-r", "--reload", dest="reload", help="enable reloader", action="store_true")
    argparser.add_argument("-ld", "--debug", dest="debug", help="set the log level to debug", action="store_true")
    argparser.add_argument("-d", "--dev", dest="dev", help="mark that you are developing", action="store_true")
    argparser.add_argument("-i", "--images", dest="images", help="reload all images from their source url", action="store_true")
    argparser.add_argument("-nn", "--no-nextcloud", dest="no_nextcloud", help="don't attempt to fetch data from nextcloud", action="store_true")

    argparser.set_defaults(config_file="config.yml")
    # Parse args to dictionary
    args: Namespace = argparser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.debug(f"Args: {args}")
    return args  # Return Args


ARGS = get_args()
