===================================================
 downpour --- OpenStack Tenant Data Migration Tool
===================================================

downpour exports tenant data from an OpenStack cloud to create a set
of Ansible playbooks for importing the data into another cloud.

Installing and Using
====================

The project is in a very very early prototyping stage.

downpour uses `os-client-config`_ for settings related to accessing
the cloud. Fill in your ``clouds.yaml`` or use the environment
variables or command line arguments provided.

With tox_ installed, experiment via::

  $ tox -e venv -- downpour

.. _tox: https://tox.readthedocs.io/en/latest/
.. _os-client-config: http://docs.openstack.org/developer/os-client-config/

* Free software: Apache license
* Source: http://git.openstack.org/cgit/openstack/downpour
* Documentation: http://downpour.readthedocs.io/en/latest/
