.. _db-session-ref:

Increase Database Performance
-----------------------------

To increase database performance switch to database-based user sessions.
File-based sessions are only suitable for smaller setups. The most common
issue being file limit errors which occur if there are lots of session files.
Therefore, in a large scale deployment, to give better performance,
scalability, and maintainability we recommend switching from file-based
sessions to database-based user sessions.

To switch to database-based user sessions uncomment the following section in
your :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file.

.. code-block:: ini

      # db session
      beaker.session.type = ext:database

      # adjust this property to include your database credentials
      beaker.session.sa.url = postgresql://postgres:<pass>@localhost/rhodecode
      beaker.session.table_name = db_session
