==================================================
 aerostat -- OpenStack Tenant Data Migration Tool
==================================================

aerostat_ exports tenant data from an OpenStack cloud to create a set
of Ansible playbooks for importing the data into another cloud.

.. _aerostat: https://en.wikipedia.org/wiki/Aerostat

Installing and Using
====================

The project is in a very very early prototyping stage.  With tox_
installed, experiment via::

  $ tox -e venv -- aerostat

.. _tox: https://tox.readthedocs.io/en/latest/

* Free software: Apache license
* Source: http://git.openstack.org/cgit/openstack/aerostat
