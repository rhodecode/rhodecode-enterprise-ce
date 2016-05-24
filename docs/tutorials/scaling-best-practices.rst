.. _scaling-tips:

======================
Scaling Best Practices
======================

When deploying |RCE| at scale; 100s of users, multiple instances, CI servers,
there are a number of steps you can take to ensure you are getting the
most out of your system.

Separate Users and CI Servers
-----------------------------

You can configure multiple |RCE| instances to point to the same database and
set of |repos|. This lets users work on an instance that has less traffic
than those being hit by CI servers. To configure this, use |RCC| to install
multiple instances and configure the database and |repos| connection. If you
do need to reset the database connection, see the
:ref:`config-database` section.

Once configured, set your CI servers to use a particular instance and for
user specific instances you can configure loads balancing. See the
:ref:`nginx-ws-ref` section for examples.

Switch to Database Sessions
---------------------------

To increase database performance switch to database-based user sessions. In a
large scale deployment, we recommend switching from file-based
sessions to database-based user sessions. For configuration details, see the
:ref:`db-session-ref` section.

Tuning |RCE|
------------

There are also a number of options available to tune |RCE| for certain
scenarios, including memory cache size. See the :ref:`rhodecode-tuning-ref`
section.

Use Authentication Tokens
-------------------------

Set up a user account for external services, and then use Authentication
Tokens with those external services. These tokens work with
push/pull operations only, and you can manage multiple tokens through this user
account, and revoke particular ones if necessary. In this way one user can have
multiple tokens, so all your jenkins/CI servers could share one account.

* To enable tokens, go to :menuselection:`Admin --> Authentication` and enable
  the `rhodecode.lib.auth_modules.auth_token` library.

* To create tokens, go to
  :menuselection:`Username --> My Account --> Auth tokens` and generate the
  necessary tokens. For more information, see the :ref:`config-token-ref`
  section.

Scaling Deployment Diagram
--------------------------

.. image:: ../images/scaling-diagrm.png
   :align: center
