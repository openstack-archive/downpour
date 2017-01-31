==================================================
 aerostat -- OpenStack Tenant Data Migration Tool
==================================================

aerostat_ exports tenant data from an OpenStack cloud to create a set
of Ansible playbooks for importing the data into another cloud.

.. _aerostat: https://en.wikipedia.org/wiki/Aerostat

Installing and Using
====================

The project is in a very very early prototyping stage.

aerostat uses `os-client-config`_ for settings related to accessing
the cloud. Fill in your ``clouds.yaml`` or use the environment
variables or command line arguments provided.

With tox_ installed, experiment via::

  $ tox -e venv -- aerostat

.. _tox: https://tox.readthedocs.io/en/latest/
.. _os-client-config: http://docs.openstack.org/developer/os-client-config/

* Free software: Apache license
* Source: http://git.openstack.org/cgit/openstack/aerostat
