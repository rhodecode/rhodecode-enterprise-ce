.. _config-files:

Configuration Files Overview
============================

|RCE| and |RCC| have a number of different configuration files. The following
is a brief explanation of each, and links to their associated configuration
sections.

.. rst-class:: dl-horizontal

    \- **rhodecode.ini**
        Default location:
        :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini`

        This is the main |RCE| configuration file and controls much of its
        default behaviour. It is also used to configure certain customer
        settings. Here are some of the most common reasons to make changes to
        this file.

        * :ref:`config-database`
        * :ref:`set-up-mail`
        * :ref:`increase-gunicorn`
        * :ref:`x-frame`

    \- **mapping.ini**
        Default location:
        :file:`/home/{user}/.rccontrol/{instance-id}/mapping.ini`

        This file is used to control the |RCE| indexer. It comes configured
        to index your instance. To change the default configuration, see
        :ref:`advanced-indexing`.

    \- **vcsserver.ini**
        Default location:
        :file:`/home/{user}/.rccontrol/{vcsserver-id}/vcsserver.ini`

        The VCS Server handles the connection between your |repos| and |RCE|.
        See the :ref:`vcs-server` section for configuration options and more
        detailed information.

    \- **supervisord.ini**
        Default location:
        :file:`/home/{user}/.rccontrol/supervisor/supervisord.ini`

        |RCC| uses Supervisor to monitor and manage installed instances of
        |RCE| and the VCS Server. |RCC| will manage this file completely,
        unless you install |RCE| in self-managed mode. For more information,
        see the :ref:`Supervisor Setup<control:supervisor-setup>` section.

    \- **.rccontrol.ini**
        Default location: :file:`/home/{user}/.rccontrol.ini`

        This file contains the instances that |RCC| starts at boot, which is all
        by default, but for more information, see
        the :ref:`Manually Start At Boot <control:set-start-boot>` section.

    \- **.rhoderc**
        Default location: :file:`/home/{user}/.rhoderc`

        This file is used by the |RCE| API when accessing an instance from a
        remote machine. The API checks this file for connection and
        authentication details. For more details, see the :ref:`config-rhoderc`
        section.

    \- **MANIFEST**
        Default location: :file:`/home/{user}/.rccontrol/cache/MANIFEST`

        |RCC| uses this file to source the latest available builds from the
        secure |RC| download channels. The only reason to mess with this file
        is if you need to do an offline installation,
        see the :ref:`Offline Installation<control:offline-installer-ref>`
        instructions, otherwise |RCC| will completely manage this file.

