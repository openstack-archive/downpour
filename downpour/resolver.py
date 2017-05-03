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

import itertools
import logging

LOG = logging.getLogger(__name__)


class Resolver:

    def __init__(self, cloud, downloader, output_path):
        self.cloud = cloud
        self._memo = set()
        self._downloader = downloader
        self._output_path = output_path
        self._uuid_map_file = 'uuids.csv'
        self._var_counter = itertools.count(1)

    def _mk_var_name(self, slug):
        name = '{}{:03d}'.format(slug, next(self._var_counter))
        self._last_var = name
        return name

    def _map_uuids(self, resource_type, name, old_id, var_expr):
        pat = '"{}","{}","{}"'.format(
            resource_type, name, old_id,
        )
        line = '{},"{}"'.format(
            pat, '{{' + self._last_var + '.' + var_expr + '}}',
        )
        return {
            'name': 'Map UUID for {} {}'.format(resource_type, name),
            'lineinfile': {
                'dest': self._uuid_map_file,
                'state': 'present',
                'regexp': pat,
                'insertafter': 'EOF',
                'line': line,
            },
        }

    def init_tasks(self):
        yield {
            'name': 'Initializing UUID mapping file',
            'lineinfile': {
                'create': 'yes',
                'dest': self._uuid_map_file,
                'state': 'present',
                'regexp': '"Resource Type","Resource Name","Old","New"',
                'insertbefore': 'BOF',
                'line': '"Resource Type","Resource Name","Old","New"',
            },
        }

    def keypair(self, keypair):
        if ('keypair', keypair.name) in self._memo:
            return
        self._memo.add(('keypair', keypair.name))
        yield {
            'name': 'Add public key {}'.format(keypair.name),
            'os_keypair': {
                'name': keypair.name,
                'public_key': keypair.public_key,
            },
            'register': self._mk_var_name('key'),
        }
        yield self._map_uuids(
            'keypair', keypair.name, keypair.id, 'key.id',
        )

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
            'register': self._mk_var_name('sg'),
        }
        yield self._map_uuids(
            'security group', group.name, group.id,
            'secgroup.id',
        )
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
            yield {
                'name': 'Add rule to security group {}'.format(group.name),
                'os_security_group_rule': rule_data,
            }

    def volume(self, volume, save_state):
        if ('volume', volume.name) in self._memo:
            return
        self._memo.add(('volume', volume.name))
        if save_state:
            image_name = 'volume-capture-{}'.format(volume.id)
            image_info = self.cloud.get_image(image_name)
            if image_info:
                LOG.info('found existing capture of volume %s in %s',
                         volume.name, image_name)
            else:
                LOG.info('creating image from volume %s as %s',
                         volume.name, image_name)
                image_info = self.cloud.create_image(
                    name=image_name,
                    volume=volume.id,
                    wait=True,
                )
            yield from self.image(image_info)
        os_volume = {
            'display_name': volume.display_name,
            'display_description': volume.display_description,
            'size': volume.size,
            'state': 'present',
        }
        if save_state:
            os_volume['image'] = image_name
        yield {
            'name': 'Create volume {}'.format(volume.name),
            'os_volume': os_volume,
            'register': self._mk_var_name('vol'),
        }
        yield self._map_uuids('volume', volume.name, volume.id, 'volume.id')

    def network(self, network):
        if ('network', network.name) in self._memo:
            return
        self._memo.add(('network', network.name))
        yield {
            'name': 'Create network {}'.format(network.name),
            'os_network': {
                'name': network.name,
                'external': network.get('router:external', False),
                'shared': network.shared,
                'state': 'present',
            },
            'register': self._mk_var_name('net'),
        }
        yield self._map_uuids('network', network.name, network.id, 'network.id')
        for subnet_id in network.subnets:
            subnet = self.cloud.get_subnet(subnet_id)
            os_subnet = {
                'name': subnet.name,
                'network_name': network.name,
                'cidr': subnet.cidr,
                'state': 'present',
                'allocation_pool_start': subnet.allocation_pools[0]['start'],
                'allocation_pool_end': subnet.allocation_pools[0]['end'],
                'dns_nameservers': subnet.dns_nameservers,
                'ip_version': subnet.ip_version,
            }
            if subnet.gateway_ip:
                os_subnet['gateway_ip'] = subnet.gateway_ip
            if subnet.ip_version == 6:
                os_subnet['ipv6_ra_mode'] = subnet.ipv6_ra_mode
                os_subnet['ipv6_address_mode'] = subnet.ipv6_address_mode
            yield {
                'name': 'Create subnet {} on network {}'.format(subnet.name,
                                                                network.name),
                'os_subnet': os_subnet,
                'register': self._mk_var_name('subnet'),
            }
            yield self._map_uuids('subnet', subnet.name, subnet.id, 'subnet.id')

    def server(self, server, save_state, key_name=None):
        # The ssh key needed to login to the server.
        keypair = self.cloud.get_keypair(server.key_name)
        yield from self.keypair(keypair)

        # The security groups and other network settings for the
        # server.
        for sg in server.security_groups:
            sg_data = self.cloud.get_security_group(sg.name)
            yield from self.security_group(sg_data)
        for net_name in server.networks:
            net_data = self.cloud.get_network(net_name)
            yield from self.network(net_data)
        # FIXME(dhellmann): Need to handle public IPs. Use auto_ip?

        # Any volumes attached to the server.
        # FIXME(dhellmann): The server needs to be stopped and the
        # volumes need to be detached before this step.
        vol_names = []
        # for vol in server.volumes:
        #     vol_data = self.cloud.get_volume(vol.id)
        #     vol_names.append(vol_data.name)
        #     yield from self.volume(vol_data, save_state)

        # The main portion of the server image.
        # FIXME(dhellmann): It looks like ceph-backed servers have an
        # image ID set to their volume or something? It's not a public
        # image visible through the glance API.
        if save_state:
            image_name = 'downpour-server-capture-{}'.format(server.id)
            image = self.cloud.get_image(image_name)
            if image:
                LOG.info('found existing capture of server %s in %s',
                         server.name, image_name)
            else:
                LOG.info('capturing server %s to image %s',
                         server.name, image_name)
                image = self.cloud.create_image_snapshot(
                    name=image_name,
                    server=server,
                    wait=True,
                )
        else:
            image = self.cloud.get_image(server.image.id)
        yield from self.image(image)

        server_data = {
            'name': server.name,
            'state': 'present',
            # Attach to the networks by name.
            'nics': list(server.networks.keys()),
            'image': image.name,
        }
        key_name = key_name or server.key_name
        if key_name:
            server_data['key_name'] = key_name
        if vol_names:
            server_data['volumes'] = vol_names
        yield {
            'name': 'Creating server {}'.format(server.name),
            'os_server': server_data,
            'register': self._mk_var_name('server'),
        }
        yield self._map_uuids('server', server.name, server.id, 'server.id')

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
            'register': self._mk_var_name('img'),
        }
        yield self._map_uuids('image', image.name, image.id, 'image.id')
