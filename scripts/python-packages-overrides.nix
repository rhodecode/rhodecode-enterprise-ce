# Overrides for the generated python-packages.nix
#
# This function is intended to be used as an extension to the generated file
# python-packages.nix. The main objective is to add needed dependencies of C
# libraries and tweak the build instructions where needed.

{ pkgs, basePythonPackages }:

let
  sed = "sed -i";
in

self: super: {

  kombu = super.kombu.override (attrs: {
    preConfigure = ''
      # Disable msgpack support to avoid conflict.
      # https://github.com/celery/kombu/pull/143/files
      #
      # This can be dropped once celery and kombu are updated to more
      # recent versions.
      ${sed} -e \
        's:msgpack.packs, msgpack.unpacks:msgpack.packb, msgpack.unpackb:' \
        kombu/serialization.py
    '';
  });

  lxml = super.lxml.override (attrs: {
    buildInputs = with self; [
      pkgs.libxml2
      pkgs.libxslt
    ];
  });

  mercurial = super.mercurial.override (attrs: {
    propagatedBuildInputs = attrs.propagatedBuildInputs ++ [
      self.python.modules.curses
    ] ++ pkgs.lib.optional pkgs.stdenv.isDarwin
      pkgs.darwin.apple_sdk.frameworks.ApplicationServices;
  });

  psutil = super.psutil.override (attrs: {
    buildInputs = attrs.buildInputs ++
      pkgs.lib.optional pkgs.stdenv.isDarwin pkgs.darwin.IOKit;
  });

  psycopg2 = super.psycopg2.override (attrs: {
    buildInputs = attrs.buildInputs ++
      pkgs.lib.optional pkgs.stdenv.isDarwin pkgs.openssl;
    propagatedBuildInputs = attrs.propagatedBuildInputs ++ [
      pkgs.postgresql
    ];
  });

  pycurl = super.pycurl.override (attrs: {
    propagatedBuildInputs = attrs.propagatedBuildInputs ++ [
      pkgs.curl
      pkgs.openssl
    ];
  });

  Pylons = super.Pylons.override (attrs: {
    name = "Pylons-1.0.1-patch1";
    src = pkgs.fetchgit {
      url = "https://code.rhodecode.com/upstream/pylons";
      rev = "707354ee4261b9c10450404fc9852ccea4fd667d";
      sha256 = "b2763274c2780523a335f83a1df65be22ebe4ff413a7bc9e9288d23c1f62032e";
    };
  });

  pyramid = super.pyramid.override (attrs: {
    postFixup = ''
      wrapPythonPrograms
      # TODO: johbo: "wrapPython" adds this magic line which
      # confuses pserve.
      ${sed} '/import sys; sys.argv/d' $out/bin/.pserve-wrapped
    '';
  });

  Pyro4 = super.Pyro4.override (attrs: {
    # TODO: Was not able to generate this version, needs further
    # investigation.
    name = "Pyro4-4.35";
    src = pkgs.fetchurl {
      url = "https://pypi.python.org/packages/source/P/Pyro4/Pyro4-4.35.src.tar.gz";
      md5 = "cbe6cb855f086a0f092ca075005855f3";
    };
  });

  pysqlite = super.pysqlite.override (attrs: {
    propagatedBuildInputs = [
      pkgs.sqlite
    ];
  });

  python-ldap = super.python-ldap.override (attrs: {
    propagatedBuildInputs = attrs.propagatedBuildInputs ++ [
      pkgs.cyrus_sasl
      pkgs.openldap
      pkgs.openssl
    ];
    NIX_CFLAGS_COMPILE = "-I${pkgs.cyrus_sasl}/include/sasl";
  });

  # Avoid that setuptools is replaced, this leads to trouble
  # with buildPythonPackage.
  setuptools = basePythonPackages.setuptools;

}
