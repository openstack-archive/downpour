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
import shade
import yaml


def build_security_group(cloud, memo, group):
    if ('security_group', group.id) in memo:
        return
    memo.add(('security_group', group.id))
    remote_groups = {}
    pprint.pprint(group)
    yield {
        'name': 'Add security group {}'.format(group.name),
        'os_security_group': {
            'state': 'present',
            'name': group.name,
            'description': group.description,
        },
    }
    for rule in group.security_group_rules:
        rule_data = {
            'direction': rule.direction,
            'ethertype': rule.ethertype,
            'protocol': rule.protocol,
            'security_group': group.name,
            'state': 'present',
        }
        for opt in ['port_range_min', 'port_range_max',
                    'remote_group_id', 'remote_ip_prefix']:
            value = rule.get(opt)
            if value:
                rule_data[opt] = value
        if rule.remote_group_id:
            if rule.remote_group_id not in remote_groups:
                remote_group = cloud.get_security_group(rule.remote_group_id)
                remote_groups[remote_group.id] = remote_group.name
            rule_data['remote_group_id'] = remote_groups[rule.remote_group_id]
        yield {'os_security_group_rule': rule_data}


def build_server(cloud, memo, server):
    pprint.pprint(server)
    for sg in server.security_groups:
        sg_data = cloud.get_security_group(sg.name)
        yield from build_security_group(cloud, memo, sg_data)


def main():
    parser = argparse.ArgumentParser()
    config = os_client_config.OpenStackConfig()

    config.register_argparse_arguments(parser, sys.argv, None)
    parsed_options = parser.parse_known_args(sys.argv[1:])

    cloud_config = config.get_one_cloud(options=parsed_options)
    cloud = shade.OpenStackCloud(cloud_config=cloud_config)

    tasks = []
    memo = set()

    for server in cloud.list_servers():
        tasks.extend(build_server(cloud, memo, server))

    playbook = [
        {'hosts': 'localhost',
         'connection': 'local',
         'tasks': tasks,
         },
    ]

    print(yaml.dump(playbook, default_flow_style=False, explicit_start=True))

    # for volume in dev1.volumes:
    #     vol = cloud.get_volume(volume.id)
    #     pprint.pprint(vol)
