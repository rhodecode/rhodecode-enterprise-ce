.. _clean-up-cmds:

|RCT| Clean Up Commands
=======================

|RCT| comes with a number of functions which can be used to administer your
|RCE| instances. Two of these can be used to automate the cleanup of gists
and |repos|

rhodecode-cleanup-gists
-----------------------

Use this command to delete gists within RhodeCode Enterprise. It takes a
number of options for specifying the kind of gists you want deleted, and it
is possible to run these commands from a cron job or cleanup script. For more
information, see the :ref:`tools-cli`

rhodecode-cleanup-repos
-----------------------

Use this command to delete |repos| from your |RCE| instances. It takes
a number of options specifying the kind of |repos| you want deleted. For more
information, see the :ref:`tools-cli`
