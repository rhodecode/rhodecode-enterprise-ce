|RCE| 3.6.1 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

* 2015-10-19

Security
^^^^^^^^

* HTTP response splitting on login redirection has been secured to
  prevent header injection.

Fixes
^^^^^

* Alphabetically sort the external license dependencies overview for quicker
  reading.
* Change directory permissions checks for Windows.
* Fixed a login redirection issue when using a custom prefix to improve the
  user experience when using a proxy server.
* Skip reading |repos| with names that contain special characters.
