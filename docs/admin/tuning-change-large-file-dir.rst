.. _hg-lrg-loc:

Change the |hg| Large Files Location
------------------------------------

|RCE| manages |hg| larges files from the following default location
:file:`/home/{user}/repos/.cache/largefiles`. If you wish to change this, use
the following steps:

1. Open ishell from the terminal and use it to log into the |RCE| database by
   specifying the instance :file:`rhodecode.ini` file.

.. code-block:: bash

    # Open iShell from the terminal and set ini file
    $ .rccontrol/enterprise-1/profile/bin/paster ishell .rccontrol/enterprise-1/rhodecode.ini

2. Run the following commands, and ensure that |RCE| has write access to the
   new directory:

.. code-block:: mysql

    # Once logged into the database, use SQL to redirect
    # the large files location
    In [1]: from rhodecode.model.settings import SettingsModel
    In [2]: SettingsModel().get_ui_by_key('usercache')
    Out[2]: <RhodeCodeUi[largefiles]usercache=>/mnt/hgfs/shared/workspace/xxxx/.cache/largefiles]>

    In [3]: largefiles_cache = SettingsModel().get_ui_by_key('usercache')
    In [4]: largefiles_cache.ui_value = '/new/path’
    In [5]: Session().add(largefiles_cache);Session().commit()

