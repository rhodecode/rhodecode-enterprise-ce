|RCM|
=====

|RCM| is a high-performance source code management and collaboration system.
It enables you to develop projects securely behind the firewall while
providing collaboration tools that work with |git|, |hg|,
and |svn| |repos|. The user interface allows you to create, edit,
and commit files and |repos| while managing their security permissions.

|RCM| provides the following features:

* Source code management.
* Extended permissions management.
* Integrated code collaboration tools.
* Integrated code review and notifications.
* Scalability provided by multi-node setup.
* Fully programmable automation API.
* Web-based hook management.
* Native |svn| support.
* Migration from existing databases.
* |RCM| SDK.
* Built-in analytics
* Pluggable authentication system.
* Support for |LDAP|, Crowd, CAS, PAM.
* Debug modes of operation.
* Private and public gists.
* Gists with limited lifetimes and within instance only sharing.
* Fully integrated code search function.
* Always on SSL connectivity.

.. only:: html

   Table of Contents
   -----------------

.. toctree::
   :maxdepth: 1
   :caption: Admin Documentation

   install/quick-start
   install/install-database
   install/install-steps
   admin/system-overview
   nix/default-env
   admin/system-admin
   admin/user-admin
   admin/setting-repo-perms
   admin/security-tips
   auth/auth
   issue-trackers/issue-trackers
   admin/lab-settings

.. toctree::
   :maxdepth: 1
   :caption: Feature Documentation

   collaboration/collaboration
   collaboration/review-notifications
   collaboration/pull-requests
   code-review/code-review

.. toctree::
   :maxdepth: 1
   :caption: Developer Documentation

   api/api
   tools/rhodecode-tools
   integrations/integrations
   contributing/contributing

.. toctree::
   :maxdepth: 1
   :caption: User Documentation

   usage/basic-usage
   tutorials/tutorials

.. toctree::
   :maxdepth: 1
   :caption: About

   known-issues/known-issues
   release-notes/release-notes
   admin/glossary
