============
 Background
============

Downpour is being created to solve the problem of moving workloads
between clouds. It is only one of several possible approaches to the
problem, and fits into a very specific niche at the hard end of the
range of use cases.

.. list-table::
   :header-rows: 1

   - * 
     * Easy
     * Moderate
     * Hard
   - * **Ownership**
     * Operator
     * Admin
     * Tenant
   - * **Backend**
     * Shared storage
     * Fast interconnect
     * Shared nothing
   - * **Applications**
     * One per tenant
     * Multi-app with naming conventions
     * Rats nest

Downpour does not assume the user has an special access to the cloud,
either as an operator with access to backend systems or via admin
APIs.

Downpour does not assume that the source and destination clouds are
connected in any way. Not only is it possible to move data between
clouds that do not share backend services, it is possible to move data
between clouds that cannot be accessed from the same system at the
same time.

Downpour does not make any assumptions about the mapping between
applications and tenants. It is possible to extract only part of the
resources owned by a tenant. The grouping is completely up to the
user, and can represent an application or a single node in a multi-VM
configuration.

Downpour does not assume the source and destination clouds are build
using the same architecture or configured in the same way. As long as
the two clouds pass the standard OpenStack interoperability tests, it
should be possible to use Downpour to move your workload.

These requirements do come with trade-offs, the impact of which will
depend on how "cloud native" an application really is. For example,
the benefits of copy-on-write images may be lost during the migration
if the entire image from each VM needs to be uploaded into the new
cloud. The UUIDs associated with resources will also change, since
there is no way to guarantee the assignment of a specific UUID for
resources created in a separate cloud.
