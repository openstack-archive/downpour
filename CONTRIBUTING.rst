There are two ways to contribute to downpour, using OpenStack's gerrit
system and GitHub. The repository managed via gerrit and visible at
https://git.openstack.org/cgit/openstack/downpour is the canonical
repository.

Gerrit Process
==============

If you would like to contribute using the standard OpenStack tools and
processes, you should follow the steps in this page:

   http://docs.openstack.org/infra/manual/developers.html

If you already have a good understanding of how the system works and your
OpenStack accounts are set up, you can skip to the development workflow
section of this documentation to learn how changes to OpenStack should be
submitted for review via the Gerrit tool:

   http://docs.openstack.org/infra/manual/developers.html#development-workflow

GitHub Process
==============

If you would prefer to use GitHub, you may also submit pull requests
to https://github.com/dhellmann/downpour. I will do the work to push
the patch through the OpenStack review process on your behalf. That
may involve changing some of the git metadata, such as committer. I
will try to keep the author field intact so you retain credit. Please
add the DCO signature to your commit messages, just to be safe.

The repository https://github.com/openstack/downpour is synced from
gerrit. Pull requests to that repository will be closed automatically.

Bug Reports
===========

Bugs should be filed on Launchpad, not GitHub:

   https://bugs.launchpad.net/os-downpour
