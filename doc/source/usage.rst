=======
 Usage
=======

Downpour uses a four step process. Between each step it is possible to
stop and modify the data that has been prepared to pass to the next
step.

1. Identify Resources to Export
===============================

The first phase of using Downpour is to identify exactly what
resources will be exported from the cloud to build the :term:`resource
file`. This step can be performed by hand by creating the required
input file in a text editor, or the file can be build using the
``query`` command.

The resource file is a YAML file with sections for the principle
resource types, ``keypairs``, ``images``, ``volumes``, and
``servers``.  Resources are identified by name, and may also include
extra parameters to control how the export and re-import operations
are performed. For example, this resource file causes the
``downpour-demo-tiny`` server to be exported but when it is recreated
a different ssh key is used to provide access to log in.

.. literalinclude:: ../../demo/tiny-resources.yml

The ``downpour query`` command also can be used to find resources
visible in the cloud, and add them to the resource file. It supports
wildcard patterns in names and other criteria for filtering
resources. For example, this command finds all servers with "``tiny``"
in their name.

::

  $ downpour query --server-name '*tiny*' export.yml

.. seealso::

   :doc:`resource_file` includes more details about resource files.

2. Exporting Resources
======================

The second phase of operation is to actually export the resources from
the cloud using ``downpour export``, passing the resource file as
input. Downpour starts by processing the resources listed in the file
explicitly, and identifies any extra dependencies needed to recreate
the configuration of those resources. For example, the networks,
subnets, and security groups used by a server are exported
automatically, as are the volumes attached to the server.

::

  $ downpour export export.yml ./export/

The output for the export process is an Ansible_ playbook to recreate
the resources, with all relationships intact. For images, volumes, and
servers with the ``save-state`` flag set to true, the content of the
resource will be downloaded and saved to the output directory where it
can be used to recreate the resource.

3. Importing Resources
======================

The import phase uses ``ansible-playbook`` to run the playbook created
by the exporter.

.. note::

   Although Downpour currently requires Python 3.5 or greater, Ansible
   is a Python 2.x application. If you are using ``pip`` and
   ``virtualenv`` to install the tools, you will need to install them
   in separate virtual environments.

Ansible uses uses `os-client-config`_ for settings related to
accessing the cloud. The simplest way to configure the cloud is via a
``clouds.yaml`` file, but any mechanism supported by Ansible will
work. The credentials used for the import phase do not need to be the
same as the export phase. In fact, they're likely to be completely
different because they will refer to a separate cloud's API endpoints.

Downpour supports some customizations during export, such as changing
the ssh key to be used for accessing a server. Other changes can be
made by editing the playbook before running it.

The playbook produced by Downpour creates each resource, then adds a
line to a file ``uuids.csv`` to map the UUID in the source cloud to
the UUID in the target cloud. This file may be useful for updating
scripts or other configuration that rely on the UUID instead of a
unique name for the resource.

::

   "Resource Type","Resource Name","Old","New"
   "security group","downpour-demo","6deea469-54bd-4846-b12a-79fa6b482280","a4b80ffc-bc51-485c-915a-9ba9a7b4dcf0"
   "volume","downpour-demo-tiny","256868c6-441f-4cd3-96fd-bda92c33822c","62e5616c-9a8c-44e2-bd14-4685b905ea94"
   "security group","downpour-demo","3c7dcb77-d9ac-4af1-ba95-3f5d89a85227","a4b80ffc-bc51-485c-915a-9ba9a7b4dcf0"
   "volume","downpour-demo-tiny","a6192546-c36e-4bee-ad00-8229e0b0efc5","62e5616c-9a8c-44e2-bd14-4685b905ea94"
   "network","private","56a86bdb-13b2-4c9f-b8f5-a942d52602b5","f3027502-e4a2-4610-81fb-c6df99ead5c3"
   "subnet","ipv6-private-subnet","8d736fe4-6b8f-4bf5-a38e-b511dce21f7f","01025e33-703b-4aa4-b6ec-80036bb3679b"
   "subnet","private-subnet","e6baf9f4-09b5-4292-8236-3cca609ec2a3","2f9a1686-8125-4316-acd3-dbee51c44c1d"
   "keypair","downpour-demo","downpour-demo","downpour-demo"
   "image","cirros-0.3.5-x86_64-disk","570ec7bd-011b-4fbe-9968-626225654a7f","570ec7bd-011b-4fbe-9968-626225654a7f"

.. _ansible: https://www.ansible.com
.. _os-client-config: http://docs.openstack.org/developer/os-client-config/

4. Decomissioning Resources
===========================

Downpour is not a live-migration tool, and it does not delete any
resources from the source cloud. This allows you to perform
application-specific migration (such as a final database sync) before
updating any load balancers or DNS records and deleting old
information.
