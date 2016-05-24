.. _per-repo-vcs:

Repository VCS Settings
=======================

You can configure |repo| VCS (Version Control System) settings at a global
level, and individually per |repo|. Global settings are applied by default.
If you configure individual settings per |repo|, these will remain unaffected
by any subsequent global changes.

Set Global Repository Settings
------------------------------

To configure |repo| settings across your |RCE| instance use the following steps:

1. Go to to the :menuselection:`Admin --> Settings --> VCS` page.
2. Configure the following |repo| options:

    * :guilabel:`Web`: Require SSL if necessary.
    * :guilabel:`Hooks`: Enable built in hooks.
    * :guilabel:`Mercurial Settings`: Configure |hg| specific settings.
    * :guilabel:`Repositories Location`: Set the file system |repos| location.
    * :guilabel:`Subversion Settings`: Configure |svn| specific settings.
    * :guilabel:`Pull Request Settings`: Enable the listed additional |pr|
      features.

3. Click :guilabel:`Save`.


Set Individual Repository Settings
----------------------------------

To configure specific VCS settings for an individual |repo|, use the following
steps:

1. Go to to the :menuselection:`Admin --> Repositories --> Edit --> VCS` page.
2. Uncheck the :guilabel:`Inherit from global settings` box.
3. Configure the following |repo| options:

    * :guilabel:`Hooks`: Enable built in hooks.
    * :guilabel:`Mercurial Settings` (|hg| Only): Configure |hg| specific
      settings.
    * :guilabel:`Subversion Settings` (|svn| Only): Configure |svn| specific
      settings.
    * :guilabel:`Pull Request Settings` (|git| and |hg| Only): Enable the
      listed additional |pr| features.

3. Click :guilabel:`Save`.
