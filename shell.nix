{ pkgs ? (import <nixpkgs> {})
, vcsserverPath ? "./../rhodecode-vcsserver"
, vcsserverNix ? "shell.nix"
, doCheck ? true
}:

let

  # Convert vcsserverPath to absolute path.
  vcsserverAbsPath =
    if pkgs.lib.strings.hasPrefix "/" vcsserverPath then
      builtins.toPath "${vcsserverPath}"
    else
      builtins.toPath ("${builtins.getEnv "PWD"}/${vcsserverPath}");

  # Import vcsserver if nix file exists, otherwise set it to null.
  vcsserver =
    let
      nixFile = "${vcsserverAbsPath}/${vcsserverNix}";
    in
      if pkgs.lib.pathExists "${nixFile}" then
        builtins.trace
          "Using local vcsserver from ${nixFile}"
          import "${nixFile}" {inherit pkgs;}
      else
          null;

  hasVcsserver = !isNull vcsserver;

  enterprise = import ./default.nix {
    inherit pkgs doCheck;
  };

  pythonPackages = enterprise.pythonPackages;

in enterprise.override (attrs: {
  # Avoid that we dump any sources into the store when entering the shell and
  # make development a little bit more convenient.
  src = null;

  buildInputs = attrs.buildInputs ++
    pkgs.lib.optionals (hasVcsserver) vcsserver.propagatedNativeBuildInputs ++ [
    pythonPackages.bumpversion
    pythonPackages.invoke
    pythonPackages.ipdb
  ];

  shellHook = attrs.shellHook +
    pkgs.lib.strings.optionalString (hasVcsserver) ''
      # Setup the vcsserver development egg.
      pushd ${vcsserverAbsPath}
      python setup.py develop --prefix $tmp_path --allow-hosts ""
      popd
    '';
})
