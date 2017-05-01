==============
 Installation
==============

Prerequisites
=============

Downpour is written to take advantage of features of Python 3.5, so
you will need a Python 3.5+ interpreter installed.

Installing with pip
===================

At the command line::

    $ pip install os-downpour

.. note:: The dist name for downpour is ``os-downpour``.

Cloud Access Credentials
========================

downpour uses `os-client-config`_ for settings related to accessing
the cloud. Fill in your ``clouds.yaml`` or use the environment
variables or command line arguments provided.

.. _os-client-config: http://docs.openstack.org/developer/os-client-config/
