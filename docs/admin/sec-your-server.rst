.. _sec-your-server:

Securing Your Server
--------------------

|RCE| runs on your hardware, and while it is developed with security in mind
it is also important that you ensure your servers are well secured. In this
section we will cover some basic security practices that are best to
configure when setting up your |RCE| instances.

SSH Keys
^^^^^^^^

Using SSH keys to access your server provides more security than using the
standard username and password combination. To set up your SSH Keys, use the
following steps:

1. On your local machine create the public/private key combination. The
   private key you will keep, and the matching public key is copied to the
   server. Setting a passphrase here is optional, if you set one you will
   always be prompted for it when logging in.

.. code-block:: bash

    # Generate SSH Keys
    user@ubuntu:~$ ssh-keygen -t rsa

.. code-block:: bash

    Generating public/private rsa key pair.
    Enter file in which to save the key (/home/user/.ssh/id_rsa):
    Created directory '/home/user/.ssh'.
    Enter passphrase (empty for no passphrase):
    Enter same passphrase again:
    Your identification has been saved in /home/user/.ssh/id_rsa.
    Your public key has been saved in /home/user/.ssh/id_rsa.pub.
    The key fingerprint is:
    02:82:38:95:e5:30:d2:ad:17:60:15:7f:94:17:9f:30 user@ubuntu
    The key's randomart image is:
    +--[ RSA 2048]----+

2. SFTP to your server, and copy the public key to the ``~/.ssh`` folder.

.. code-block:: bash

    # SFTP to your server
    $ sftp user@hostname

    # copy your public key
    sftp> mput /home/user/.ssh/id_rsa.pub /home/user/.ssh
    Uploading /home/user/.ssh/id_rsa.pub to /home/user/.ssh/id_rsa.pub
    /home/user/.ssh/id_rsa.pub      100%  394     0.4KB/s   00:00

3. On your server, add the public key to the :file:`~/.ssh/authorized_keys`
   file.

.. code-block:: bash

    $ cat /home/user/.ssh/id_rsa.pub > /home/user/.ssh/authorized_keys

You should now be able to log into your server using your SSH
Keys. If you've added a passphrase you'll be asked for it. For more
information about using SSH keys with |RCE| |repos|, see the
:ref:`ssh-connection` section.

VPN Whitelist
^^^^^^^^^^^^^

Most company networks will have a VPN. If you need to set one up, there are
many tutorials online for how to do that. Getting it right requires good
knowledge and attention to detail. Once set up, you can configure your
|RCE| instances to only allow user access from the VPN, to do this see the
:ref:`settip-ip-white` section.

Public Key Infrastructure and SSL/TLS Encryption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Public key infrastructure (PKI) is a system that creates, manages, and
validates certificates for identifying nodes on a network and encrypting
communication between them. SSL or TLS certificates can be used to
authenticate different entities with one another. To read more about PKIs,
see the `OpenSSL PKI tutorial`_ site, or this `Cloudflare PKI post`_.

If the network you are running is SSL/TLS encrypted, you can configure |RCE|
to always use secure connections using the ``force_https`` and ``use_htsts``
options in the :file:`/home/user/.rccontrol/instance-id/rhodecode.ini` file.
For more details, see the :ref:`x-frame` section.

FireWalls and Ports
^^^^^^^^^^^^^^^^^^^

Setting up a network firewall for your internal traffic is a good way
of keeping it secure by blocking off any ports that should not be used.
Additionally, you can set non-default ports for certain functions which adds
an extra layer of security to your setup.

A well configured firewall will restrict access to everything except the
services you need to remain open. By exposing fewer services you reduce the
number of potential vulnerabilities.

There are a number of different firewall solutions, but for most Linux systems
using the built in `IpTables`_ firewall should suffice. On BSD systems you
can use `IPFILTER`_ or `IPFW`_. Use the following examples, and the IpTables
documentation to configure your IP Tables on Ubuntu.

Changing the default SSH port.

.. code-block:: bash

    # Open SSH config file and change to port 10022
    vi /etc/ssh/sshd_config

    # What ports, IPs and protocols we listen for
    Port 10022

Setting IP Table rules for SSH traffic. It is important to note that the
default policy of your IpTables can differ and it is worth checking how each
is configured. The options are *ACCEPT*, *REJECT*, *DROP*, or *LOG*. The
usual practice is to block access on all ports and then enable access only on
the ports you with to expose.

.. code-block:: bash

    # Check iptables policy
    $ sudo iptables -L

    Chain INPUT (policy ACCEPT)
    target     prot opt source               destination

    Chain FORWARD (policy ACCEPT)
    target     prot opt source               destination

    Chain OUTPUT (policy ACCEPT)
    target     prot opt source               destination

    # Close all ports by default
    $ sudo iptables -P INPUT DROP

    $ sudo iptables -L
    Chain INPUT (policy DROP)
    target     prot opt source               destination
    DROP       all  --  anywhere             anywhere

    Chain FORWARD (policy ACCEPT)
    target     prot opt source               destination

    Chain OUTPUT (policy ACCEPT)
    target     prot opt source               destination

.. code-block:: bash

    # Deny outbound SSH traffic
    sudo iptables -A OUTPUT -p tcp --dport 10022 -j DROP

    # Allow incoming SSH traffic on port 10022
    sudo iptables -A INPUT -p tcp --dport 10022 -j ACCEPT

    # Allow incoming HTML traffic on port 80 and 443
    iptables -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT
    iptables -A INPUT -p tcp -m tcp --dport 443 -j ACCEPT

Saving your IP Table rules, and restoring them from file.

.. code-block:: bash

    # Save you IP Table Rules
    iptables-save

    # Save your IP Table Rules to a file
    sudo sh -c "iptables-save > /etc/iptables.rules"

    # Restore your IP Table rules from file
    iptables-restore < /etc/iptables.rules

.. _OpenSSL PKI tutorial: https://pki-tutorial.readthedocs.org/en/latest/#
.. _Cloudflare PKI post: https://blog.cloudflare.com/how-to-build-your-own-public-key-infrastructure/
.. _IpTables: https://help.ubuntu.com/community/IptablesHowTo
.. _IPFW: https://www.freebsd.org/doc/handbook/firewalls-ipfw.html
.. _IPFILTER: https://www.freebsd.org/doc/handbook/firewalls-ipf.html
