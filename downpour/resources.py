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

import munch

LOG = logging.getLogger(__name__)


def load(filename, missing_ok=False):
    "Read the file and return the parsed data in a consistent format."
    LOG.info('loading resource list from %s', filename)

    # Ensure the return value has a basic set of keys representing the
    # types of resources we expect to find.
    to_return = munch.Munch(
        servers=[],
        volumes=[],
        images=[],
        keypairs=[],
    )

    try:
        with open(filename, 'r', encoding='utf-8') as fd:
            contents = munch.Munch.fromYAML(fd.read())
    except FileNotFoundError:
        if not missing_ok:
            raise
    else:
        to_return.update(contents)

    # Ensure all entries have consistent sets of keys so the rest of
    # the app doesn't have to check every time it wants to use a
    # value.
    for s in to_return.servers:
        if 'save_state' not in s:
            s['save_state'] = True
    for s in to_return.volumes:
        if 'save_state' not in s:
            s['save_state'] = True

    return to_return


def save(filename, to_export):
    "Write the resources file."
    with open(filename, 'w', encoding='utf-8') as fd:
        fd.write(to_export.toYAML())
