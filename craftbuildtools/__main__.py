#!/usr/bin/python3
import sys
from craftbuildtools import craftbuildtools
from craftbuildtools.craftbuildtools import parser, App


def main(args=None):
    """The main entry point for CraftBuildTools."""
    if args is None:
        args = sys.argv[1:]

    args = parser.parse_args()
    craftbuildtools.args = args
    app = App(args)
    app.run()


if __name__ == "__main__":
    main()
