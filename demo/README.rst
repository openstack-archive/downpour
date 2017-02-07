================
 Demo Playbooks
================

The playbooks in this directory can be used to set up test cases for
data capture.

tiny
====

Using
=====

1. Create and activate a virtualenv.

  ::

    $ virtualenv --python=python2.7 venv
    $ source venv/bin/activate

2. Install the dependencies.

  ::

    $ pip install -r requirements.txt

3. Run the playbook.

  ::

    $ ansible-playbook tiny.yml

4. Deactivate the virtualenv or start a new shell.
5. Move to the parent directory.

  ::

    $ cd ..

6. Run ``downpour``, using tox to set up a python 3.5 virtualenv.

  ::

    $ tox -e venv -- downpour export demo/tiny-resources.yml demo/export
