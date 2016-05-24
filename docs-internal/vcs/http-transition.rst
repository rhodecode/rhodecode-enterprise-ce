.. _vcs-http:

========================================
 Transition to HTTP based communication
========================================

We are in the process of replacing the Pyro4 based communication with an HTTP
based implementation. Currently both backends are supported and can be
activated via various settings in the configuration.

To run the system in full HTTP based mode, use the following settings::

   vcs.hooks.protocol = http
   vcs.scm_app_implementation = rhodecode.lib.middleware.utils.scm_app_http
   vcs.server.protocol = http
