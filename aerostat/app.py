# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
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
import shade

from aerostat import export
from aerostat import query


def main():
    parser = argparse.ArgumentParser()
    config = os_client_config.OpenStackConfig()

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

    config.register_argparse_arguments(parser, sys.argv, None)
    subparsers = parser.add_subparsers(title='commands')

    do_export = subparsers.add_parser(
        'export',
        help='export data',
    )
    do_export.add_argument(
        'resource_file',
        help='the name of the file listing resources to be exported',
    )
    do_export.add_argument(
        'output_path',
        default='.',
        nargs='?',
        help='the name of a directory to use for output file(s)',
    )
    do_export.set_defaults(func=export.export_data)

    do_query = subparsers.add_parser(
        'query',
        help='query to build an export list',
    )
    do_query.add_argument(
        'resource_file',
        help='the name of the file listing resources to be updated',
    )
    do_query.set_defaults(func=query.query_data)

    args = parser.parse_args(sys.argv[1:])

    return args.func(config, args)
    return args.func(cloud, config, args)
