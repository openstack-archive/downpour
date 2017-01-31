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

    def __init__(self, cloud, downloader):
        self.cloud = cloud
        self._memo = set()
        self._downloader = downloader

    def security_group(self, group):
        if ('security_group', group.id) in self._memo:
            return
        self._memo.add(('security_group', group.id))
        remote_groups = {}
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

    def volume(self, volume, save_state):
        # FIXME(dhellmann): For now this only creates new empty
        # volumes, and doesn't handle cases like booting from a volume
        # or creating a volume from an image.
        #
        # FIXME(dhellmann): Need to snapshot the volume and then
        # download the results.
        if save_state:
            self._downloader.add_volume(volume)
        yield {
            'name': 'Create volume {}'.format(volume.name),
            'os_volume': {
                'display_name': volume.display_name,
                'display_description': volume.display_description,
                'size': volume.size,
                'state': 'present',
            },
        }

    def server(self, server, save_state):
        for sg in server.security_groups:
            sg_data = self.cloud.get_security_group(sg.name)
            yield from self.security_group(sg_data)
        vol_names = []
        for vol in server.volumes:
            vol_data = self.cloud.get_volume(vol.id)
            vol_names.append(vol_data.name)
            yield from self.volume(vol_data, save_state)
        # FIXME(dhellmann): Need to handle networks other than 'public'.
        # FIXME(dhellmann): Need to handle public IPs. Use auto_ip?
        # FIXME(dhellmann): For now assume the image exists, but we may
        #                   have to dump and recreate it.
        # image = self.cloud.get_image(server.image.id)
        # pprint.pprint(image)
        # FIXME(dhellmann): It looks like ceph-backed servers have an
        # image ID set to their volume or something? It's not a public
        # image visible through the glance API.
        server_data = {
            'name': server.name,
            'state': 'present',
            # Attach to the networks by name.
            'nics': list(server.networks.keys()),
            # 'image': image.name if image else server.image.id,
        }
        if vol_names:
            server_data['volumes'] = vol_names
        yield {
            'name': 'Creating server {}'.format(server.name),
            'os_server': server_data,
        }

    def image(self, image):
        filename = self._downloader.add_image(image)
        image_data = {
            'name': image.name,
            'container_format': image.container_format,
            'disk_format': image.disk_format,
            'min_disk': image.min_disk,
            'min_ram': image.min_ram,
        }
        # FIXME(dhellmann): handle ramdisk property?
        if filename:
            image_data['filename'] = filename
        yield {
            'name': 'Creating image {}'.format(image.name),
            'os_image': image_data,
        }
