=========
RhodeCode
=========

About
-----

``RhodeCode`` is a fast and powerful management tool for Mercurial_ and GIT_
and Subversion_ with a built in push/pull server, full text search,
pull requests and powerfull code-review system. It works on http/https and
has a few unique features like:
 - plugable architecture
 - advanced permission system with IP restrictions
 - rich set of authentication plugins including LDAP,
   ActiveDirectory, Atlassian Crowd, Http-Headers, Pam, Token-Auth.
 - live code-review chat
 - full web based file editing
 - unified multi vcs support
 - snippets (gist) system
 - integration with all 3rd party issue trackers

RhodeCode also provides rich API, and multiple event hooks so it's easy
integrable with existing external systems.

RhodeCode is similar in some respects to gitlab_, github_ or bitbucket_,
however RhodeCode can be run as standalone hosted application on your own server.
RhodeCode can be installed on \*nix or Windows systems.

RhodeCode uses `PEP386 versioning <http://www.python.org/dev/peps/pep-0386/>`_

Installation
------------
Please visit https://docs.rhodecode.com/RhodeCode-Control/tasks/install-cli.html
for more details


Source code
-----------

The latest sources can be obtained from official RhodeCode instance
https://code.rhodecode.com


Contributions
-------------

RhodeCode is open-source; contributions are welcome!

Please see the contribution documentation inside of the docs folder, which is
also available at
https://docs.rhodecode.com/RhodeCode-Enterprise/contributing/contributing.html

For additional information about collaboration tools, our issue tracker,
licensing, and contribution credit, visit https://rhodecode.com/open-source 


RhodeCode Features
------------------

Check out all features of RhodeCode at https://rhodecode.com/features

License
-------

``RhodeCode`` is dual-licensed with AGPLv3 and commercial license.
Please see LICENSE.txt file for details.


Getting help
------------

Listed bellow are various support resources that should help.

.. note::

   Please try to read the documentation before posting any issues, especially
   the **troubleshooting section**

- Official issue tracker `RhodeCode Issue tracker <https://issues.rhodecode.com>`_

- Search our community portal `Community portal <https://community.rhodecode.com>`_

- Join #rhodecode on FreeNode (irc.freenode.net)
  or use http://webchat.freenode.net/?channels=rhodecode for web access to irc.

- You can also follow RhodeCode on twitter **@RhodeCode** where we often post
  news and other interesting stuff about RhodeCode.


Online documentation
--------------------

Online documentation for the current version of RhodeCode is available at
 - http://rhodecode.com/docs

You may also build the documentation for yourself - go into ``docs/`` and run::

    nix-build default.nix -o result && make clean html

(You need to have sphinx_ installed to build the documentation. If you don't
have sphinx_ installed you can install it via the command:
``pip install sphinx``)

.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _python: http://www.python.org/
.. _sphinx: http://sphinx.pocoo.org/
.. _mercurial: http://mercurial.selenic.com/
.. _bitbucket: http://bitbucket.org/
.. _github: http://github.com/
.. _gitlab: http://gitlab.com/
.. _subversion: http://subversion.tigris.org/
.. _git: http://git-scm.com/
.. _celery: http://celeryproject.org/
.. _vcs: http://pypi.python.org/pypi/vcs
