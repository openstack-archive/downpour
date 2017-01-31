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
import os.path
import pprint
import sys

import os_client_config
import progressbar
import shade
import yaml

from aerostat import download
from aerostat import resolver


def main():
    parser = argparse.ArgumentParser()
    config = os_client_config.OpenStackConfig()

    config.register_argparse_arguments(parser, sys.argv, None)
    parser.add_argument(
        'resource_file',
        help='the name of the file listing resources to be exported',
    )
    parser.add_argument(
        'output_path',
        default='.',
        nargs='?',
        help='the name of a directory to use for output file(s)',
    )

    args, remaining = parser.parse_known_args(sys.argv[1:])
    output_path = args.output_path

    cloud_config = config.get_one_cloud(options=(args, remaining))
    cloud = shade.OpenStackCloud(cloud_config=cloud_config)
    downloader = download.Downloader(output_path, cloud)
    res = resolver.Resolver(cloud, downloader)

    tasks = []

    # FIXME(dhellmann): We want the list of things to download to be
    # part of the inputs to the program, but for now let's just grab
    # all servers and private images..

    for server in cloud.list_servers():
        tasks.extend(res.server(server))

    for image in cloud.list_images():
        if image.visibility != 'private':
            continue
        tasks.extend(res.image(image))

    playbook = [
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

    # print('downloading volume snapshot')
    # snapshot = cloud.get_volume_snapshot('testvol1-sn1')
    # pprint.pprint(snapshot)
    # # with download.ProgressBarDownloader('testvol1-sn1.dat', snapshot.size) as out:
    # #     cloud.download_image('dev1-sn1', output_file=out)

    # for volume in dev1.volumes:
    #     vol = cloud.get_volume(volume.id)
    #     pprint.pprint(vol)
