# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import logging
import sys

import os_client_config
import pkg_resources
import shade

from downpour import export
from downpour import query


def main():
    parser = argparse.ArgumentParser()
    config = os_client_config.OpenStackConfig()

    version_info = pkg_resources.get_distribution('os-downpour').version
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s ' + version_info,
        help='show the program version and exit',
    )

    verbose_group = parser.add_mutually_exclusive_group()
    verbose_group.add_argument(
        '--verbose', '-v',
        action='count',
        dest='verbose_level',
        default=1,
        help='Increase verbosity of output. Can be repeated.',
    )
    verbose_group.add_argument(
        '-q', '--quiet',
        action='store_const',
        dest='verbose_level',
        const=0,
        help='Suppress output except warnings and errors.',
    )
    progress_group = parser.add_mutually_exclusive_group()
    progress_group.add_argument(
        '--progress', '-p',
        default=True,
        action='store_true',
        help='show download progress',
    )
    progress_group.add_argument(
        '--no-progress',
        dest='progress',
        action='store_false',
        help='do not show download progress',
    )

    config.register_argparse_arguments(parser, sys.argv, None)
    subparsers = parser.add_subparsers(title='commands')

    export.register_command(subparsers)
    query.register_command(subparsers)

    args = parser.parse_args(sys.argv[1:])

    cloud_config = config.get_one_cloud(options=(args, []))
    cloud = shade.OpenStackCloud(cloud_config=cloud_config)

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler(sys.stderr)
    console_level = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(args.verbose_level, logging.DEBUG)
    console.setLevel(console_level)
    formatter = logging.Formatter('[%(asctime)s] %(message)s')
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    return args.func(cloud, config, args)
