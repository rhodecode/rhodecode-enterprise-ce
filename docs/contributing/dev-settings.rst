
==========================
 Settings for Development
==========================


We have a few settings which are intended to be used only for development
purposes. This section contains an overview of them.



`debug_style`
=============

Enables the section "Style" in the application. This section provides an
overview of all components which are found in the frontend of the
application.



`vcs.start_server`
==================

Starts the server as a subprocess while the system comes up. Intended usage is
to ease development.



`[logging]`
===========

Use this to configure logging to your current needs. The documentation of
Python's `logging` module explains all of the details. The following snippets
are useful for day to day development work.


Mute SQL output
---------------

They come out of the package `sqlalchemy.engine`::

  [logger_sqlalchemy]
  level = WARNING
  handlers = console_sql
  qualname = sqlalchemy.engine
  propagate = 0
