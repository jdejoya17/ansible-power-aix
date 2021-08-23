#!/usr/bin/env python
# Purpose: this will auto update the file version of the
# modules on this collection.
#
# For the official release of ibm.power_aix collection
# follows the versioning schema below:
#
# x.y.z
#
# x - increment major version number for an incompatible
#     API change
# y - increment minor version number for a new functionality
#     that is backwards compatible
# z - increment patch version number for backward compatible
#     bug fixes
#
# This script will:
# - add or update the file version on each module
# - will run per Pull Request
# - a github workflow will take care of running the auto
#   file versioning
# - you should not run this script manually
# - the individual file version schema is not the official
#   ansible collection version, this file version is only
#   really important to the developers to quickly tell if
#   the current module is the latest module
# - the file version schema follows:
#
# x.y.z.a
#
# a - increment changes version number for changes added
#     that is not currently officially publishe on an
#     official release

import glob
import os

# constants
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = SCRIPT_PATH.rsplit("/", 2)[0] + "/plugins/modules"


def main():
    modules_path = glob.glob(MODULE_DIR + "/*.py")

    print(SCRIPT_PATH)
    print(MODULE_DIR)
    print(modules)

    return


if __name__ == "__main__":
    main()

