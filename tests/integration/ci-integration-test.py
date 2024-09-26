#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020- IBM, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import sys
import glob
import yaml
import argparse
import ansible_runner
import re


# escape sequence
class fg:
    BLACK = '\033[0;30m'
    RED = '\033[0;31m' #'\033[31m'
    GREEN = '\033[0;32m' #'\033[32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[1;34m'
    PURPLE = '\033[1;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    RESET = '\033[39m'
    NC = '\033[0m'


class style:
    BOLD = '\033[1m'
    RESET_ALL = '\033[0m'
    END = '\033[22m'
    UNDERLINE = '\033[04m'


class Global():
    def __init__(self):
        # command handlers
        self.cmd = None
        self.bucket_cmd = None
        self.test_cmd = None

        # bucket info
        self.bucket = None
        self.bucket_list = None
        self.bl_path = None

        # test info
        self.test = None
        self.test_list = None
        self.tl_path = None

        runner_dir = os.path.dirname(os.path.abspath(__file__))
        # directory locations
        self.top_dir = runner_dir.rsplit("/", 2)[0]
        self.target_dir = runner_dir + "/target"
        self.inventory = runner_dir + "/inventory"

        # report
        self.report = dict()

        # when a single integration test, stop all tests in
        # queue, as the first failed test may result in an
        # uncleaned environment that may cause the other test
        # to fail when it would not otherwise with a fresh
        # environment
        self.skip_test = False


g = Global()

#######################################################################
## Report Function
#######################################################################
def line_filler(text):
    max_char = 50
    num_char = len(text)
    line_char = max_char - num_char
    if line_char % 2 == 1:
        line_char -= 1

    LEFT = ""
    RIGHT = ""
    for i in range(0, int(line_char / 2)):
        LEFT += "="
        RIGHT += "="

    text = LEFT + text + RIGHT
    if len(text) != max_char:
        RIGHT += "="

    return LEFT, RIGHT


def print_report():
    """
    Print integration test result.
    """
    global g

    TEXT = "SUMMARY"
    LEFT, RIGHT = line_filler(TEXT)
    print(LEFT + style.BOLD + fg.GREEN + TEXT + fg.NC +
          style.END + RIGHT + style.RESET_ALL + "\n")

    # failed_tests = dict()
    num_passed = 0
    num_skipped = 0
    num_failed = 0
    failed_bucket = ""
    failed_test = ""
    buckets = g.report.keys()
    for bucket in buckets:
        tests = g.report[bucket].keys()
        for test in tests:
            status = g.report[bucket][test]['status']
            if status == "PASSED":
                STATUS = fg.GREEN
                num_passed += 1
            elif status == "SKIPPED":
                STATUS = fg.CYAN
                num_skipped += 1
            elif status == "FAILED":
                STATUS = fg.RED
                num_failed += 1
                failed_bucket = bucket
                failed_test = test
            else:
                raise Exception("UNKNOWN STATUS")
                
            STATUS += status + fg.NC
            BUCKET = " [ " + fg.PURPLE + bucket + fg.NC + " ] "
            print("-> " + STATUS + BUCKET + test + "\n")

    PASSED = str(num_passed) + " passed"
    SKIPPED = str(num_skipped) + " skipped"
    FAILED = str(num_failed) + " failed"
    LEFT, RIGHT = line_filler(PASSED + ", " + SKIPPED + ", " + FAILED)

    PASSED = fg.GREEN + PASSED + fg.NC
    SKIPPED = fg.CYAN + SKIPPED + fg.NC
    FAILED = fg.RED + FAILED + fg.NC
    print(LEFT + PASSED + ", " + SKIPPED + ", " + FAILED + RIGHT + "\n") 

    # warn user to go reset the victim as a test have failed
    # and the victim is now in need of a cleanup
    if num_failed != 0 or num_skipped != 0:
        print(fg.YELLOW + "IMPORTANT:" + fg.NC)
        if num_skipped != 0:
            MSG = "Tests are " + fg.CYAN + "SKIPPED" + fg.NC + " because one of "
            MSG += "the tests " + fg.RED + "FAILED" + fg.NC
            print("-> " + MSG)
        if num_failed != 0:
            MSG = "The test [ " + fg.BLUE + failed_test + fg.NC + " ]"
            MSG += " from test bucket [ " + fg.PURPLE + failed_bucket + fg.NC + " ]"
            MSG += " has " + fg.RED + "FAILED" + fg.NC
            print("-> " + MSG)

            MSG = "PLEASE check the victim machine used for the integrationd\n"
            MSG += "test to see if it needs any cleanup because of the "
            MSG += fg.RED + "FAILED" + fg.NC + " test"
            print("-> " + MSG)



######################################################################
# Helper Functions
######################################################################
def get_args():
    global g

    # main level parser
    parser = argparse.ArgumentParser(
        prog="integration-test-runner",
        description="TEMPORARY integration test runner"
    )

    # add subparser
    cmd_parser = parser.add_subparsers(
        title="commands",
        help="list of commands",
        dest="cmd"
    )

    # bucket parser
    bucket_parser = cmd_parser.add_parser(
        "bucket",
        help="runs a test bucket",
        description="runs all tests in the targeted bucket"
    )

    # bucket subparser
    bucket_subparser = bucket_parser.add_subparsers(
        title="bucket commands",
        help="list of bucket subcommands",
        dest="bucket_cmd"
    )

    # run test bucket
    bucket_run_parser = bucket_subparser.add_parser(
        "run",
        help="run all tests in the target bucket",
        description="run all tests in the a bucket"
    )
    bucket_run_parser.add_argument(
        "target_bucket",
        help="name of test bucket",
        nargs='*'
    )

    # list test bucket
    bucket_list_parser = bucket_subparser.add_parser(
        "list",
        help="list all target buckets",
        description="list all valid target buckets"
    )
    bucket_list_parser.add_argument(
        "target_bucket",
        help="name of test bucket",
        nargs='*',
        default=None
    )
   
    # individual test runner
    test_parser = cmd_parser.add_parser(
        "test",
        help="runs an individual test",
        description="runs an individual targeted test"
    )

    # test subparser
    test_subparser = test_parser.add_subparsers(
        title="test commands",
        help="list of test subcommands",
        dest="test_cmd"
    )

    # run test
    test_run_parser = test_subparser.add_parser(
        "run",
        help="run all specified tests",
        description="run all specified tests, multiple tests can be entered"
    )
    test_run_parser.add_argument(
        "target_test",
        help="name of test",
        nargs='*'
    )

    # list all tests or all tests in a bucket
    test_list_parser = test_subparser.add_parser(
        "list",
        help="list tests",
        description="list all tests or only the tests in a specified bucket"
    )
    bucket_list_parser.add_argument(
        "target_bucket",
        help="name of test bucket",
        nargs='*',
        default=None
    )

    # parse arguments
    args = parser.parse_args()
    print(args)

    if args.cmd == None:
        parser.print_help()
        return

    elif args.cmd == "bucket":
        if args.bucket_cmd == None:
            bucket_parser.print_help()
        else:
            g.bucket_cmd = args.bucket_cmd
            g.bucket = args.target_bucket

    elif args.cmd == "test":
        if args.test_cmd == None:
            test_parser.print_help()
        else:
            g.test_cmd = args.test_cmd
            g.test = args.target_test

    g.cmd = args.cmd
    return


def get_bucket_list():
    """
    Fetch all the bucket names located in tests/integration/target
    """
    global g

    bl_path = glob.glob(g.target_dir + "/*")
    bucket_list = [ path.rsplit("/", 1)[-1] for path in bl_path]
    return (bucket_list, bl_path)


def get_test_list(bucket):
    """
    Fetch all the tests in the specified test bucket.
    """
    global g

    tl_path = glob.glob(g.target_dir + "/%s/tasks/*" % bucket)
    test_list = [ path.rsplit("/", 1)[-1] for path in tl_path]
    test_list = [ test.split(".")[0] for test in test_list ]
    return (test_list, tl_path)


def check_valid_buckets(buckets):
    """
    Check if the specified test bucket name(s) are valid.
    """
    bucket_list, _ = get_bucket_list()
    for bucket in buckets:
        if bucket not in bucket_list:
            print("Invalid test bucket name: %s" % bucket)
            exit()


def print_list(lst, indent=0):
    """
    Print each item on a list per line.
    """
    space = ""
    for i in range(0, indent):
        space += " "
    for item in lst:
        if indent:
            item = space + item
        print(item)


######################################################################
# Action Handler Functions
######################################################################
def run_test_bucket(specified_tests=None):
    """
    Run all integration tests on the test bucket(s)
    """
    global g


    # if tests are specified, fetch all the buckets
    # so we can go through each one and find the specified
    # tests
    if specified_tests is not None:
        buckets, _ = get_bucket_list()
    else:
        buckets = g.bucket

    # check if all target test buckets are valid
    check_valid_buckets(buckets)

    # run through each test bucket
    for bucket in buckets:
        g.report[bucket] = dict()

        # run through each test in the bucket
        test_list, tl_path = get_test_list(bucket)
        for test, path in zip(test_list, tl_path):
                
            # if individual tests are specified, run only those
            if specified_tests is not None and \
                    test not in specified_tests:
                continue

            g.report[bucket][test] = dict()

            # if a single test already failed, skip the rest
            if g.skip_test:
                g.report[bucket][test]['status'] = "SKIPPED"
                continue

            # run playbook - first run
            results = ansible_runner.interface.run(
                playbook=path,
                inventory=g.inventory
            )
            first_run_succeeded = True if results.stats['failures'] == {} else False

            # run playbook - second run for idempotency
            results = ansible_runner.interface.run(
                playbook=path,
                inventory=g.inventory
            )
            second_run_succeeded = True if results.stats['failures'] == {} else False

            if first_run_succeeded and second_run_succeeded:
                overall = "PASSED"
            else:
                overall = "FAILED"
                g.skip_test = True
            g.report[bucket][test]['status'] = overall


def print_bucket_list():
    """
    Print all valid test bucket names.
    """
    global g

    buckets = g.bucket
    if len(buckets) == 0:
        bucket_list, _ = get_bucket_list()
        print("list of valid test buckets:")
        if len(bucket_list) == 0:
            print("  no available test bucket")
            return
        print_list(bucket_list, indent=2)
    else:
        check_valid_buckets(buckets)
        for bucket in buckets:
            test_list, _ = get_test_list(bucket)
            print("list of test cases in %s bucket" % bucket)
            if len(test_list) == 0:
                print("  test bucket is empty")
            else:
                print_list(test_list, indent=2)


def run_test():
    """
    Run specified list of tests
    """
    tests = g.test
    run_test_bucket(specified_tests=tests)


def print_test_list():
    pass


######################################################################
# Main Function
######################################################################
def main():
    global g
    should_report = False
    
    # parse arguments
    get_args()


    # action handler
    if g.cmd == "all":
        pass
    elif g.cmd == "bucket":
        if g.bucket_cmd == "run":
            run_test_bucket()
            should_report = True
        elif g.bucket_cmd == "list":
            print_bucket_list()
    elif g.cmd == "test":
        if g.test_cmd == "run":
            run_test()
            should_report = True
        elif g.test_cmd == "list":
            print_test_list(bucket)

    if should_report:
        print_report()


if __name__ == "__main__":
    main()
