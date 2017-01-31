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

import progressbar

LOG = logging.getLogger(__name__)


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

    def __init__(self, output_dir, cloud, use_progress_bar):
        self.output_dir = output_dir
        self.cloud = cloud
        self.use_progress_bar = use_progress_bar
        self._tasks = []

    def _add(self, resource_type, resource, output_path):
        LOG.info('scheduling download of %s %s', resource_type, resource.name)
        self._tasks.append((resource_type, resource, output_path))

    def add_image(self, image):
        base = image.name + '.dat'
        output_path = os.path.join(self.output_dir, base)
        self._add('image', image, output_path)
        return base

    def add_volume(self, volume):
        LOG.error('DO NOT KNOW HOW TO SAVE VOLUME STATE YET %s', volume.name)

    def start(self):
        # FIXME(dhellmann): start downloads in a separate thread or process
        for resource_type, resource, output_path in self._tasks:
            if os.path.exists(output_path):
                LOG.info(
                    'output file %s already exists, skipping download',
                    output_path,
                )
                continue
            if resource_type == 'image':
                LOG.info(
                    'downloading image %s to %s',
                    resource.name,
                    output_path,
                )
                if self.use_progress_bar:
                    with ProgressBarDownloader(output_path, resource.size) as out:
                        self.cloud.download_image(resource.name, output_file=out)
                else:
                    with open(output_path, 'wb') as out:
                        self.cloud.download_image(resource.name, output_file=out)
                LOG.info(
                    'downloaded image %s to %s',
                    resource.name,
                    output_path,
                )
