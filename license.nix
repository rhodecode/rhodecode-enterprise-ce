# Utility to generate the license information
#
# Usage:
#
#   nix-build -I ~/dev license.nix -A result
#
# Afterwards ./result will contain the license information as JSON files.
#
#
# Overview
#
# Uses two steps to get the relevant license information:
#
# 1. Walk down the derivations based on "buildInputs" and
#    "propagatedBuildInputs". This results in all dependencies based on the nix
#    declartions.
#
# 2. Build Enterprise and query nix-store to get a list of runtime
#    dependencies. The results from step 1 are then limited to the ones which
#    are in this list.
#
# The result is then available in ./result/license.json.
#


let

  nixpkgs = import <nixpkgs> {};

  stdenv = nixpkgs.stdenv;

  # Enterprise as simple as possible, goal here is just to identify the runtime
  # dependencies. Ideally we could avoid building Enterprise at all and somehow
  # figure it out without calling into nix-store.
  enterprise = import ./default.nix {
    doCheck = false;
  };

  # For a given derivation, return the list of all dependencies
  drvToDependencies = drv: nixpkgs.lib.flatten [
    drv.nativeBuildInputs or []
    drv.propagatedNativeBuildInputs or []
  ];

  # Transform the given derivation into the meta information which we need in
  # the resulting JSON files.
  drvToMeta = drv: {
    name = drv.name or "UNNAMED";
    license = if drv ? meta.license then drv.meta.license else "UNKNOWN";
  };

  # Walk the tree of buildInputs and propagatedBuildInputs and return it as a
  # flat list.  Duplicates are avoided.
  listDrvDependencies = drv: let
    addElement = element: seen:
      if (builtins.elem element seen)
      then seen
      else let
        newSeen = seen ++ [ element ];
        newDeps = drvToDependencies element;
      in nixpkgs.lib.fold addElement newSeen newDeps;
    initialElements = drvToDependencies drv;
  in nixpkgs.lib.fold addElement [] initialElements;

  # Reads in a file with store paths and returns a list of derivation names.
  #
  # Reads the file, splits the lines, then removes the prefix, so that we
  # end up with a list of derivation names in the end.
  storePathsToDrvNames = srcPath: let
    rawStorePaths = nixpkgs.lib.removeSuffix "\n" (
      builtins.readFile srcPath);
    storePaths = nixpkgs.lib.splitString "\n" rawStorePaths;
    # TODO: johbo: Would be nice to use some sort of utility here to convert
    # the path to a derivation name.
    storePathPrefix = (
      builtins.stringLength "/nix/store/zwy7aavnif9ayw30rya1k6xiacafzzl6-");
    storePathToName = path:
      builtins.substring storePathPrefix (builtins.stringLength path) path;
  in (map storePathToName storePaths);

in rec {

  # Build Enterprise and call nix-store to retrieve the runtime
  # dependencies. The result is available in the nix store.
  runtimeDependencies = stdenv.mkDerivation {
    name = "runtime-dependencies";
    buildInputs = [
      # Needed to query the store
      nixpkgs.nix
    ];
    unpackPhase = ''
      echo "Nothing to unpack"
    '';
    buildPhase = ''
      # Get a list of runtime dependencies
      nix-store -q --references ${enterprise} > nix-store-references
    '';
    installPhase = ''
      mkdir -p $out
      cp -v nix-store-references $out/
    '';
  };

  # Produce the license overview files.
  result = let

    # Dependencies according to the nix-store
    runtimeDependencyNames = (
      storePathsToDrvNames "${runtimeDependencies}/nix-store-references");

    # Dependencies based on buildInputs and propagatedBuildInputs
    enterpriseAllDependencies = listDrvDependencies enterprise;
    enterpriseRuntimeDependencies = let
      elemName = element: element.name or "UNNAMED";
      isRuntime = element: builtins.elem (elemName element) runtimeDependencyNames;
    in builtins.filter isRuntime enterpriseAllDependencies;

    # Extract relevant meta information
    enterpriseAllLicenses = map drvToMeta enterpriseAllDependencies;
    enterpriseRuntimeLicenses = map drvToMeta enterpriseRuntimeDependencies;

  in stdenv.mkDerivation {

    name = "licenses";

    buildInputs = [];

    unpackPhase = ''
      echo "Nothing to unpack"
    '';

    buildPhase = ''
      mkdir build

      # Copy list of runtime dependencies for the Python processor
      cp "${runtimeDependencies}/nix-store-references" ./build/nix-store-references

      # All licenses which we found by walking buildInputs and
      # propagatedBuildInputs
      cat > build/all-licenses.json <<EOF
      ${builtins.toJSON enterpriseAllLicenses}
      EOF

      # License information for our runtime dependencies only. Basically all
      # licenses limited to the items which where also reported by nix-store as
      # a dependency.
      cat > build/licenses.json <<EOF
      ${builtins.toJSON enterpriseRuntimeLicenses}
      EOF
    '';

    installPhase = ''
      mkdir -p $out

      # Store it all, that helps when things go wrong
      cp -rv ./build/* $out
    '';
  };

}
