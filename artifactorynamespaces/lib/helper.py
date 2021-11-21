import argparse
import logging
import os
import sys
from dataclasses import dataclass

import yaml


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Artifactory namespaces automation")

    parser.add_argument(
        '-q',
        '--quiet',
        dest='loglevel',
        action='store_const',
        default=logging.INFO,
        const=logging.ERROR,
        help='quiet logging')
    parser.add_argument(
        '-v',
        '--verbose',
        dest='loglevel',
        action='store_const',
        default=logging.INFO,
        const=logging.DEBUG,
        help='verbose logging')

    parser.add_argument(
        "-n",
        "--namespaces-file",
        dest="namespaces_file",
        default=os.getenv("NAMESPACES_FILE", ""),
        help="path to namespaces yaml file",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default=os.getenv("OUTPUT_DIR", ""),
        help="target directory for generated files",
    )
    parser.add_argument(
        "-c",
        "--config-file",
        dest="config_file",
        default=os.getenv("CONFIG_FILE", ""),
        help="configuration yaml file",
    )

    args = parser.parse_args(args)

    if not args.namespaces_file or not args.config_file:
        sys.exit(parser.print_usage())

    args.output_dir = args.output_dir.rstrip(os.sep)

    config = Config()

    if args.config_file:
        config.from_yaml(args.config_file)

    # Override yaml settings with cli args or ENV
    config.from_args(args.__dict__)

    return config


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


@dataclass
class Config:
    """Class holds configuration settings defined by config yaml file or cli arguments
    """
    namespaces_file: str = ""
    internal_repos: list = None
    thirdparty_repos: list = None
    internal_users: list = None
    public_users: list = None
    internal_groups: list = None
    public_groups: list = None
    output_dir: str = "out"
    output_format: str = "json"
    loglevel: int = ""

    def __init__(self, initial_data=None):
        if initial_data is None:
            initial_data = {}

        for key in initial_data:
            if key == "repos":
                self.internal_repos = as_list(initial_data[key].get('internal', None))
                self.thirdparty_repos = as_list(initial_data[key].get('thirdparty', None))
            if key == "users":
                self.public_users = as_list(initial_data[key].get('public', None))
                self.internal_users = as_list(initial_data[key].get('internal', None))
            if key == "groups":
                self.public_groups = as_list(initial_data[key].get('public', None))
                self.internal_groups = as_list(initial_data[key].get('internal', None))
            else:
                setattr(self, key, initial_data[key])

        self.output_dir = self.output_dir + '/' if not self.output_dir.endswith('/') else self.output_dir

    def from_yaml(self, config_file: str):
        if not os.path.isfile(config_file):
            print(f"Config file '{config_file}' doesn't exist")
            sys.exit(0)

        with open(config_file) as yaml_file:
            yaml_config = yaml.safe_load(yaml_file)
            self.__init__(yaml_config)

    def from_args(self, args: dict):
        self.__init__({k: v for k, v in args.items() if not v == ""})


def as_list(value):
    if value is None:
        return []
    elif isinstance(value, list):
        return value
    elif isinstance(value, str):
        return value.split(',')
