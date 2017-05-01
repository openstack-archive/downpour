======================
 Resource File Format
======================

A Downpour resource file is a YAML file containing explicitly
identified resources to be exported, along with instructions for how
to handle the export.

``keypairs``
============

The keypairs section lists the names of the keypairs to be
exported. Keys associated with servers are exported automatically, but
if it is important to move keys not in use by any of the servers those
keys can be listed separately.

Each item in the keypairs list should be a mapping with a value for
``name``.

::

  keypairs:
    - name: downpour-demo

``images``
==========

The images section lists the names of the images to be exported.

Each item in the images list should be a mapping with a value for
``name``.

::

  images:
    - name: cirros-0.3.5-x86_64-disk

``volumes``
===========

The volumes section lists the names and settings for the unattached
volumes to be exported. This section should **not** include volumes
attached to servers, because those are exported as part of exporting
the server definition.

Each item in the images list should be a mapping with a value for
``name`` and an optional boolean value for ``save_state``, indicating
whether the contents of the volume should be exported. If
``save_state`` is false, a new volume with the same name and size will
be created but it will be empty. The default is to save the contents
of the volume.

::

  volumes:
    - name: downpour-demo-unattached
      save_state: false

``servers``
===========

The servers section lists the names and settings for the virtual
machines to be exported.

Each item in the images list should be a mapping with a value for
``name``. It can also contain an optional boolean value for
``save_state``, indicating whether the contents of the VM should be
exported. If ``save_state`` is false, a new VM with the same name and
flavor will be created, but it will not contain any of the files from
the current VM. The default is to save the contents of the volume.

If an optional ``key_name`` setting is given, the new VM will be
initialized using that ssh keypair instead of the one already
associated with the server. The keypair does not need to exist on the
source system.

::

   servers:
     - name: downpour-demo-tiny
       # Create the server using a separate key than
       # it was created with in tiny.yml.
       key_name: downpour-demo2
