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
    parsed_options = parser.parse_known_args(sys.argv[1:])

    cloud_config = config.get_one_cloud(options=parsed_options)
    cloud = shade.OpenStackCloud(cloud_config=cloud_config)
    res = resolver.Resolver(cloud)

    tasks = []

    # for server in cloud.list_servers():
    #     tasks.extend(res.server(server))
    tasks.extend(res.server(cloud.get_server('dev1')))

    playbook = [
        {'hosts': 'localhost',
         'connection': 'local',
         'tasks': tasks,
         },
    ]

    print(yaml.dump(playbook, default_flow_style=False, explicit_start=True))

    print('downloading snapshot')
    image = cloud.get_image('dev1-sn1')
    with download.ProgressBarDownloader('dev1-sn1.dat', image.size) as out:
        cloud.download_image('dev1-sn1', output_file=out)

    # for volume in dev1.volumes:
    #     vol = cloud.get_volume(volume.id)
    #     pprint.pprint(vol)
