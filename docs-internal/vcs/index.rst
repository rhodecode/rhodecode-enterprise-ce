
======================================
 VCS client and VCSServer integration
======================================

Enterprise uses the VCSServer as a backend to provide version control
functionalities. This section describes the components in Enterprise which talk
to the VCSServer.

The client library is implemented in :mod:`rhodecode.lib.vcs`. For HTTP based
access of the command line clients special middlewares and utilities are
implemented in :mod:`rhodecode.lib.middleware`.




.. toctree::
   :maxdepth: 2

   http-transition
   middleware
   vcsserver
   subversion
