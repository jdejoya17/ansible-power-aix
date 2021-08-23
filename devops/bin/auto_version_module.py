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
import argparse
import re

# constants
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = SCRIPT_PATH.rsplit("/", 2)[0] + "/plugins/modules"

# global variable class
class Global():
    def __init__(self):
        self.module_list = None

# initialize global variable
g = Global()


def get_args():
    parser = argparse.ArgumentParser(prog='auto_version_module')
    parser.add_argument('file_list')
    args = parser.parse_args()
    
    module_list = args.file_list

    return module_list

def main():
    filename = get_args()
    major = "1"
    minor = "3"
    patch = "1"
  
    # version only module files
    dirs = filename.split("/")
    if (len(dirs) != 3) or (dirs[0] != "plugins") or (dirs[1] != "modules"):
        return

    # read lines
    with open(filename, "r") as f:
        lines = f.readlines()
        # third line is where the file version should be
        file_version_line = lines[2]
        pattern = r"(for dev use only)"
        found = re.search(pattern, file_version_line)
        # print([file_version_line, type(file_version_line), pattern, found])
        if found:
            print("has file version")
            pattern = r"(\d+?)\.(\d+?)\.(\d+?)\.(\d+?)"
            file_version = re.search(pattern, file_version_line)
            major = file_version.group(1)
            minor = file_version.group(2)
            patch = file_version.group(3)
            change = file_version.group(4)
            new_file_version = major + "."
            new_file_version += minor + "."
            new_file_version += patch + "."
            new_file_version += str(int(change)+1)
            lines[2] = re.sub(pattern, new_file_version, file_version_line)
            print(lines[2])
        else:
            print("needs file version")
            version_eyecatcher = "# (for dev use only) {0} ".format("module")
            version_eyecatcher += "file version: {0}.{1}.{2}.0".format(
                major, minor, patch
            )
            print(version_eyecatcher)
        print(filename)

        # edit file

    return


if __name__ == "__main__":
    main()
