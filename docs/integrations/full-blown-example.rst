.. _int-full-blown:

Extensions Extended Example
---------------------------

This example
:file:`/home/{user}/.rccontrol/{instance-id}/rcextensions/__init.py__` file
has been highlighted to show a Redmine integration in full. To extend your
|RCE| instances, use the below example to integrate with other
applications.

This example file also contains a Slack integration, but it is not
highlighted.


.. literalinclude:: example-ext.py
   :language: python
   :emphasize-lines: 186,193-198,210-218,474-496,648-660,749-760,810-822
   :linenos:
