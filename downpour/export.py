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
import os.path

import yaml

from downpour import download
from downpour import resolver
from downpour import resources

LOG = logging.getLogger(__name__)


def register_command(subparsers):
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
    do_export.set_defaults(func=export_data)


def export_data(cloud, config, args):
    output_path = args.output_path

    downloader = download.Downloader(
        output_path,
        cloud,
        use_progress_bar=(args.progress and (args.verbose_level >= 1)),
    )
    res = resolver.Resolver(cloud, downloader, output_path)
    tasks = []

    # Any tasks needed to initialize the output.
    tasks.extend(res.init_tasks())

    # Export independent resources. The resolver handles dependencies
    # automatically.
    to_export = resources.load(args.resource_file)

    for keypair_info in to_export.keypairs:
        keypair = cloud.get_keypair(keypair_info.name)
        tasks.extend(res.keypair(keypair))

    for image_info in to_export.images:
        image = cloud.get_image(image_info.name)
        tasks.extend(res.image(image))

    for volume_info in to_export.volumes:
        volume = cloud.get_volume(volume_info.name)
        tasks.extend(res.volume(volume, save_state=volume_info.save_state))

    for server_info in to_export.servers:
        server = cloud.get_server(server_info.name)
        tasks.extend(res.server(server,
                                save_state=server_info.save_state,
                                key_name=server_info.get('key_name')))

    playbook = [
        # The default playbook is configured to run instructions
        # locally to talk to the cloud API.
        {'hosts': 'localhost',
         'connection': 'local',
         'tasks': tasks,
         },
    ]
    playbook_filename = os.path.join(output_path, 'playbook.yml')
    with open(playbook_filename, 'w', encoding='utf-8') as fd:
        yaml.dump(playbook, fd, default_flow_style=False, explicit_start=True)
    LOG.info('wrote playbook to %s', playbook_filename)

    downloader.start()
