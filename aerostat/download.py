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

import progressbar


class ProgressBarDownloader:

    def __init__(self, output_path, max_value):
        self.output_path = output_path
        self.max_value = max_value
        self.bar = None
        self.fd = None
        self.amt_read = 0

    def __enter__(self):
        self.bar = progressbar.ProgressBar(
            widgets=[
                progressbar.Percentage(),
                ' ',
                progressbar.Bar(),
                progressbar.FileTransferSpeed(),
                ' ',
                progressbar.ETA(),
            ],
            max_value=self.max_value,
        )
        self.fd = open(self.output_path, 'wb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()
        self.bar.finish()
        return False

    def write(self, block):
        if block:
            self.fd.write(block)
            self.amt_read += len(block)
            self.bar.update(self.amt_read)


class Downloader:

    def __init__(self, output_dir, cloud):
        self.output_dir = output_dir
        self.cloud = cloud
        self._tasks = []

    def _add(self, resource_type, resource, output_path):
        self._tasks.append((resource_type, resource, output_path))

    def add_image(self, image):
        base = image.name + '.dat'
        output_path = os.path.join(self.output_dir, base)
        self._add('image', image, output_path)
        return base

    def add_volume(self, volume):
        print('DO NOT KNOW HOW TO SAVE VOLUME STATE YET', volume.name)

    def start(self):
        # FIXME(dhellmann): start downloads in a separate thread or process
        for resource_type, resource, output_path in self._tasks:
            if os.path.exists(output_path):
                print(
                    'output file {} already exists, skipping download'.format(
                        output_path))
                continue
            if resource_type == 'image':
                print('downloading image {} to {}'.format(
                    resource.name,
                    output_path,
                ))
                with ProgressBarDownloader(output_path, resource.size) as out:
                    self.cloud.download_image(resource.name, output_file=out)
