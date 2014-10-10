gerrit
======

Gerrit is a java application that binds to an SSH port and an HTTP port. The
data volume is replicated across application servers with *btsync*. It requires
a postgres database which is provided by an ambassador to the postgres master
unit.

There are several secrets (``ssh_host_key``, ``registerEmailPrivateKey``, and
``restTokenPrivateKey``) which are created when the ``init`` command is run for
the first time. We capture these secrets into etcd so they are available to
other nodes.
