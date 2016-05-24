.. _hg-auth-loop:

|hg| Authentication Tuning
--------------------------

When using external authentication tools such as LDAP with |hg|, a
password retry loop in |hg| can result in users being locked out due to too
many failed password attempts. To prevent this from happening, add the
following setting to your
:file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file, in the
``[app:main]`` section.


.. code-block:: ini

   [app:main]
   auth_ret_code_detection = true
