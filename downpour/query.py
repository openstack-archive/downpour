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

import logging

from downpour import resources

LOG = logging.getLogger(__name__)


def register_command(subparsers):
    do_query = subparsers.add_parser(
        'query',
        help='query to build an export list',
    )
    do_query.add_argument(
        'resource_file',
        help='the name of the file listing resources to be updated',
    )
    do_query.add_argument(
        '--save-state',
        action='store_true',
        default=False,
        help='should the state of the server or volume be saved',
    )
    do_query.add_argument(
        '--server',
        action='append',
        help='pattern to match against server names',
    )
    do_query.set_defaults(func=query_data)


def query_data(cloud, config, args):
    to_export = resources.load(args.resource_file, missing_ok=True)
    servers = set(s.name for s in to_export.servers)

    for pattern in args.server:
        LOG.info('searching for server %r', pattern)
        for server_info in cloud.search_servers(name_or_id=pattern):
            if server_info.name not in servers:
                LOG.info('found server %s to export', server_info.name)
                to_export.servers.append({
                    'name': server_info.name,
                    'save_state': args.save_state,
                })

    resources.save(args.resource_file, to_export)
