.. _rhodecode-nix-ref:

Nix Packaging
=============

|RCM| is installed using |Nix Package Manager|. The Nix environment provides
the following features for maintenance and deployment:

* Atomic upgrades and rollbacks
* Complete dependency management
* Garbage collection
* Binary patching
* Secure channel updates
* Nix works on Windows, Linux, and OSX

The complete list of dependencies can be found in
:file:`/opt/rhodecode/store/{unique-hash}`.

.. note::

   No |RCE| data is stored in this location.
   
.. warning::

   Never alter any of the packages in the store. Always use the
   :ref:`RhodeCode Control CLI <control:rcc-cli>` update functions to keep
   the packages and instances updated.

.. |Nix Package Manager| raw:: html

   <a href="http://nixos.org/nix/" target="_blank">Nix</a>
