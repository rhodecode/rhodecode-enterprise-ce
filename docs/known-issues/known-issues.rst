.. _known-issues:

Known Issues
============

Subversion Issues
-----------------

Limited |svn| support has been achieved for this release,
|release|. The following known issues are in development for improvement.

* |svn| |repo| creation:
  Terminating the VCS Server during remote importation of |svn| |repos| leaves
  the the process still running in the background.

* |svn| |repo| checkin/checkout:
  |svn| cloning support is not enabled by default. Please contact support if
  you want it enabled.

Windows Upload
--------------

There can be an issue with uploading files from web interface on Windows,
and afterwards users cannot properly clone or synchronize with the repository.

Early testing shows that often uploading files via HTML forms on Windows
includes the full path of the file being uploaded and not the name of the file.

Old Format of Git Repositories
------------------------------

There is an issue when trying to import old |git| format |repos| into recent
versions of |RCE|. This issue can occur when importing from external |git|
repositories or from older versions of |RCE| (<=2.2.7).

To convert the old version into a current version, clone the old
|repo| into a local machine using a recent |git| client, then push it to a new
|repo| inside |RCE|.

VCS Server Memory Consumption
-----------------------------

The VCS Server cache grows without limits if not configured correctly. This
applies to |RCE| versions prior to the 3.3.2 releases, as 3.3.2
shipped with the optimal configuration as default. See the
:ref:`vcs-server-maintain` section for details.

To fix this issue, upgrade to |RCE| 3.3.2 or greater, and if you discover
memory consumption issues check the VCS Server settings.

Fedora 23
---------

|RCC| does not run perfectly on Fedora 23 due to a locale issue. This is a
known issue under investigation due to the Nix packaging of the product, see the
`Github issue here`_. |RCC| runs fine on Fedora 21.

To work around this problem, you need to point ``$LOCAL_ARCHIVE`` to the
workaround locale package.

1. Download this package:
   http://lipa.ms.mff.cuni.cz/~cunav5am/nix/locale-archive

2. Point ``$LOCAL_ARCHIVE`` to the locale package.

.. code-block:: bash

    $ export LOCALE_ARCHIVE=/home/VERSION/locale-archive # change to your path

If you happen to be running |RCC| from systemd, use the following
example to pass the correct locale information on boot.

.. code-block:: ini

    [Unit]
    Description=Rhodecode
    After=network.target

    [Service]
    Type=forking
    User=scm
    Environment="LOCALE_ARCHIVE=/YOUR-PATH/locale-archive"
    ExecStart=/YOUR-PATH/.rccontrol-profile/bin/rccontrol-self-init

    [Install]
    WantedBy=multi-user.target

.. _Github issue here: https://github.com/NixOS/nix/issues/599
