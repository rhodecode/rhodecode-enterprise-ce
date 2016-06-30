#
# About
# =====
#
# This file defines jobs for our CI system and the attribute "build" is used
# as the input for packaging.
#
#
# CI details
# ==========
#
# This file defines an attribute set of derivations. Each of these attributes is
# then used in our CI system as one job to run. This way we keep the
# configuration for the CI jobs as well under version control.
#
# Run CI jobs locally
# -------------------
#
# Since it is all based on normal Nix derivations, the jobs can be tested
# locally with a run of "nix-build" like the following example:
#
#    nix-build release.nix -A test-api -I vcsserver=~/rhodecode-vcsserver
#
# Note: Replace "~/rhodecode-vcsserver" with a path where a clone of the
# vcsserver resides.

{ pkgs ? import <nixpkgs> {}
, doCheck ? true
}:

let

  inherit (pkgs)
    stdenv
    system;

  testing = import <nixpkgs/nixos/lib/testing.nix> {
    inherit system;
  };

  runInMachine = testing.runInMachine;

  sphinx = import ./docs/default.nix {};

  mkDocs = kind: stdenv.mkDerivation {
    name = kind;
    srcs = [
      (./. + (builtins.toPath "/${kind}"))
      (builtins.filterSource
        (path: type: baseNameOf path == "VERSION")
        ./rhodecode)
    ];
    sourceRoot = kind;
    buildInputs = [ sphinx ];
    configurePhase = null;
    buildPhase = ''
      make SPHINXBUILD=sphinx-build html
    '';
    installPhase = ''
      mkdir -p $out
      mv _build/html $out/

      mkdir -p $out/nix-support
      echo "doc manual $out/html index.html" >> \
        "$out/nix-support/hydra-build-products"
    '';
  };

  enterprise = import ./default.nix {
    inherit
      pkgs;

    # TODO: for quick local testing
    doCheck = false;
  };

  test-cfg = stdenv.mkDerivation {
    name = "test-cfg";
    unpackPhase = "true";
    buildInputs = [
      enterprise.src
    ];
    installPhase = ''
      mkdir -p $out/etc
      cp ${enterprise.src}/test.ini $out/etc/enterprise.ini
      # TODO: johbo: Needed, so that the login works, this causes
      # probably some side effects
      substituteInPlace $out/etc/enterprise.ini --replace "is_test = True" ""

      # Gevent configuration
      cp $out/etc/enterprise.ini $out/etc/enterprise-gevent.ini;
      cat >> $out/etc/enterprise-gevent.ini <<EOF

      [server:main]
      use = egg:gunicorn#main
      worker_class = gevent
      EOF

      cp ${enterprise.src}/vcsserver/test.ini $out/etc/vcsserver.ini
    '';
  };

  ac-test-drv = import ./acceptance_tests {
    withExternals = false;
  };

  # TODO: johbo: Currently abusing buildPythonPackage to make the
  # needed environment for the ac-test tools.
  mkAcTests = {
    # Path to an INI file which will be used to run Enterprise.
    #
    # Intended usage is to provide different configuration files to
    # run the tests against a different configuration.
    enterpriseCfg ? "${test-cfg}/etc/enterprise.ini"

    # Path to an INI file which will be used to run the VCSServer.
  , vcsserverCfg ? "${test-cfg}/etc/vcsserver.ini"
  }: pkgs.pythonPackages.buildPythonPackage {
    name = "enterprise-ac-tests";
    src = ./acceptance_tests;

    buildInputs = with pkgs; [
      curl
      enterprise
      ac-test-drv
    ];

    buildPhase = ''
      cp ${enterpriseCfg} enterprise.ini

      echo "Creating a fake home directory"
      mkdir fake-home
      export HOME=$PWD/fake-home

      echo "Creating a repository directory"
      mkdir repos

      echo "Preparing the database"
      paster setup-rhodecode \
        --user=admin \
        --email=admin@example.com \
        --password=secret \
        --api-key=9999999999999999999999999999999999999999 \
        --force-yes \
        --repos=$PWD/repos \
        enterprise.ini > /dev/null

      echo "Starting rcserver"
      vcsserver --config ${vcsserverCfg} >vcsserver.log 2>&1 &
      rcserver enterprise.ini >rcserver.log 2>&1 &

      while ! curl -f -s http://localhost:5000 > /dev/null
      do
          echo "Waiting for server to be ready..."
          sleep 3
      done
      echo "Webserver is ready."

      echo "Starting the test run"
      py.test -c example.ini -vs --maxfail=5 tests

      echo "Kill rcserver"
      kill %2
      kill %1
    '';

    # TODO: johbo: Use the install phase again once the normal mkDerivation
    # can be used again.
    postInstall = ''
      mkdir -p $out
      cp enterprise.ini $out
      cp ${vcsserverCfg} $out/vcsserver.ini
      cp rcserver.log $out
      cp vcsserver.log $out

      mkdir -p $out/nix-support
      echo "report config $out enterprise.ini" >> $out/nix-support/hydra-build-products
      echo "report config $out vcsserver.ini" >> $out/nix-support/hydra-build-products
      echo "report rcserver $out rcserver.log" >> $out/nix-support/hydra-build-products
      echo "report vcsserver $out vcsserver.log" >> $out/nix-support/hydra-build-products
    '';
  };

  vcsserver = import <vcsserver> {
    inherit pkgs;

    # TODO: johbo: Think of a more elegant solution to this problem
    pythonExternalOverrides = self: super: (enterprise.myPythonPackagesUnfix self);
  };

  runTests = optionString: (enterprise.override (attrs: {
    doCheck = true;
    name = "test-run";
    buildInputs = attrs.buildInputs ++ [
      vcsserver
    ];
    checkPhase = ''
      py.test ${optionString} -vv -ra
    '';
    buildPhase = attrs.shellHook;
    installPhase = ''
      echo "Intentionally not installing anything"
    '';
    meta.description = "Enterprise test run ${optionString}";
  }));

  jobs = {

    build = enterprise;

    # johbo: Currently this is simply running the tests against the sources. Nicer
    # would be to run xdist and against the installed application, so that we also
    # cover the impact of installing the application.
    test-api = runTests "rhodecode/api";
    test-functional = runTests "rhodecode/tests/functional";
    test-rest = runTests "rhodecode/tests --ignore=rhodecode/tests/functional";
    test-full = runTests "rhodecode";

    docs = mkDocs "docs";

    aggregate = pkgs.releaseTools.aggregate {
      name = "aggregated-jobs";
      constituents = [
        jobs.build
        jobs.test-api
        jobs.test-rest
        jobs.docs
      ];
    };
  };

in jobs
