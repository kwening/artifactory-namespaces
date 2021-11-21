import sys
import logging

from lib import namespaces
from lib import helper

__author__ = "Klaus Wening"
__copyright__ = "Klaus Wening"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def main(args):
    """Wrapper allowing :func:`apply_config` to be called with string arguments in a CLI fashion

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    config = helper.parse_args(args)
    helper.setup_logging(config.loglevel)
    namespaces.read_namespaces(config)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
