.. _set-up-mail:

Set up Email
------------

To setup email with your |RCM| instance, open the default
:file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini`
file and uncomment and configure the email section. If it is not there,
use the below example to insert it.

Once configured you can check the settings for your |RCM| instance on the
:menuselection:`Admin --> Settings --> Email` page.

.. code-block:: ini

    ################################################################################
    ## Uncomment and replace with the email address which should receive          ##
    ## any error reports after an application crash                               ##
    ## Additionally these settings will be used by the RhodeCode mailing system   ##
    ################################################################################
    #email_to = admin@localhost
    #error_email_from = paste_error@localhost
    #app_email_from = rhodecode-noreply@localhost
    #error_message =
    #email_prefix = [RhodeCode]

    #smtp_server = mail.server.com
    #smtp_username =
    #smtp_password =
    #smtp_port =
    #smtp_use_tls = false
    #smtp_use_ssl = true
    ## Specify available auth parameters here (e.g. LOGIN PLAIN CRAM-MD5, etc.)
    #smtp_auth =
