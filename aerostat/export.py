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

import os.path

import yaml

from aerostat import download
from aerostat import resolver
from aerostat import resources


def export_data(cloud, config, args):
    output_path = args.output_path

    downloader = download.Downloader(output_path, cloud)
    res = resolver.Resolver(cloud, downloader)
    tasks = []

    # Export independent resources. The resolver handles dependencies
    # automatically.
    to_export = resources.load(args.resource_file)

    for image_info in to_export.images:
        image = cloud.get_image(image_info.name)
        tasks.extend(res.image(image))

    for volume_info in to_export.volumes:
        volume = cloud.get_volume(volume_info.name)
        tasks.extend(res.volume(volume, save_state=volume_info.save_state))

    for server_info in to_export.servers:
        server = cloud.get_server(server_info.name)
        tasks.extend(res.server(server, save_state=server_info.save_state))

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
    print('wrote playbook to {}'.format(playbook_filename))

    downloader.start()
