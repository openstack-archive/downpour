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


class ResourceFileEditor:

    def __init__(self, filename, save_state):
        self._filename = filename
        self._save_state = save_state
        self._resources = resources.load(filename, missing_ok=True)
        self._servers = set(s.name for s in self._resources.servers)
        self._images = set(i.name for i in self._resources.images)
        self._volumes = set(v.name for v in self._resources.volumes)

    def add_server(self, info):
        if info.name in self._servers:
            return
        LOG.info('found server %s to export', info.name)
        self._resources.servers.append({
            'name': info.name,
            'save_state': self._save_state,
            'key_name': info.key_name,
        })

    def add_image(self, info):
        if info.name in self._images:
            return
        LOG.info('found image %s to export', info.name)
        self._resources.images.append({
            'name': info.name,
        })

    def add_volume(self, info):
        if info.name in self._volumes:
            return
        LOG.info('found volume %s to export', info.name)
        self._resources.volumes.append({
            'name': info.name,
            'save_state': self._save_state,
        })

    def save(self):
        resources.save(self._filename, self._resources)


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
        '--server-name',
        action='append',
        default=[],
        help='pattern to match against server names',
    )
    do_query.add_argument(
        '--server-flavor',
        action='append',
        default=[],
        help='server flavor(s) to capture',
    )
    do_query.add_argument(
        '--image-name',
        action='append',
        default=[],
        help='pattern to match against image names',
    )
    do_query.add_argument(
        '--volume-name',
        action='append',
        default=[],
        help='pattern to match against volume names',
    )
    do_query.set_defaults(func=query_data)


def query_data(cloud, config, args):
    editor = ResourceFileEditor(args.resource_file, save_state=args.save_state)

    for pattern in args.server_name:
        LOG.info('searching for servers matching pattern %r', pattern)
        for info in cloud.search_servers(name_or_id=pattern):
            editor.add_server(info)

    for flavor in args.server_flavor:
        LOG.info('searching for servers using flavor %r', flavor)
        for info in cloud.search_servers(
                filters={'flavor': {'id': flavor}}):
            editor.add_server(info)

    for pattern in args.image_name:
        LOG.info('searching for images matching pattern %r', pattern)
        for info in cloud.search_images(name_or_id=pattern):
            editor.add_image(info)

    for pattern in args.volume_name:
        LOG.info('searching for available volumes matching pattern %r',
                 pattern)
        for info in cloud.search_volumes(
                name_or_id=pattern,
                filters={
                    'status': 'available',
                }):
            editor.add_volume(info)

    editor.save()
