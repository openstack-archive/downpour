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

import pprint


class Resolver:

    def __init__(self, cloud):
        self.cloud = cloud
        self._memo = set()

    def security_group(self, group):
        if ('security_group', group.id) in self._memo:
            return
        self._memo.add(('security_group', group.id))
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
                    remote_group = self.cloud.get_security_group(rule.remote_group_id)
                    remote_groups[remote_group.id] = remote_group.name
                rule_data['remote_group_id'] = remote_groups[rule.remote_group_id]
            yield {'os_security_group_rule': rule_data}

    def server(self, server):
        pprint.pprint(server)
        for sg in server.security_groups:
            sg_data = self.cloud.get_security_group(sg.name)
            yield from self.security_group(sg_data)
