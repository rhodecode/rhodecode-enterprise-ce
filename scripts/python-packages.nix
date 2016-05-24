{
  Babel = super.buildPythonPackage {
    name = "Babel-1.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pytz];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/B/Babel/Babel-1.3.tar.gz";
      md5 = "5264ceb02717843cbc9ffce8e6e06bdb";
    };
  };
  Beaker = super.buildPythonPackage {
    name = "Beaker-1.7.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/B/Beaker/Beaker-1.7.0.tar.gz";
      md5 = "386be3f7fe427358881eee4622b428b3";
    };
  };
  CProfileV = super.buildPythonPackage {
    name = "CProfileV-1.0.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [bottle];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/C/CProfileV/CProfileV-1.0.6.tar.gz";
      md5 = "08c7c242b6e64237bc53c5d13537e03d";
    };
  };
  Cython = super.buildPythonPackage {
    name = "Cython-0.22";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/C/Cython/cython-0.22.tar.gz";
      md5 = "1ae25add4ef7b63ee9b4af697300d6b6";
    };
  };
  Fabric = super.buildPythonPackage {
    name = "Fabric-1.10.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [paramiko];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/F/Fabric/Fabric-1.10.0.tar.gz";
      md5 = "2cb96473387f0e7aa035210892352f4a";
    };
  };
  FormEncode = super.buildPythonPackage {
    name = "FormEncode-1.2.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/F/FormEncode/FormEncode-1.2.4.tar.gz";
      md5 = "6bc17fb9aed8aea198975e888e2077f4";
    };
  };
  Jinja2 = super.buildPythonPackage {
    name = "Jinja2-2.7.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [MarkupSafe];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/J/Jinja2/Jinja2-2.7.3.tar.gz";
      md5 = "b9dffd2f3b43d673802fe857c8445b1a";
    };
  };
  Mako = super.buildPythonPackage {
    name = "Mako-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [MarkupSafe];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/M/Mako/Mako-1.0.1.tar.gz";
      md5 = "9f0aafd177b039ef67b90ea350497a54";
    };
  };
  Markdown = super.buildPythonPackage {
    name = "Markdown-2.6.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/M/Markdown/Markdown-2.6.2.tar.gz";
      md5 = "256d19afcc564dc4ce4c229bb762f7ae";
    };
  };
  MarkupSafe = super.buildPythonPackage {
    name = "MarkupSafe-0.23";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/M/MarkupSafe/MarkupSafe-0.23.tar.gz";
      md5 = "f5ab3deee4c37cd6a922fb81e730da6e";
    };
  };
  MySQL-python = super.buildPythonPackage {
    name = "MySQL-python-1.2.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/M/MySQL-python/MySQL-python-1.2.5.zip";
      md5 = "654f75b302db6ed8dc5a898c625e030c";
    };
  };
  Paste = super.buildPythonPackage {
    name = "Paste-2.0.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/P/Paste/Paste-2.0.2.tar.gz";
      md5 = "4bfc8a7eaf858f6309d2ac0f40fc951c";
    };
  };
  PasteDeploy = super.buildPythonPackage {
    name = "PasteDeploy-1.5.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/P/PasteDeploy/PasteDeploy-1.5.2.tar.gz";
      md5 = "352b7205c78c8de4987578d19431af3b";
    };
  };
  PasteScript = super.buildPythonPackage {
    name = "PasteScript-1.7.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [Paste PasteDeploy];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/P/PasteScript/PasteScript-1.7.5.tar.gz";
      md5 = "4c72d78dcb6bb993f30536842c16af4d";
    };
  };
  Pygments = super.buildPythonPackage {
    name = "Pygments-2.0.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/P/Pygments/Pygments-2.0.2.tar.gz";
      md5 = "238587a1370d62405edabd0794b3ec4a";
    };
  };
  Pylons = super.buildPythonPackage {
    name = "Pylons-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [Routes WebHelpers Beaker Paste PasteDeploy PasteScript FormEncode simplejson decorator nose Mako WebError WebTest Tempita MarkupSafe WebOb];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/P/Pylons/Pylons-1.0.1.tar.gz";
      md5 = "6cb880d75fa81213192142b07a6e4915";
    };
  };
  Pyro4 = super.buildPythonPackage {
    name = "Pyro4-4.41";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [serpent];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/P/Pyro4/Pyro4-4.41.tar.gz";
      md5 = "ed69e9bfafa9c06c049a87cb0c4c2b6c";
    };
  };
  RhodeCodeEnterprise = super.buildPythonPackage {
    name = "RhodeCodeEnterprise-3.9.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [Babel Beaker FormEncode Mako Markdown MarkupSafe Paste PasteDeploy PasteScript Pygments Pylons Pyro4 Routes SQLAlchemy Tempita URLObject WebError WebHelpers WebOb WebTest Whoosh amqplib anyjson backport-ipaddress celery decorator docutils kombu mercurial packaging pycrypto pyparsing python-dateutil recaptcha-client repoze.lru requests simplejson waitress zope.cachedescriptors py-bcrypt psutil];
    src = ./../..;
  };
  Routes = super.buildPythonPackage {
    name = "Routes-1.13";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [repoze.lru];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/R/Routes/Routes-1.13.tar.gz";
      md5 = "d527b0ab7dd9172b1275a41f97448783";
    };
  };
  SQLAlchemy = super.buildPythonPackage {
    name = "SQLAlchemy-0.9.9";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/S/SQLAlchemy/SQLAlchemy-0.9.9.tar.gz";
      md5 = "8a10a9bd13ed3336ef7333ac2cc679ff";
    };
  };
  Sphinx = super.buildPythonPackage {
    name = "Sphinx-1.2.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [Pygments docutils Jinja2];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/S/Sphinx/Sphinx-1.2.2.tar.gz";
      md5 = "3dc73ccaa8d0bfb2d62fb671b1f7e8a4";
    };
  };
  Tempita = super.buildPythonPackage {
    name = "Tempita-0.5.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/T/Tempita/Tempita-0.5.2.tar.gz";
      md5 = "4c2f17bb9d481821c41b6fbee904cea1";
    };
  };
  URLObject = super.buildPythonPackage {
    name = "URLObject-2.4.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/U/URLObject/URLObject-2.4.0.tar.gz";
      md5 = "2ed819738a9f0a3051f31dc9924e3065";
    };
  };
  WebError = super.buildPythonPackage {
    name = "WebError-0.10.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [WebOb Tempita Pygments Paste];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/W/WebError/WebError-0.10.3.tar.gz";
      md5 = "84b9990b0baae6fd440b1e60cdd06f9a";
    };
  };
  WebHelpers = super.buildPythonPackage {
    name = "WebHelpers-1.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [MarkupSafe];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/W/WebHelpers/WebHelpers-1.3.tar.gz";
      md5 = "32749ffadfc40fea51075a7def32588b";
    };
  };
  WebHelpers2 = super.buildPythonPackage {
    name = "WebHelpers2-2.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [MarkupSafe six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/W/WebHelpers2/WebHelpers2-2.0.tar.gz";
      md5 = "0f6b68d70c12ee0aed48c00b24da13d3";
    };
  };
  WebOb = super.buildPythonPackage {
    name = "WebOb-1.3.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/W/WebOb/WebOb-1.3.1.tar.gz";
      md5 = "20918251c5726956ba8fef22d1556177";
    };
  };
  WebTest = super.buildPythonPackage {
    name = "WebTest-1.4.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [WebOb];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/W/WebTest/WebTest-1.4.3.zip";
      md5 = "631ce728bed92c681a4020a36adbc353";
    };
  };
  Whoosh = super.buildPythonPackage {
    name = "Whoosh-2.7.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/W/Whoosh/Whoosh-2.7.0.tar.gz";
      md5 = "9a0fc2df9335e1d2e81dd84a2c4c416f";
    };
  };
  alembic = super.buildPythonPackage {
    name = "alembic-0.8.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [SQLAlchemy Mako python-editor];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/a/alembic/alembic-0.8.4.tar.gz";
      md5 = "5f95d8ee62b443f9b37eb5bee76c582d";
    };
  };
  amqplib = super.buildPythonPackage {
    name = "amqplib-1.0.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/a/amqplib/amqplib-1.0.2.tgz";
      md5 = "5c92f17fbedd99b2b4a836d4352d1e2f";
    };
  };
  anyjson = super.buildPythonPackage {
    name = "anyjson-0.3.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/a/anyjson/anyjson-0.3.3.tar.gz";
      md5 = "2ea28d6ec311aeeebaf993cb3008b27c";
    };
  };
  appenlight-client = super.buildPythonPackage {
    name = "appenlight-client-0.6.14";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [WebOb requests];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/a/appenlight-client/appenlight_client-0.6.14.tar.gz";
      md5 = "578c69b09f4356d898fff1199b98a95c";
    };
  };
  backport-ipaddress = super.buildPythonPackage {
    name = "backport-ipaddress-0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/b/backport_ipaddress/backport_ipaddress-0.1.tar.gz";
      md5 = "9c1f45f4361f71b124d7293a60006c05";
    };
  };
  bottle = super.buildPythonPackage {
    name = "bottle-0.12.8";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/b/bottle/bottle-0.12.8.tar.gz";
      md5 = "13132c0a8f607bf860810a6ee9064c5b";
    };
  };
  bumpversion = super.buildPythonPackage {
    name = "bumpversion-0.5.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/b/bumpversion/bumpversion-0.5.3.tar.gz";
      md5 = "c66a3492eafcf5ad4b024be9fca29820";
    };
  };
  celery = super.buildPythonPackage {
    name = "celery-2.2.10";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [python-dateutil anyjson kombu pyparsing];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/c/celery/celery-2.2.10.tar.gz";
      md5 = "898bc87e54f278055b561316ba73e222";
    };
  };
  channelstream = super.buildPythonPackage {
    name = "channelstream-0.4.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [gevent gevent-websocket pyramid pyramid-jinja2 itsdangerous];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/c/channelstream/channelstream-0.4.2.tar.gz";
      md5 = "5857cc2b1cef993088817ccc31285254";
    };
  };
  click = super.buildPythonPackage {
    name = "click-4.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/c/click/click-4.0.tar.gz";
      md5 = "79b475a1dbd566d8ce7daba5e6c1aaa7";
    };
  };
  colander = super.buildPythonPackage {
    name = "colander-1.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [translationstring iso8601];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/c/colander/colander-1.2.tar.gz";
      md5 = "83db21b07936a0726e588dae1914b9ed";
    };
  };
  configobj = super.buildPythonPackage {
    name = "configobj-5.0.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [six];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/c/configobj/configobj-5.0.6.tar.gz";
      md5 = "e472a3a1c2a67bb0ec9b5d54c13a47d6";
    };
  };
  cov-core = super.buildPythonPackage {
    name = "cov-core-1.15.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [coverage];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/c/cov-core/cov-core-1.15.0.tar.gz";
      md5 = "f519d4cb4c4e52856afb14af52919fe6";
    };
  };
  coverage = super.buildPythonPackage {
    name = "coverage-3.7.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/c/coverage/coverage-3.7.1.tar.gz";
      md5 = "c47b36ceb17eaff3ecfab3bcd347d0df";
    };
  };
  cssselect = super.buildPythonPackage {
    name = "cssselect-0.9.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/c/cssselect/cssselect-0.9.1.tar.gz";
      md5 = "c74f45966277dc7a0f768b9b0f3522ac";
    };
  };
  decorator = super.buildPythonPackage {
    name = "decorator-3.4.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/d/decorator/decorator-3.4.2.tar.gz";
      md5 = "9e0536870d2b83ae27d58dbf22582f4d";
    };
  };
  docutils = super.buildPythonPackage {
    name = "docutils-0.12";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/d/docutils/docutils-0.12.tar.gz";
      md5 = "4622263b62c5c771c03502afa3157768";
    };
  };
  dogpile.cache = super.buildPythonPackage {
    name = "dogpile.cache-0.5.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [dogpile.core];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/d/dogpile.cache/dogpile.cache-0.5.7.tar.gz";
      md5 = "3e58ce41af574aab41d78e9c4190f194";
    };
  };
  dogpile.core = super.buildPythonPackage {
    name = "dogpile.core-0.4.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/d/dogpile.core/dogpile.core-0.4.1.tar.gz";
      md5 = "01cb19f52bba3e95c9b560f39341f045";
    };
  };
  dulwich = super.buildPythonPackage {
    name = "dulwich-0.12.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/d/dulwich/dulwich-0.12.0.tar.gz";
      md5 = "f3a8a12bd9f9dd8c233e18f3d49436fa";
    };
  };
  ecdsa = super.buildPythonPackage {
    name = "ecdsa-0.11";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/e/ecdsa/ecdsa-0.11.tar.gz";
      md5 = "8ef586fe4dbb156697d756900cb41d7c";
    };
  };
  flake8 = super.buildPythonPackage {
    name = "flake8-2.4.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyflakes pep8 mccabe];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/f/flake8/flake8-2.4.1.tar.gz";
      md5 = "ed45d3db81a3b7c88bd63c6e37ca1d65";
    };
  };
  future = super.buildPythonPackage {
    name = "future-0.14.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/f/future/future-0.14.3.tar.gz";
      md5 = "e94079b0bd1fc054929e8769fc0f6083";
    };
  };
  futures = super.buildPythonPackage {
    name = "futures-3.0.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/f/futures/futures-3.0.2.tar.gz";
      md5 = "42aaf1e4de48d6e871d77dc1f9d96d5a";
    };
  };
  gevent = super.buildPythonPackage {
    name = "gevent-1.0.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [greenlet];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/g/gevent/gevent-1.0.2.tar.gz";
      md5 = "117f135d57ca7416203fba3720bf71c1";
    };
  };
  gevent-websocket = super.buildPythonPackage {
    name = "gevent-websocket-0.9.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [gevent];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/g/gevent-websocket/gevent-websocket-0.9.5.tar.gz";
      md5 = "03a8473b9a61426b0ef6094319141389";
    };
  };
  gnureadline = super.buildPythonPackage {
    name = "gnureadline-6.3.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/g/gnureadline/gnureadline-6.3.3.tar.gz";
      md5 = "c4af83c9a3fbeac8f2da9b5a7c60e51c";
    };
  };
  gprof2dot = super.buildPythonPackage {
    name = "gprof2dot-2015.12.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/g/gprof2dot/gprof2dot-2015.12.1.tar.gz";
      md5 = "e23bf4e2f94db032750c193384b4165b";
    };
  };
  greenlet = super.buildPythonPackage {
    name = "greenlet-0.4.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/g/greenlet/greenlet-0.4.7.zip";
      md5 = "c2333a8ff30fa75c5d5ec0e67b461086";
    };
  };
  gunicorn = super.buildPythonPackage {
    name = "gunicorn-19.3.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/g/gunicorn/gunicorn-19.3.0.tar.gz";
      md5 = "faa3e80661efd67e5e06bba32699af20";
    };
  };
  infrae.cache = super.buildPythonPackage {
    name = "infrae.cache-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [Beaker repoze.lru];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/i/infrae.cache/infrae.cache-1.0.1.tar.gz";
      md5 = "b09076a766747e6ed2a755cc62088e32";
    };
  };
  invoke = super.buildPythonPackage {
    name = "invoke-0.11.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/i/invoke/invoke-0.11.1.tar.gz";
      md5 = "3d4ecbe26779ceef1046ecf702c9c4a8";
    };
  };
  ipdb = super.buildPythonPackage {
    name = "ipdb-0.8";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [ipython];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/i/ipdb/ipdb-0.8.zip";
      md5 = "96dca0712efa01aa5eaf6b22071dd3ed";
    };
  };
  ipython = super.buildPythonPackage {
    name = "ipython-3.1.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [gnureadline];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/i/ipython/ipython-3.1.0.tar.gz";
      md5 = "a749d90c16068687b0ec45a27e72ef8f";
    };
  };
  iso8601 = super.buildPythonPackage {
    name = "iso8601-0.1.11";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/i/iso8601/iso8601-0.1.11.tar.gz";
      md5 = "b06d11cd14a64096f907086044f0fe38";
    };
  };
  itsdangerous = super.buildPythonPackage {
    name = "itsdangerous-0.24";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/i/itsdangerous/itsdangerous-0.24.tar.gz";
      md5 = "a3d55aa79369aef5345c036a8a26307f";
    };
  };
  kombu = super.buildPythonPackage {
    name = "kombu-1.5.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [anyjson amqplib];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/k/kombu/kombu-1.5.1.tar.gz";
      md5 = "50662f3c7e9395b3d0721fb75d100b63";
    };
  };
  lxml = super.buildPythonPackage {
    name = "lxml-3.4.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/l/lxml/lxml-3.4.4.tar.gz";
      md5 = "a9a65972afc173ec7a39c585f4eea69c";
    };
  };
  mccabe = super.buildPythonPackage {
    name = "mccabe-0.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/m/mccabe/mccabe-0.3.tar.gz";
      md5 = "81640948ff226f8c12b3277059489157";
    };
  };
  meld3 = super.buildPythonPackage {
    name = "meld3-1.0.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/m/meld3/meld3-1.0.2.tar.gz";
      md5 = "3ccc78cd79cffd63a751ad7684c02c91";
    };
  };
  mercurial = super.buildPythonPackage {
    name = "mercurial-3.3.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/M/Mercurial/mercurial-3.3.3.tar.gz";
      md5 = "8648a6980fc12a5a424abe809ab4c6e5";
    };
  };
  mock = super.buildPythonPackage {
    name = "mock-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/m/mock/mock-1.0.1.tar.gz";
      md5 = "c3971991738caa55ec7c356bbc154ee2";
    };
  };
  msgpack-python = super.buildPythonPackage {
    name = "msgpack-python-0.4.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/m/msgpack-python/msgpack-python-0.4.6.tar.gz";
      md5 = "8b317669314cf1bc881716cccdaccb30";
    };
  };
  nose = super.buildPythonPackage {
    name = "nose-1.3.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/n/nose/nose-1.3.6.tar.gz";
      md5 = "0ca546d81ca8309080fc80cb389e7a16";
    };
  };
  objgraph = super.buildPythonPackage {
    name = "objgraph-2.0.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/o/objgraph/objgraph-2.0.0.tar.gz";
      md5 = "25b0d5e5adc74aa63ead15699614159c";
    };
  };
  packaging = super.buildPythonPackage {
    name = "packaging-15.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/packaging/packaging-15.2.tar.gz";
      md5 = "c16093476f6ced42128bf610e5db3784";
    };
  };
  paramiko = super.buildPythonPackage {
    name = "paramiko-1.15.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pycrypto ecdsa];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/paramiko/paramiko-1.15.1.tar.gz";
      md5 = "48c274c3f9b1282932567b21f6acf3b5";
    };
  };
  pep8 = super.buildPythonPackage {
    name = "pep8-1.5.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pep8/pep8-1.5.7.tar.gz";
      md5 = "f6adbdd69365ecca20513c709f9b7c93";
    };
  };
  psutil = super.buildPythonPackage {
    name = "psutil-2.2.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/psutil/psutil-2.2.1.tar.gz";
      md5 = "1a2b58cd9e3a53528bb6148f0c4d5244";
    };
  };
  psycopg2 = super.buildPythonPackage {
    name = "psycopg2-2.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/psycopg2/psycopg2-2.6.tar.gz";
      md5 = "fbbb039a8765d561a1c04969bbae7c74";
    };
  };
  py = super.buildPythonPackage {
    name = "py-1.4.29";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/py/py-1.4.29.tar.gz";
      md5 = "c28e0accba523a29b35a48bb703fb96c";
    };
  };
  py-bcrypt = super.buildPythonPackage {
    name = "py-bcrypt-0.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/py-bcrypt/py-bcrypt-0.4.tar.gz";
      md5 = "dd8b367d6b716a2ea2e72392525f4e36";
    };
  };
  pycrypto = super.buildPythonPackage {
    name = "pycrypto-2.6.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pycrypto/pycrypto-2.6.1.tar.gz";
      md5 = "55a61a054aa66812daf5161a0d5d7eda";
    };
  };
  pycurl = super.buildPythonPackage {
    name = "pycurl-7.19.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pycurl/pycurl-7.19.5.tar.gz";
      md5 = "47b4eac84118e2606658122104e62072";
    };
  };
  pyflakes = super.buildPythonPackage {
    name = "pyflakes-0.8.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pyflakes/pyflakes-0.8.1.tar.gz";
      md5 = "905fe91ad14b912807e8fdc2ac2e2c23";
    };
  };
  pyparsing = super.buildPythonPackage {
    name = "pyparsing-1.5.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pyparsing/pyparsing-1.5.7.tar.gz";
      md5 = "9be0fcdcc595199c646ab317c1d9a709";
    };
  };
  pyramid = super.buildPythonPackage {
    name = "pyramid-1.5.7";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools WebOb repoze.lru zope.interface zope.deprecation venusian translationstring PasteDeploy];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pyramid/pyramid-1.5.7.tar.gz";
      md5 = "179437d1c331e720df50fb4e7428ed6b";
    };
  };
  pyramid-jinja2 = super.buildPythonPackage {
    name = "pyramid-jinja2-2.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyramid zope.deprecation Jinja2 MarkupSafe];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pyramid_jinja2/pyramid_jinja2-2.5.tar.gz";
      md5 = "07cb6547204ac5e6f0b22a954ccee928";
    };
  };
  pyramid-mako = super.buildPythonPackage {
    name = "pyramid-mako-1.0.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pyramid Mako];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pyramid_mako/pyramid_mako-1.0.2.tar.gz";
      md5 = "ee25343a97eb76bd90abdc2a774eb48a";
    };
  };
  pysqlite = super.buildPythonPackage {
    name = "pysqlite-2.6.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pysqlite/pysqlite-2.6.3.tar.gz";
      md5 = "7ff1cedee74646b50117acff87aa1cfa";
    };
  };
  pytest = super.buildPythonPackage {
    name = "pytest-2.8.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [py];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pytest/pytest-2.8.5.zip";
      md5 = "8493b06f700862f1294298d6c1b715a9";
    };
  };
  pytest-catchlog = super.buildPythonPackage {
    name = "pytest-catchlog-1.2.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [py pytest];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pytest-catchlog/pytest-catchlog-1.2.2.zip";
      md5 = "09d890c54c7456c818102b7ff8c182c8";
    };
  };
  pytest-cov = super.buildPythonPackage {
    name = "pytest-cov-1.8.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [py pytest coverage cov-core];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pytest-cov/pytest-cov-1.8.1.tar.gz";
      md5 = "76c778afa2494088270348be42d759fc";
    };
  };
  pytest-profiling = super.buildPythonPackage {
    name = "pytest-profiling-1.0.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [six pytest gprof2dot];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pytest-profiling/pytest-profiling-1.0.1.tar.gz";
      md5 = "354404eb5b3fd4dc5eb7fffbb3d9b68b";
    };
  };
  pytest-timeout = super.buildPythonPackage {
    name = "pytest-timeout-0.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [pytest];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pytest-timeout/pytest-timeout-0.4.tar.gz";
      md5 = "03b28aff69cbbfb959ed35ade5fde262";
    };
  };
  python-dateutil = super.buildPythonPackage {
    name = "python-dateutil-1.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/python-dateutil/python-dateutil-1.5.tar.gz";
      md5 = "0dcb1de5e5cad69490a3b6ab63f0cfa5";
    };
  };
  python-editor = super.buildPythonPackage {
    name = "python-editor-0.5";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/python-editor/python-editor-0.5.tar.gz";
      md5 = "ece4f1848d93286d58df88e3fcb37704";
    };
  };
  python-ldap = super.buildPythonPackage {
    name = "python-ldap-2.4.19";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/python-ldap/python-ldap-2.4.19.tar.gz";
      md5 = "b941bf31d09739492aa19ef679e94ae3";
    };
  };
  pytz = super.buildPythonPackage {
    name = "pytz-2015.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pytz/pytz-2015.4.tar.bz2";
      md5 = "39f7375c4b1fa34cdcb4b4765d08f817";
    };
  };
  pyzmq = super.buildPythonPackage {
    name = "pyzmq-14.6.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/p/pyzmq/pyzmq-14.6.0.tar.gz";
      md5 = "395b5de95a931afa5b14c9349a5b8024";
    };
  };
  recaptcha-client = super.buildPythonPackage {
    name = "recaptcha-client-1.0.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/r/recaptcha-client/recaptcha-client-1.0.6.tar.gz";
      md5 = "74228180f7e1fb76c4d7089160b0d919";
    };
  };
  repoze.lru = super.buildPythonPackage {
    name = "repoze.lru-0.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/r/repoze.lru/repoze.lru-0.6.tar.gz";
      md5 = "2c3b64b17a8e18b405f55d46173e14dd";
    };
  };
  requests = super.buildPythonPackage {
    name = "requests-2.9.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/r/requests/requests-2.9.1.tar.gz";
      md5 = "0b7f480d19012ec52bab78292efd976d";
    };
  };
  serpent = super.buildPythonPackage {
    name = "serpent-1.11";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/serpent/serpent-1.11.tar.gz";
      md5 = "8d72e90f84631b3ffcb665d74b99a78f";
    };
  };
  setproctitle = super.buildPythonPackage {
    name = "setproctitle-1.1.8";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/setproctitle/setproctitle-1.1.8.tar.gz";
      md5 = "728f4c8c6031bbe56083a48594027edd";
    };
  };
  setuptools = super.buildPythonPackage {
    name = "setuptools-20.1.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/setuptools/setuptools-20.1.1.tar.gz";
      md5 = "10a0f4feb9f2ea99acf634c8d7136d6d";
    };
  };
  simplejson = super.buildPythonPackage {
    name = "simplejson-3.7.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/simplejson/simplejson-3.7.2.tar.gz";
      md5 = "a5fc7d05d4cb38492285553def5d4b46";
    };
  };
  six = super.buildPythonPackage {
    name = "six-1.9.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/six/six-1.9.0.tar.gz";
      md5 = "476881ef4012262dfc8adc645ee786c4";
    };
  };
  subprocess32 = super.buildPythonPackage {
    name = "subprocess32-3.2.6";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/subprocess32/subprocess32-3.2.6.tar.gz";
      md5 = "754c5ab9f533e764f931136974b618f1";
    };
  };
  supervisor = super.buildPythonPackage {
    name = "supervisor-3.1.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [meld3];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/s/supervisor/supervisor-3.1.3.tar.gz";
      md5 = "aad263c4fbc070de63dd354864d5e552";
    };
  };
  transifex-client = super.buildPythonPackage {
    name = "transifex-client-0.10";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/transifex-client/transifex-client-0.10.tar.gz";
      md5 = "5549538d84b8eede6b254cd81ae024fa";
    };
  };
  translationstring = super.buildPythonPackage {
    name = "translationstring-1.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/translationstring/translationstring-1.1.tar.gz";
      md5 = "0979b46d8f0f852810c8ec4be5c26cf2";
    };
  };
  trollius = super.buildPythonPackage {
    name = "trollius-1.0.4";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [futures];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/t/trollius/trollius-1.0.4.tar.gz";
      md5 = "3631a464d49d0cbfd30ab2918ef2b783";
    };
  };
  uWSGI = super.buildPythonPackage {
    name = "uWSGI-2.0.11.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/u/uWSGI/uwsgi-2.0.11.2.tar.gz";
      md5 = "1f02dcbee7f6f61de4b1fd68350cf16f";
    };
  };
  venusian = super.buildPythonPackage {
    name = "venusian-1.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/v/venusian/venusian-1.0.tar.gz";
      md5 = "dccf2eafb7113759d60c86faf5538756";
    };
  };
  waitress = super.buildPythonPackage {
    name = "waitress-0.8.9";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/w/waitress/waitress-0.8.9.tar.gz";
      md5 = "da3f2e62b3676be5dd630703a68e2a04";
    };
  };
  wsgiref = super.buildPythonPackage {
    name = "wsgiref-0.1.2";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/w/wsgiref/wsgiref-0.1.2.zip";
      md5 = "29b146e6ebd0f9fb119fe321f7bcf6cb";
    };
  };
  zope.cachedescriptors = super.buildPythonPackage {
    name = "zope.cachedescriptors-4.0.0";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/z/zope.cachedescriptors/zope.cachedescriptors-4.0.0.tar.gz";
      md5 = "8d308de8c936792c8e758058fcb7d0f0";
    };
  };
  zope.deprecation = super.buildPythonPackage {
    name = "zope.deprecation-4.1.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/z/zope.deprecation/zope.deprecation-4.1.1.tar.gz";
      md5 = "ce261b9384066f7e13b63525778430cb";
    };
  };
  zope.event = super.buildPythonPackage {
    name = "zope.event-4.0.3";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/z/zope.event/zope.event-4.0.3.tar.gz";
      md5 = "9a3780916332b18b8b85f522bcc3e249";
    };
  };
  zope.interface = super.buildPythonPackage {
    name = "zope.interface-4.1.1";
    buildInputs = with self; [];
    doCheck = false;
    propagatedBuildInputs = with self; [setuptools];
    src = fetchurl {
      url = "https://pypi.python.org/packages/source/z/zope.interface/zope.interface-4.1.1.tar.gz";
      md5 = "edcd5f719c5eb2e18894c4d06e29b6c6";
    };
  };

### Test requirements


}
