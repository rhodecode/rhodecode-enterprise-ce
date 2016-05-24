{ self, fetchurl, fetchgit ? null, lib }:

{
  by-spec."abbrev"."1" =
    self.by-version."abbrev"."1.0.7";
  by-version."abbrev"."1.0.7" = lib.makeOverridable self.buildNodePackage {
    name = "abbrev-1.0.7";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/abbrev/-/abbrev-1.0.7.tgz";
        name = "abbrev-1.0.7.tgz";
        sha1 = "5b6035b2ee9d4fb5cf859f08a9be81b208491843";
      })
    ];
    buildInputs =
      (self.nativeDeps."abbrev" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "abbrev" ];
  };
  by-spec."amdefine".">=0.0.4" =
    self.by-version."amdefine"."1.0.0";
  by-version."amdefine"."1.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "amdefine-1.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/amdefine/-/amdefine-1.0.0.tgz";
        name = "amdefine-1.0.0.tgz";
        sha1 = "fd17474700cb5cc9c2b709f0be9d23ce3c198c33";
      })
    ];
    buildInputs =
      (self.nativeDeps."amdefine" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "amdefine" ];
  };
  by-spec."ansi-regex"."^0.2.0" =
    self.by-version."ansi-regex"."0.2.1";
  by-version."ansi-regex"."0.2.1" = lib.makeOverridable self.buildNodePackage {
    name = "ansi-regex-0.2.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/ansi-regex/-/ansi-regex-0.2.1.tgz";
        name = "ansi-regex-0.2.1.tgz";
        sha1 = "0d8e946967a3d8143f93e24e298525fc1b2235f9";
      })
    ];
    buildInputs =
      (self.nativeDeps."ansi-regex" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "ansi-regex" ];
  };
  by-spec."ansi-regex"."^0.2.1" =
    self.by-version."ansi-regex"."0.2.1";
  by-spec."ansi-regex"."^2.0.0" =
    self.by-version."ansi-regex"."2.0.0";
  by-version."ansi-regex"."2.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "ansi-regex-2.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/ansi-regex/-/ansi-regex-2.0.0.tgz";
        name = "ansi-regex-2.0.0.tgz";
        sha1 = "c5061b6e0ef8a81775e50f5d66151bf6bf371107";
      })
    ];
    buildInputs =
      (self.nativeDeps."ansi-regex" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "ansi-regex" ];
  };
  by-spec."ansi-styles"."^1.1.0" =
    self.by-version."ansi-styles"."1.1.0";
  by-version."ansi-styles"."1.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "ansi-styles-1.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/ansi-styles/-/ansi-styles-1.1.0.tgz";
        name = "ansi-styles-1.1.0.tgz";
        sha1 = "eaecbf66cd706882760b2f4691582b8f55d7a7de";
      })
    ];
    buildInputs =
      (self.nativeDeps."ansi-styles" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "ansi-styles" ];
  };
  by-spec."ansi-styles"."^2.1.0" =
    self.by-version."ansi-styles"."2.1.0";
  by-version."ansi-styles"."2.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "ansi-styles-2.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/ansi-styles/-/ansi-styles-2.1.0.tgz";
        name = "ansi-styles-2.1.0.tgz";
        sha1 = "990f747146927b559a932bf92959163d60c0d0e2";
      })
    ];
    buildInputs =
      (self.nativeDeps."ansi-styles" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "ansi-styles" ];
  };
  by-spec."argparse"."~ 0.1.11" =
    self.by-version."argparse"."0.1.16";
  by-version."argparse"."0.1.16" = lib.makeOverridable self.buildNodePackage {
    name = "argparse-0.1.16";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/argparse/-/argparse-0.1.16.tgz";
        name = "argparse-0.1.16.tgz";
        sha1 = "cfd01e0fbba3d6caed049fbd758d40f65196f57c";
      })
    ];
    buildInputs =
      (self.nativeDeps."argparse" or []);
    deps = {
      "underscore-1.7.0" = self.by-version."underscore"."1.7.0";
      "underscore.string-2.4.0" = self.by-version."underscore.string"."2.4.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "argparse" ];
  };
  by-spec."asap"."~1.0.0" =
    self.by-version."asap"."1.0.0";
  by-version."asap"."1.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "asap-1.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/asap/-/asap-1.0.0.tgz";
        name = "asap-1.0.0.tgz";
        sha1 = "b2a45da5fdfa20b0496fc3768cc27c12fa916a7d";
      })
    ];
    buildInputs =
      (self.nativeDeps."asap" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "asap" ];
  };
  by-spec."asn1".">=0.2.3 <0.3.0" =
    self.by-version."asn1"."0.2.3";
  by-version."asn1"."0.2.3" = lib.makeOverridable self.buildNodePackage {
    name = "asn1-0.2.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/asn1/-/asn1-0.2.3.tgz";
        name = "asn1-0.2.3.tgz";
        sha1 = "dac8787713c9966849fc8180777ebe9c1ddf3b86";
      })
    ];
    buildInputs =
      (self.nativeDeps."asn1" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "asn1" ];
  };
  by-spec."assert-plus".">=0.2.0 <0.3.0" =
    self.by-version."assert-plus"."0.2.0";
  by-version."assert-plus"."0.2.0" = lib.makeOverridable self.buildNodePackage {
    name = "assert-plus-0.2.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/assert-plus/-/assert-plus-0.2.0.tgz";
        name = "assert-plus-0.2.0.tgz";
        sha1 = "d74e1b87e7affc0db8aadb7021f3fe48101ab234";
      })
    ];
    buildInputs =
      (self.nativeDeps."assert-plus" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "assert-plus" ];
  };
  by-spec."assert-plus"."^0.1.5" =
    self.by-version."assert-plus"."0.1.5";
  by-version."assert-plus"."0.1.5" = lib.makeOverridable self.buildNodePackage {
    name = "assert-plus-0.1.5";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/assert-plus/-/assert-plus-0.1.5.tgz";
        name = "assert-plus-0.1.5.tgz";
        sha1 = "ee74009413002d84cec7219c6ac811812e723160";
      })
    ];
    buildInputs =
      (self.nativeDeps."assert-plus" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "assert-plus" ];
  };
  by-spec."assert-plus"."^0.2.0" =
    self.by-version."assert-plus"."0.2.0";
  by-spec."async"."^0.9.0" =
    self.by-version."async"."0.9.2";
  by-version."async"."0.9.2" = lib.makeOverridable self.buildNodePackage {
    name = "async-0.9.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/async/-/async-0.9.2.tgz";
        name = "async-0.9.2.tgz";
        sha1 = "aea74d5e61c1f899613bf64bda66d4c78f2fd17d";
      })
    ];
    buildInputs =
      (self.nativeDeps."async" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "async" ];
  };
  by-spec."async"."^1.4.0" =
    self.by-version."async"."1.5.2";
  by-version."async"."1.5.2" = lib.makeOverridable self.buildNodePackage {
    name = "async-1.5.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/async/-/async-1.5.2.tgz";
        name = "async-1.5.2.tgz";
        sha1 = "ec6a61ae56480c0c3cb241c95618e20892f9672a";
      })
    ];
    buildInputs =
      (self.nativeDeps."async" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "async" ];
  };
  by-spec."async"."~0.1.22" =
    self.by-version."async"."0.1.22";
  by-version."async"."0.1.22" = lib.makeOverridable self.buildNodePackage {
    name = "async-0.1.22";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/async/-/async-0.1.22.tgz";
        name = "async-0.1.22.tgz";
        sha1 = "0fc1aaa088a0e3ef0ebe2d8831bab0dcf8845061";
      })
    ];
    buildInputs =
      (self.nativeDeps."async" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "async" ];
  };
  by-spec."async"."~0.2.9" =
    self.by-version."async"."0.2.10";
  by-version."async"."0.2.10" = lib.makeOverridable self.buildNodePackage {
    name = "async-0.2.10";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/async/-/async-0.2.10.tgz";
        name = "async-0.2.10.tgz";
        sha1 = "b6bbe0b0674b9d719708ca38de8c237cb526c3d1";
      })
    ];
    buildInputs =
      (self.nativeDeps."async" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "async" ];
  };
  by-spec."aws-sign2"."~0.6.0" =
    self.by-version."aws-sign2"."0.6.0";
  by-version."aws-sign2"."0.6.0" = lib.makeOverridable self.buildNodePackage {
    name = "aws-sign2-0.6.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/aws-sign2/-/aws-sign2-0.6.0.tgz";
        name = "aws-sign2-0.6.0.tgz";
        sha1 = "14342dd38dbcc94d0e5b87d763cd63612c0e794f";
      })
    ];
    buildInputs =
      (self.nativeDeps."aws-sign2" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "aws-sign2" ];
  };
  by-spec."balanced-match"."^0.3.0" =
    self.by-version."balanced-match"."0.3.0";
  by-version."balanced-match"."0.3.0" = lib.makeOverridable self.buildNodePackage {
    name = "balanced-match-0.3.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/balanced-match/-/balanced-match-0.3.0.tgz";
        name = "balanced-match-0.3.0.tgz";
        sha1 = "a91cdd1ebef1a86659e70ff4def01625fc2d6756";
      })
    ];
    buildInputs =
      (self.nativeDeps."balanced-match" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "balanced-match" ];
  };
  by-spec."bl"."~1.0.0" =
    self.by-version."bl"."1.0.1";
  by-version."bl"."1.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "bl-1.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/bl/-/bl-1.0.1.tgz";
        name = "bl-1.0.1.tgz";
        sha1 = "0e6df7330308c46515751676cafa7334dc9852fd";
      })
    ];
    buildInputs =
      (self.nativeDeps."bl" or []);
    deps = {
      "readable-stream-2.0.5" = self.by-version."readable-stream"."2.0.5";
    };
    peerDependencies = [
    ];
    passthru.names = [ "bl" ];
  };
  by-spec."boom"."2.x.x" =
    self.by-version."boom"."2.10.1";
  by-version."boom"."2.10.1" = lib.makeOverridable self.buildNodePackage {
    name = "boom-2.10.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/boom/-/boom-2.10.1.tgz";
        name = "boom-2.10.1.tgz";
        sha1 = "39c8918ceff5799f83f9492a848f625add0c766f";
      })
    ];
    buildInputs =
      (self.nativeDeps."boom" or []);
    deps = {
      "hoek-2.16.3" = self.by-version."hoek"."2.16.3";
    };
    peerDependencies = [
    ];
    passthru.names = [ "boom" ];
  };
  by-spec."brace-expansion"."^1.0.0" =
    self.by-version."brace-expansion"."1.1.2";
  by-version."brace-expansion"."1.1.2" = lib.makeOverridable self.buildNodePackage {
    name = "brace-expansion-1.1.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.2.tgz";
        name = "brace-expansion-1.1.2.tgz";
        sha1 = "f21445d0488b658e2771efd870eff51df29f04ef";
      })
    ];
    buildInputs =
      (self.nativeDeps."brace-expansion" or []);
    deps = {
      "balanced-match-0.3.0" = self.by-version."balanced-match"."0.3.0";
      "concat-map-0.0.1" = self.by-version."concat-map"."0.0.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "brace-expansion" ];
  };
  by-spec."caseless"."~0.11.0" =
    self.by-version."caseless"."0.11.0";
  by-version."caseless"."0.11.0" = lib.makeOverridable self.buildNodePackage {
    name = "caseless-0.11.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/caseless/-/caseless-0.11.0.tgz";
        name = "caseless-0.11.0.tgz";
        sha1 = "715b96ea9841593cc33067923f5ec60ebda4f7d7";
      })
    ];
    buildInputs =
      (self.nativeDeps."caseless" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "caseless" ];
  };
  by-spec."chalk"."^0.5.1" =
    self.by-version."chalk"."0.5.1";
  by-version."chalk"."0.5.1" = lib.makeOverridable self.buildNodePackage {
    name = "chalk-0.5.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/chalk/-/chalk-0.5.1.tgz";
        name = "chalk-0.5.1.tgz";
        sha1 = "663b3a648b68b55d04690d49167aa837858f2174";
      })
    ];
    buildInputs =
      (self.nativeDeps."chalk" or []);
    deps = {
      "ansi-styles-1.1.0" = self.by-version."ansi-styles"."1.1.0";
      "escape-string-regexp-1.0.4" = self.by-version."escape-string-regexp"."1.0.4";
      "has-ansi-0.1.0" = self.by-version."has-ansi"."0.1.0";
      "strip-ansi-0.3.0" = self.by-version."strip-ansi"."0.3.0";
      "supports-color-0.2.0" = self.by-version."supports-color"."0.2.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "chalk" ];
  };
  by-spec."chalk"."^1.0.0" =
    self.by-version."chalk"."1.1.1";
  by-version."chalk"."1.1.1" = lib.makeOverridable self.buildNodePackage {
    name = "chalk-1.1.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/chalk/-/chalk-1.1.1.tgz";
        name = "chalk-1.1.1.tgz";
        sha1 = "509afb67066e7499f7eb3535c77445772ae2d019";
      })
    ];
    buildInputs =
      (self.nativeDeps."chalk" or []);
    deps = {
      "ansi-styles-2.1.0" = self.by-version."ansi-styles"."2.1.0";
      "escape-string-regexp-1.0.4" = self.by-version."escape-string-regexp"."1.0.4";
      "has-ansi-2.0.0" = self.by-version."has-ansi"."2.0.0";
      "strip-ansi-3.0.0" = self.by-version."strip-ansi"."3.0.0";
      "supports-color-2.0.0" = self.by-version."supports-color"."2.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "chalk" ];
  };
  by-spec."chalk"."^1.1.1" =
    self.by-version."chalk"."1.1.1";
  by-spec."cli"."0.6.x" =
    self.by-version."cli"."0.6.6";
  by-version."cli"."0.6.6" = lib.makeOverridable self.buildNodePackage {
    name = "cli-0.6.6";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/cli/-/cli-0.6.6.tgz";
        name = "cli-0.6.6.tgz";
        sha1 = "02ad44a380abf27adac5e6f0cdd7b043d74c53e3";
      })
    ];
    buildInputs =
      (self.nativeDeps."cli" or []);
    deps = {
      "glob-3.2.11" = self.by-version."glob"."3.2.11";
      "exit-0.1.2" = self.by-version."exit"."0.1.2";
    };
    peerDependencies = [
    ];
    passthru.names = [ "cli" ];
  };
  by-spec."coffee-script"."~1.3.3" =
    self.by-version."coffee-script"."1.3.3";
  by-version."coffee-script"."1.3.3" = lib.makeOverridable self.buildNodePackage {
    name = "coffee-script-1.3.3";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/coffee-script/-/coffee-script-1.3.3.tgz";
        name = "coffee-script-1.3.3.tgz";
        sha1 = "150d6b4cb522894369efed6a2101c20bc7f4a4f4";
      })
    ];
    buildInputs =
      (self.nativeDeps."coffee-script" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "coffee-script" ];
  };
  by-spec."colors"."~0.6.2" =
    self.by-version."colors"."0.6.2";
  by-version."colors"."0.6.2" = lib.makeOverridable self.buildNodePackage {
    name = "colors-0.6.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/colors/-/colors-0.6.2.tgz";
        name = "colors-0.6.2.tgz";
        sha1 = "2423fe6678ac0c5dae8852e5d0e5be08c997abcc";
      })
    ];
    buildInputs =
      (self.nativeDeps."colors" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "colors" ];
  };
  by-spec."combined-stream"."^1.0.5" =
    self.by-version."combined-stream"."1.0.5";
  by-version."combined-stream"."1.0.5" = lib.makeOverridable self.buildNodePackage {
    name = "combined-stream-1.0.5";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/combined-stream/-/combined-stream-1.0.5.tgz";
        name = "combined-stream-1.0.5.tgz";
        sha1 = "938370a57b4a51dea2c77c15d5c5fdf895164009";
      })
    ];
    buildInputs =
      (self.nativeDeps."combined-stream" or []);
    deps = {
      "delayed-stream-1.0.0" = self.by-version."delayed-stream"."1.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "combined-stream" ];
  };
  by-spec."combined-stream"."~1.0.5" =
    self.by-version."combined-stream"."1.0.5";
  by-spec."commander"."^2.9.0" =
    self.by-version."commander"."2.9.0";
  by-version."commander"."2.9.0" = lib.makeOverridable self.buildNodePackage {
    name = "commander-2.9.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/commander/-/commander-2.9.0.tgz";
        name = "commander-2.9.0.tgz";
        sha1 = "9c99094176e12240cb22d6c5146098400fe0f7d4";
      })
    ];
    buildInputs =
      (self.nativeDeps."commander" or []);
    deps = {
      "graceful-readlink-1.0.1" = self.by-version."graceful-readlink"."1.0.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "commander" ];
  };
  by-spec."concat-map"."0.0.1" =
    self.by-version."concat-map"."0.0.1";
  by-version."concat-map"."0.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "concat-map-0.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/concat-map/-/concat-map-0.0.1.tgz";
        name = "concat-map-0.0.1.tgz";
        sha1 = "d8a96bd77fd68df7793a73036a3ba0d5405d477b";
      })
    ];
    buildInputs =
      (self.nativeDeps."concat-map" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "concat-map" ];
  };
  by-spec."console-browserify"."1.1.x" =
    self.by-version."console-browserify"."1.1.0";
  by-version."console-browserify"."1.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "console-browserify-1.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/console-browserify/-/console-browserify-1.1.0.tgz";
        name = "console-browserify-1.1.0.tgz";
        sha1 = "f0241c45730a9fc6323b206dbf38edc741d0bb10";
      })
    ];
    buildInputs =
      (self.nativeDeps."console-browserify" or []);
    deps = {
      "date-now-0.1.4" = self.by-version."date-now"."0.1.4";
    };
    peerDependencies = [
    ];
    passthru.names = [ "console-browserify" ];
  };
  by-spec."core-util-is"."~1.0.0" =
    self.by-version."core-util-is"."1.0.2";
  by-version."core-util-is"."1.0.2" = lib.makeOverridable self.buildNodePackage {
    name = "core-util-is-1.0.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/core-util-is/-/core-util-is-1.0.2.tgz";
        name = "core-util-is-1.0.2.tgz";
        sha1 = "b5fd54220aa2bc5ab57aab7140c940754503c1a7";
      })
    ];
    buildInputs =
      (self.nativeDeps."core-util-is" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "core-util-is" ];
  };
  by-spec."cryptiles"."2.x.x" =
    self.by-version."cryptiles"."2.0.5";
  by-version."cryptiles"."2.0.5" = lib.makeOverridable self.buildNodePackage {
    name = "cryptiles-2.0.5";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/cryptiles/-/cryptiles-2.0.5.tgz";
        name = "cryptiles-2.0.5.tgz";
        sha1 = "3bdfecdc608147c1c67202fa291e7dca59eaa3b8";
      })
    ];
    buildInputs =
      (self.nativeDeps."cryptiles" or []);
    deps = {
      "boom-2.10.1" = self.by-version."boom"."2.10.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "cryptiles" ];
  };
  by-spec."dashdash".">=1.10.1 <2.0.0" =
    self.by-version."dashdash"."1.12.2";
  by-version."dashdash"."1.12.2" = lib.makeOverridable self.buildNodePackage {
    name = "dashdash-1.12.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/dashdash/-/dashdash-1.12.2.tgz";
        name = "dashdash-1.12.2.tgz";
        sha1 = "1c6f70588498d047b8cd5777b32ba85a5e25be36";
      })
    ];
    buildInputs =
      (self.nativeDeps."dashdash" or []);
    deps = {
      "assert-plus-0.2.0" = self.by-version."assert-plus"."0.2.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "dashdash" ];
  };
  by-spec."date-now"."^0.1.4" =
    self.by-version."date-now"."0.1.4";
  by-version."date-now"."0.1.4" = lib.makeOverridable self.buildNodePackage {
    name = "date-now-0.1.4";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/date-now/-/date-now-0.1.4.tgz";
        name = "date-now-0.1.4.tgz";
        sha1 = "eaf439fd4d4848ad74e5cc7dbef200672b9e345b";
      })
    ];
    buildInputs =
      (self.nativeDeps."date-now" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "date-now" ];
  };
  by-spec."dateformat"."1.0.2-1.2.3" =
    self.by-version."dateformat"."1.0.2-1.2.3";
  by-version."dateformat"."1.0.2-1.2.3" = lib.makeOverridable self.buildNodePackage {
    name = "dateformat-1.0.2-1.2.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/dateformat/-/dateformat-1.0.2-1.2.3.tgz";
        name = "dateformat-1.0.2-1.2.3.tgz";
        sha1 = "b0220c02de98617433b72851cf47de3df2cdbee9";
      })
    ];
    buildInputs =
      (self.nativeDeps."dateformat" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "dateformat" ];
  };
  by-spec."debug"."~0.7.0" =
    self.by-version."debug"."0.7.4";
  by-version."debug"."0.7.4" = lib.makeOverridable self.buildNodePackage {
    name = "debug-0.7.4";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/debug/-/debug-0.7.4.tgz";
        name = "debug-0.7.4.tgz";
        sha1 = "06e1ea8082c2cb14e39806e22e2f6f757f92af39";
      })
    ];
    buildInputs =
      (self.nativeDeps."debug" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "debug" ];
  };
  by-spec."delayed-stream"."~1.0.0" =
    self.by-version."delayed-stream"."1.0.0";
  by-version."delayed-stream"."1.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "delayed-stream-1.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/delayed-stream/-/delayed-stream-1.0.0.tgz";
        name = "delayed-stream-1.0.0.tgz";
        sha1 = "df3ae199acadfb7d440aaae0b29e2272b24ec619";
      })
    ];
    buildInputs =
      (self.nativeDeps."delayed-stream" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "delayed-stream" ];
  };
  by-spec."dom-serializer"."0" =
    self.by-version."dom-serializer"."0.1.0";
  by-version."dom-serializer"."0.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "dom-serializer-0.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/dom-serializer/-/dom-serializer-0.1.0.tgz";
        name = "dom-serializer-0.1.0.tgz";
        sha1 = "073c697546ce0780ce23be4a28e293e40bc30c82";
      })
    ];
    buildInputs =
      (self.nativeDeps."dom-serializer" or []);
    deps = {
      "domelementtype-1.1.3" = self.by-version."domelementtype"."1.1.3";
      "entities-1.1.1" = self.by-version."entities"."1.1.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "dom-serializer" ];
  };
  by-spec."domelementtype"."1" =
    self.by-version."domelementtype"."1.3.0";
  by-version."domelementtype"."1.3.0" = lib.makeOverridable self.buildNodePackage {
    name = "domelementtype-1.3.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/domelementtype/-/domelementtype-1.3.0.tgz";
        name = "domelementtype-1.3.0.tgz";
        sha1 = "b17aed82e8ab59e52dd9c19b1756e0fc187204c2";
      })
    ];
    buildInputs =
      (self.nativeDeps."domelementtype" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "domelementtype" ];
  };
  by-spec."domelementtype"."~1.1.1" =
    self.by-version."domelementtype"."1.1.3";
  by-version."domelementtype"."1.1.3" = lib.makeOverridable self.buildNodePackage {
    name = "domelementtype-1.1.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/domelementtype/-/domelementtype-1.1.3.tgz";
        name = "domelementtype-1.1.3.tgz";
        sha1 = "bd28773e2642881aec51544924299c5cd822185b";
      })
    ];
    buildInputs =
      (self.nativeDeps."domelementtype" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "domelementtype" ];
  };
  by-spec."domhandler"."2.3" =
    self.by-version."domhandler"."2.3.0";
  by-version."domhandler"."2.3.0" = lib.makeOverridable self.buildNodePackage {
    name = "domhandler-2.3.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/domhandler/-/domhandler-2.3.0.tgz";
        name = "domhandler-2.3.0.tgz";
        sha1 = "2de59a0822d5027fabff6f032c2b25a2a8abe738";
      })
    ];
    buildInputs =
      (self.nativeDeps."domhandler" or []);
    deps = {
      "domelementtype-1.3.0" = self.by-version."domelementtype"."1.3.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "domhandler" ];
  };
  by-spec."domutils"."1.5" =
    self.by-version."domutils"."1.5.1";
  by-version."domutils"."1.5.1" = lib.makeOverridable self.buildNodePackage {
    name = "domutils-1.5.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/domutils/-/domutils-1.5.1.tgz";
        name = "domutils-1.5.1.tgz";
        sha1 = "dcd8488a26f563d61079e48c9f7b7e32373682cf";
      })
    ];
    buildInputs =
      (self.nativeDeps."domutils" or []);
    deps = {
      "dom-serializer-0.1.0" = self.by-version."dom-serializer"."0.1.0";
      "domelementtype-1.3.0" = self.by-version."domelementtype"."1.3.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "domutils" ];
  };
  by-spec."ecc-jsbn".">=0.0.1 <1.0.0" =
    self.by-version."ecc-jsbn"."0.1.1";
  by-version."ecc-jsbn"."0.1.1" = lib.makeOverridable self.buildNodePackage {
    name = "ecc-jsbn-0.1.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/ecc-jsbn/-/ecc-jsbn-0.1.1.tgz";
        name = "ecc-jsbn-0.1.1.tgz";
        sha1 = "0fc73a9ed5f0d53c38193398523ef7e543777505";
      })
    ];
    buildInputs =
      (self.nativeDeps."ecc-jsbn" or []);
    deps = {
      "jsbn-0.1.0" = self.by-version."jsbn"."0.1.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "ecc-jsbn" ];
  };
  by-spec."entities"."1.0" =
    self.by-version."entities"."1.0.0";
  by-version."entities"."1.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "entities-1.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/entities/-/entities-1.0.0.tgz";
        name = "entities-1.0.0.tgz";
        sha1 = "b2987aa3821347fcde642b24fdfc9e4fb712bf26";
      })
    ];
    buildInputs =
      (self.nativeDeps."entities" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "entities" ];
  };
  by-spec."entities"."~1.1.1" =
    self.by-version."entities"."1.1.1";
  by-version."entities"."1.1.1" = lib.makeOverridable self.buildNodePackage {
    name = "entities-1.1.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/entities/-/entities-1.1.1.tgz";
        name = "entities-1.1.1.tgz";
        sha1 = "6e5c2d0a5621b5dadaecef80b90edfb5cd7772f0";
      })
    ];
    buildInputs =
      (self.nativeDeps."entities" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "entities" ];
  };
  by-spec."errno"."^0.1.1" =
    self.by-version."errno"."0.1.4";
  by-version."errno"."0.1.4" = lib.makeOverridable self.buildNodePackage {
    name = "errno-0.1.4";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/errno/-/errno-0.1.4.tgz";
        name = "errno-0.1.4.tgz";
        sha1 = "b896e23a9e5e8ba33871fc996abd3635fc9a1c7d";
      })
    ];
    buildInputs =
      (self.nativeDeps."errno" or []);
    deps = {
      "prr-0.0.0" = self.by-version."prr"."0.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "errno" ];
  };
  by-spec."escape-string-regexp"."^1.0.0" =
    self.by-version."escape-string-regexp"."1.0.4";
  by-version."escape-string-regexp"."1.0.4" = lib.makeOverridable self.buildNodePackage {
    name = "escape-string-regexp-1.0.4";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-1.0.4.tgz";
        name = "escape-string-regexp-1.0.4.tgz";
        sha1 = "b85e679b46f72d03fbbe8a3bf7259d535c21b62f";
      })
    ];
    buildInputs =
      (self.nativeDeps."escape-string-regexp" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "escape-string-regexp" ];
  };
  by-spec."escape-string-regexp"."^1.0.2" =
    self.by-version."escape-string-regexp"."1.0.4";
  by-spec."esprima"."~ 1.0.2" =
    self.by-version."esprima"."1.0.4";
  by-version."esprima"."1.0.4" = lib.makeOverridable self.buildNodePackage {
    name = "esprima-1.0.4";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/esprima/-/esprima-1.0.4.tgz";
        name = "esprima-1.0.4.tgz";
        sha1 = "9f557e08fc3b4d26ece9dd34f8fbf476b62585ad";
      })
    ];
    buildInputs =
      (self.nativeDeps."esprima" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "esprima" ];
  };
  by-spec."eventemitter2"."~0.4.13" =
    self.by-version."eventemitter2"."0.4.14";
  by-version."eventemitter2"."0.4.14" = lib.makeOverridable self.buildNodePackage {
    name = "eventemitter2-0.4.14";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/eventemitter2/-/eventemitter2-0.4.14.tgz";
        name = "eventemitter2-0.4.14.tgz";
        sha1 = "8f61b75cde012b2e9eb284d4545583b5643b61ab";
      })
    ];
    buildInputs =
      (self.nativeDeps."eventemitter2" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "eventemitter2" ];
  };
  by-spec."exit"."0.1.2" =
    self.by-version."exit"."0.1.2";
  by-version."exit"."0.1.2" = lib.makeOverridable self.buildNodePackage {
    name = "exit-0.1.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/exit/-/exit-0.1.2.tgz";
        name = "exit-0.1.2.tgz";
        sha1 = "0632638f8d877cc82107d30a0fff1a17cba1cd0c";
      })
    ];
    buildInputs =
      (self.nativeDeps."exit" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "exit" ];
  };
  by-spec."exit"."0.1.x" =
    self.by-version."exit"."0.1.2";
  by-spec."exit"."~0.1.1" =
    self.by-version."exit"."0.1.2";
  by-spec."extend"."~3.0.0" =
    self.by-version."extend"."3.0.0";
  by-version."extend"."3.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "extend-3.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/extend/-/extend-3.0.0.tgz";
        name = "extend-3.0.0.tgz";
        sha1 = "5a474353b9f3353ddd8176dfd37b91c83a46f1d4";
      })
    ];
    buildInputs =
      (self.nativeDeps."extend" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "extend" ];
  };
  by-spec."extsprintf"."1.0.2" =
    self.by-version."extsprintf"."1.0.2";
  by-version."extsprintf"."1.0.2" = lib.makeOverridable self.buildNodePackage {
    name = "extsprintf-1.0.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/extsprintf/-/extsprintf-1.0.2.tgz";
        name = "extsprintf-1.0.2.tgz";
        sha1 = "e1080e0658e300b06294990cc70e1502235fd550";
      })
    ];
    buildInputs =
      (self.nativeDeps."extsprintf" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "extsprintf" ];
  };
  by-spec."faye-websocket"."~0.4.3" =
    self.by-version."faye-websocket"."0.4.4";
  by-version."faye-websocket"."0.4.4" = lib.makeOverridable self.buildNodePackage {
    name = "faye-websocket-0.4.4";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/faye-websocket/-/faye-websocket-0.4.4.tgz";
        name = "faye-websocket-0.4.4.tgz";
        sha1 = "c14c5b3bf14d7417ffbfd990c0a7495cd9f337bc";
      })
    ];
    buildInputs =
      (self.nativeDeps."faye-websocket" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "faye-websocket" ];
  };
  by-spec."findup-sync"."~0.1.2" =
    self.by-version."findup-sync"."0.1.3";
  by-version."findup-sync"."0.1.3" = lib.makeOverridable self.buildNodePackage {
    name = "findup-sync-0.1.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/findup-sync/-/findup-sync-0.1.3.tgz";
        name = "findup-sync-0.1.3.tgz";
        sha1 = "7f3e7a97b82392c653bf06589bd85190e93c3683";
      })
    ];
    buildInputs =
      (self.nativeDeps."findup-sync" or []);
    deps = {
      "glob-3.2.11" = self.by-version."glob"."3.2.11";
      "lodash-2.4.2" = self.by-version."lodash"."2.4.2";
    };
    peerDependencies = [
    ];
    passthru.names = [ "findup-sync" ];
  };
  by-spec."forever-agent"."~0.6.1" =
    self.by-version."forever-agent"."0.6.1";
  by-version."forever-agent"."0.6.1" = lib.makeOverridable self.buildNodePackage {
    name = "forever-agent-0.6.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/forever-agent/-/forever-agent-0.6.1.tgz";
        name = "forever-agent-0.6.1.tgz";
        sha1 = "fbc71f0c41adeb37f96c577ad1ed42d8fdacca91";
      })
    ];
    buildInputs =
      (self.nativeDeps."forever-agent" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "forever-agent" ];
  };
  by-spec."form-data"."~1.0.0-rc3" =
    self.by-version."form-data"."1.0.0-rc3";
  by-version."form-data"."1.0.0-rc3" = lib.makeOverridable self.buildNodePackage {
    name = "form-data-1.0.0-rc3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/form-data/-/form-data-1.0.0-rc3.tgz";
        name = "form-data-1.0.0-rc3.tgz";
        sha1 = "d35bc62e7fbc2937ae78f948aaa0d38d90607577";
      })
    ];
    buildInputs =
      (self.nativeDeps."form-data" or []);
    deps = {
      "async-1.5.2" = self.by-version."async"."1.5.2";
      "combined-stream-1.0.5" = self.by-version."combined-stream"."1.0.5";
      "mime-types-2.1.9" = self.by-version."mime-types"."2.1.9";
    };
    peerDependencies = [
    ];
    passthru.names = [ "form-data" ];
  };
  by-spec."gaze"."~0.5.1" =
    self.by-version."gaze"."0.5.2";
  by-version."gaze"."0.5.2" = lib.makeOverridable self.buildNodePackage {
    name = "gaze-0.5.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/gaze/-/gaze-0.5.2.tgz";
        name = "gaze-0.5.2.tgz";
        sha1 = "40b709537d24d1d45767db5a908689dfe69ac44f";
      })
    ];
    buildInputs =
      (self.nativeDeps."gaze" or []);
    deps = {
      "globule-0.1.0" = self.by-version."globule"."0.1.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "gaze" ];
  };
  by-spec."generate-function"."^2.0.0" =
    self.by-version."generate-function"."2.0.0";
  by-version."generate-function"."2.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "generate-function-2.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/generate-function/-/generate-function-2.0.0.tgz";
        name = "generate-function-2.0.0.tgz";
        sha1 = "6858fe7c0969b7d4e9093337647ac79f60dfbe74";
      })
    ];
    buildInputs =
      (self.nativeDeps."generate-function" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "generate-function" ];
  };
  by-spec."generate-object-property"."^1.1.0" =
    self.by-version."generate-object-property"."1.2.0";
  by-version."generate-object-property"."1.2.0" = lib.makeOverridable self.buildNodePackage {
    name = "generate-object-property-1.2.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/generate-object-property/-/generate-object-property-1.2.0.tgz";
        name = "generate-object-property-1.2.0.tgz";
        sha1 = "9c0e1c40308ce804f4783618b937fa88f99d50d0";
      })
    ];
    buildInputs =
      (self.nativeDeps."generate-object-property" or []);
    deps = {
      "is-property-1.0.2" = self.by-version."is-property"."1.0.2";
    };
    peerDependencies = [
    ];
    passthru.names = [ "generate-object-property" ];
  };
  by-spec."getobject"."~0.1.0" =
    self.by-version."getobject"."0.1.0";
  by-version."getobject"."0.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "getobject-0.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/getobject/-/getobject-0.1.0.tgz";
        name = "getobject-0.1.0.tgz";
        sha1 = "047a449789fa160d018f5486ed91320b6ec7885c";
      })
    ];
    buildInputs =
      (self.nativeDeps."getobject" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "getobject" ];
  };
  by-spec."glob"."~ 3.2.1" =
    self.by-version."glob"."3.2.11";
  by-version."glob"."3.2.11" = lib.makeOverridable self.buildNodePackage {
    name = "glob-3.2.11";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/glob/-/glob-3.2.11.tgz";
        name = "glob-3.2.11.tgz";
        sha1 = "4a973f635b9190f715d10987d5c00fd2815ebe3d";
      })
    ];
    buildInputs =
      (self.nativeDeps."glob" or []);
    deps = {
      "inherits-2.0.1" = self.by-version."inherits"."2.0.1";
      "minimatch-0.3.0" = self.by-version."minimatch"."0.3.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "glob" ];
  };
  by-spec."glob"."~3.1.21" =
    self.by-version."glob"."3.1.21";
  by-version."glob"."3.1.21" = lib.makeOverridable self.buildNodePackage {
    name = "glob-3.1.21";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/glob/-/glob-3.1.21.tgz";
        name = "glob-3.1.21.tgz";
        sha1 = "d29e0a055dea5138f4d07ed40e8982e83c2066cd";
      })
    ];
    buildInputs =
      (self.nativeDeps."glob" or []);
    deps = {
      "minimatch-0.2.14" = self.by-version."minimatch"."0.2.14";
      "graceful-fs-1.2.3" = self.by-version."graceful-fs"."1.2.3";
      "inherits-1.0.2" = self.by-version."inherits"."1.0.2";
    };
    peerDependencies = [
    ];
    passthru.names = [ "glob" ];
  };
  by-spec."glob"."~3.2.9" =
    self.by-version."glob"."3.2.11";
  by-spec."globule"."~0.1.0" =
    self.by-version."globule"."0.1.0";
  by-version."globule"."0.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "globule-0.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/globule/-/globule-0.1.0.tgz";
        name = "globule-0.1.0.tgz";
        sha1 = "d9c8edde1da79d125a151b79533b978676346ae5";
      })
    ];
    buildInputs =
      (self.nativeDeps."globule" or []);
    deps = {
      "lodash-1.0.2" = self.by-version."lodash"."1.0.2";
      "glob-3.1.21" = self.by-version."glob"."3.1.21";
      "minimatch-0.2.14" = self.by-version."minimatch"."0.2.14";
    };
    peerDependencies = [
    ];
    passthru.names = [ "globule" ];
  };
  by-spec."graceful-fs"."^3.0.5" =
    self.by-version."graceful-fs"."3.0.8";
  by-version."graceful-fs"."3.0.8" = lib.makeOverridable self.buildNodePackage {
    name = "graceful-fs-3.0.8";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/graceful-fs/-/graceful-fs-3.0.8.tgz";
        name = "graceful-fs-3.0.8.tgz";
        sha1 = "ce813e725fa82f7e6147d51c9a5ca68270551c22";
      })
    ];
    buildInputs =
      (self.nativeDeps."graceful-fs" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "graceful-fs" ];
  };
  by-spec."graceful-fs"."~1.2.0" =
    self.by-version."graceful-fs"."1.2.3";
  by-version."graceful-fs"."1.2.3" = lib.makeOverridable self.buildNodePackage {
    name = "graceful-fs-1.2.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/graceful-fs/-/graceful-fs-1.2.3.tgz";
        name = "graceful-fs-1.2.3.tgz";
        sha1 = "15a4806a57547cb2d2dbf27f42e89a8c3451b364";
      })
    ];
    buildInputs =
      (self.nativeDeps."graceful-fs" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "graceful-fs" ];
  };
  by-spec."graceful-readlink".">= 1.0.0" =
    self.by-version."graceful-readlink"."1.0.1";
  by-version."graceful-readlink"."1.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "graceful-readlink-1.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/graceful-readlink/-/graceful-readlink-1.0.1.tgz";
        name = "graceful-readlink-1.0.1.tgz";
        sha1 = "4cafad76bc62f02fa039b2f94e9a3dd3a391a725";
      })
    ];
    buildInputs =
      (self.nativeDeps."graceful-readlink" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "graceful-readlink" ];
  };
  by-spec."grunt".">=0.4.0" =
    self.by-version."grunt"."0.4.5";
  by-version."grunt"."0.4.5" = lib.makeOverridable self.buildNodePackage {
    name = "grunt-0.4.5";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/grunt/-/grunt-0.4.5.tgz";
        name = "grunt-0.4.5.tgz";
        sha1 = "56937cd5194324adff6d207631832a9d6ba4e7f0";
      })
    ];
    buildInputs =
      (self.nativeDeps."grunt" or []);
    deps = {
      "async-0.1.22" = self.by-version."async"."0.1.22";
      "coffee-script-1.3.3" = self.by-version."coffee-script"."1.3.3";
      "colors-0.6.2" = self.by-version."colors"."0.6.2";
      "dateformat-1.0.2-1.2.3" = self.by-version."dateformat"."1.0.2-1.2.3";
      "eventemitter2-0.4.14" = self.by-version."eventemitter2"."0.4.14";
      "findup-sync-0.1.3" = self.by-version."findup-sync"."0.1.3";
      "glob-3.1.21" = self.by-version."glob"."3.1.21";
      "hooker-0.2.3" = self.by-version."hooker"."0.2.3";
      "iconv-lite-0.2.11" = self.by-version."iconv-lite"."0.2.11";
      "minimatch-0.2.14" = self.by-version."minimatch"."0.2.14";
      "nopt-1.0.10" = self.by-version."nopt"."1.0.10";
      "rimraf-2.2.8" = self.by-version."rimraf"."2.2.8";
      "lodash-0.9.2" = self.by-version."lodash"."0.9.2";
      "underscore.string-2.2.1" = self.by-version."underscore.string"."2.2.1";
      "which-1.0.9" = self.by-version."which"."1.0.9";
      "js-yaml-2.0.5" = self.by-version."js-yaml"."2.0.5";
      "exit-0.1.2" = self.by-version."exit"."0.1.2";
      "getobject-0.1.0" = self.by-version."getobject"."0.1.0";
      "grunt-legacy-util-0.2.0" = self.by-version."grunt-legacy-util"."0.2.0";
      "grunt-legacy-log-0.1.3" = self.by-version."grunt-legacy-log"."0.1.3";
    };
    peerDependencies = [
    ];
    passthru.names = [ "grunt" ];
  };
  by-spec."grunt"."^0.4.5" =
    self.by-version."grunt"."0.4.5";
  "grunt" = self.by-version."grunt"."0.4.5";
  by-spec."grunt"."~0.4.0" =
    self.by-version."grunt"."0.4.5";
  by-spec."grunt-contrib-concat"."^0.5.1" =
    self.by-version."grunt-contrib-concat"."0.5.1";
  by-version."grunt-contrib-concat"."0.5.1" = lib.makeOverridable self.buildNodePackage {
    name = "grunt-contrib-concat-0.5.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/grunt-contrib-concat/-/grunt-contrib-concat-0.5.1.tgz";
        name = "grunt-contrib-concat-0.5.1.tgz";
        sha1 = "953c6efdfdfd2c107ab9c85077f2d4b24d31cd49";
      })
    ];
    buildInputs =
      (self.nativeDeps."grunt-contrib-concat" or []);
    deps = {
      "chalk-0.5.1" = self.by-version."chalk"."0.5.1";
      "source-map-0.3.0" = self.by-version."source-map"."0.3.0";
    };
    peerDependencies = [
      self.by-version."grunt"."0.4.5"
    ];
    passthru.names = [ "grunt-contrib-concat" ];
  };
  "grunt-contrib-concat" = self.by-version."grunt-contrib-concat"."0.5.1";
  by-spec."grunt-contrib-jshint"."^0.12.0" =
    self.by-version."grunt-contrib-jshint"."0.12.0";
  by-version."grunt-contrib-jshint"."0.12.0" = lib.makeOverridable self.buildNodePackage {
    name = "grunt-contrib-jshint-0.12.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/grunt-contrib-jshint/-/grunt-contrib-jshint-0.12.0.tgz";
        name = "grunt-contrib-jshint-0.12.0.tgz";
        sha1 = "f6b2f06fc715264837a7ab6c69a1ce1a689c2c29";
      })
    ];
    buildInputs =
      (self.nativeDeps."grunt-contrib-jshint" or []);
    deps = {
      "hooker-0.2.3" = self.by-version."hooker"."0.2.3";
      "jshint-2.9.1" = self.by-version."jshint"."2.9.1";
    };
    peerDependencies = [
      self.by-version."grunt"."0.4.5"
    ];
    passthru.names = [ "grunt-contrib-jshint" ];
  };
  "grunt-contrib-jshint" = self.by-version."grunt-contrib-jshint"."0.12.0";
  by-spec."grunt-contrib-less"."^1.1.0" =
    self.by-version."grunt-contrib-less"."1.1.0";
  by-version."grunt-contrib-less"."1.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "grunt-contrib-less-1.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/grunt-contrib-less/-/grunt-contrib-less-1.1.0.tgz";
        name = "grunt-contrib-less-1.1.0.tgz";
        sha1 = "44d5c5521ad76f3675a12374125d019b5dd03f51";
      })
    ];
    buildInputs =
      (self.nativeDeps."grunt-contrib-less" or []);
    deps = {
      "async-0.9.2" = self.by-version."async"."0.9.2";
      "chalk-1.1.1" = self.by-version."chalk"."1.1.1";
      "less-2.5.3" = self.by-version."less"."2.5.3";
      "lodash-3.10.1" = self.by-version."lodash"."3.10.1";
    };
    peerDependencies = [
      self.by-version."grunt"."0.4.5"
    ];
    passthru.names = [ "grunt-contrib-less" ];
  };
  "grunt-contrib-less" = self.by-version."grunt-contrib-less"."1.1.0";
  by-spec."grunt-contrib-watch"."^0.6.1" =
    self.by-version."grunt-contrib-watch"."0.6.1";
  by-version."grunt-contrib-watch"."0.6.1" = lib.makeOverridable self.buildNodePackage {
    name = "grunt-contrib-watch-0.6.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/grunt-contrib-watch/-/grunt-contrib-watch-0.6.1.tgz";
        name = "grunt-contrib-watch-0.6.1.tgz";
        sha1 = "64fdcba25a635f5b4da1b6ce6f90da0aeb6e3f15";
      })
    ];
    buildInputs =
      (self.nativeDeps."grunt-contrib-watch" or []);
    deps = {
      "gaze-0.5.2" = self.by-version."gaze"."0.5.2";
      "tiny-lr-fork-0.0.5" = self.by-version."tiny-lr-fork"."0.0.5";
      "lodash-2.4.2" = self.by-version."lodash"."2.4.2";
      "async-0.2.10" = self.by-version."async"."0.2.10";
    };
    peerDependencies = [
      self.by-version."grunt"."0.4.5"
    ];
    passthru.names = [ "grunt-contrib-watch" ];
  };
  "grunt-contrib-watch" = self.by-version."grunt-contrib-watch"."0.6.1";
  by-spec."grunt-legacy-log"."~0.1.0" =
    self.by-version."grunt-legacy-log"."0.1.3";
  by-version."grunt-legacy-log"."0.1.3" = lib.makeOverridable self.buildNodePackage {
    name = "grunt-legacy-log-0.1.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/grunt-legacy-log/-/grunt-legacy-log-0.1.3.tgz";
        name = "grunt-legacy-log-0.1.3.tgz";
        sha1 = "ec29426e803021af59029f87d2f9cd7335a05531";
      })
    ];
    buildInputs =
      (self.nativeDeps."grunt-legacy-log" or []);
    deps = {
      "colors-0.6.2" = self.by-version."colors"."0.6.2";
      "grunt-legacy-log-utils-0.1.1" = self.by-version."grunt-legacy-log-utils"."0.1.1";
      "hooker-0.2.3" = self.by-version."hooker"."0.2.3";
      "lodash-2.4.2" = self.by-version."lodash"."2.4.2";
      "underscore.string-2.3.3" = self.by-version."underscore.string"."2.3.3";
    };
    peerDependencies = [
    ];
    passthru.names = [ "grunt-legacy-log" ];
  };
  by-spec."grunt-legacy-log-utils"."~0.1.1" =
    self.by-version."grunt-legacy-log-utils"."0.1.1";
  by-version."grunt-legacy-log-utils"."0.1.1" = lib.makeOverridable self.buildNodePackage {
    name = "grunt-legacy-log-utils-0.1.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/grunt-legacy-log-utils/-/grunt-legacy-log-utils-0.1.1.tgz";
        name = "grunt-legacy-log-utils-0.1.1.tgz";
        sha1 = "c0706b9dd9064e116f36f23fe4e6b048672c0f7e";
      })
    ];
    buildInputs =
      (self.nativeDeps."grunt-legacy-log-utils" or []);
    deps = {
      "lodash-2.4.2" = self.by-version."lodash"."2.4.2";
      "underscore.string-2.3.3" = self.by-version."underscore.string"."2.3.3";
      "colors-0.6.2" = self.by-version."colors"."0.6.2";
    };
    peerDependencies = [
    ];
    passthru.names = [ "grunt-legacy-log-utils" ];
  };
  by-spec."grunt-legacy-util"."~0.2.0" =
    self.by-version."grunt-legacy-util"."0.2.0";
  by-version."grunt-legacy-util"."0.2.0" = lib.makeOverridable self.buildNodePackage {
    name = "grunt-legacy-util-0.2.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/grunt-legacy-util/-/grunt-legacy-util-0.2.0.tgz";
        name = "grunt-legacy-util-0.2.0.tgz";
        sha1 = "93324884dbf7e37a9ff7c026dff451d94a9e554b";
      })
    ];
    buildInputs =
      (self.nativeDeps."grunt-legacy-util" or []);
    deps = {
      "hooker-0.2.3" = self.by-version."hooker"."0.2.3";
      "async-0.1.22" = self.by-version."async"."0.1.22";
      "lodash-0.9.2" = self.by-version."lodash"."0.9.2";
      "exit-0.1.2" = self.by-version."exit"."0.1.2";
      "underscore.string-2.2.1" = self.by-version."underscore.string"."2.2.1";
      "getobject-0.1.0" = self.by-version."getobject"."0.1.0";
      "which-1.0.9" = self.by-version."which"."1.0.9";
    };
    peerDependencies = [
    ];
    passthru.names = [ "grunt-legacy-util" ];
  };
  by-spec."har-validator"."~2.0.2" =
    self.by-version."har-validator"."2.0.6";
  by-version."har-validator"."2.0.6" = lib.makeOverridable self.buildNodePackage {
    name = "har-validator-2.0.6";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/har-validator/-/har-validator-2.0.6.tgz";
        name = "har-validator-2.0.6.tgz";
        sha1 = "cdcbc08188265ad119b6a5a7c8ab70eecfb5d27d";
      })
    ];
    buildInputs =
      (self.nativeDeps."har-validator" or []);
    deps = {
      "chalk-1.1.1" = self.by-version."chalk"."1.1.1";
      "commander-2.9.0" = self.by-version."commander"."2.9.0";
      "is-my-json-valid-2.12.4" = self.by-version."is-my-json-valid"."2.12.4";
      "pinkie-promise-2.0.0" = self.by-version."pinkie-promise"."2.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "har-validator" ];
  };
  by-spec."has-ansi"."^0.1.0" =
    self.by-version."has-ansi"."0.1.0";
  by-version."has-ansi"."0.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "has-ansi-0.1.0";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/has-ansi/-/has-ansi-0.1.0.tgz";
        name = "has-ansi-0.1.0.tgz";
        sha1 = "84f265aae8c0e6a88a12d7022894b7568894c62e";
      })
    ];
    buildInputs =
      (self.nativeDeps."has-ansi" or []);
    deps = {
      "ansi-regex-0.2.1" = self.by-version."ansi-regex"."0.2.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "has-ansi" ];
  };
  by-spec."has-ansi"."^2.0.0" =
    self.by-version."has-ansi"."2.0.0";
  by-version."has-ansi"."2.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "has-ansi-2.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/has-ansi/-/has-ansi-2.0.0.tgz";
        name = "has-ansi-2.0.0.tgz";
        sha1 = "34f5049ce1ecdf2b0649af3ef24e45ed35416d91";
      })
    ];
    buildInputs =
      (self.nativeDeps."has-ansi" or []);
    deps = {
      "ansi-regex-2.0.0" = self.by-version."ansi-regex"."2.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "has-ansi" ];
  };
  by-spec."hawk"."~3.1.0" =
    self.by-version."hawk"."3.1.3";
  by-version."hawk"."3.1.3" = lib.makeOverridable self.buildNodePackage {
    name = "hawk-3.1.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/hawk/-/hawk-3.1.3.tgz";
        name = "hawk-3.1.3.tgz";
        sha1 = "078444bd7c1640b0fe540d2c9b73d59678e8e1c4";
      })
    ];
    buildInputs =
      (self.nativeDeps."hawk" or []);
    deps = {
      "hoek-2.16.3" = self.by-version."hoek"."2.16.3";
      "boom-2.10.1" = self.by-version."boom"."2.10.1";
      "cryptiles-2.0.5" = self.by-version."cryptiles"."2.0.5";
      "sntp-1.0.9" = self.by-version."sntp"."1.0.9";
    };
    peerDependencies = [
    ];
    passthru.names = [ "hawk" ];
  };
  by-spec."hoek"."2.x.x" =
    self.by-version."hoek"."2.16.3";
  by-version."hoek"."2.16.3" = lib.makeOverridable self.buildNodePackage {
    name = "hoek-2.16.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/hoek/-/hoek-2.16.3.tgz";
        name = "hoek-2.16.3.tgz";
        sha1 = "20bb7403d3cea398e91dc4710a8ff1b8274a25ed";
      })
    ];
    buildInputs =
      (self.nativeDeps."hoek" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "hoek" ];
  };
  by-spec."hooker"."^0.2.3" =
    self.by-version."hooker"."0.2.3";
  by-version."hooker"."0.2.3" = lib.makeOverridable self.buildNodePackage {
    name = "hooker-0.2.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/hooker/-/hooker-0.2.3.tgz";
        name = "hooker-0.2.3.tgz";
        sha1 = "b834f723cc4a242aa65963459df6d984c5d3d959";
      })
    ];
    buildInputs =
      (self.nativeDeps."hooker" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "hooker" ];
  };
  by-spec."hooker"."~0.2.3" =
    self.by-version."hooker"."0.2.3";
  by-spec."htmlparser2"."3.8.x" =
    self.by-version."htmlparser2"."3.8.3";
  by-version."htmlparser2"."3.8.3" = lib.makeOverridable self.buildNodePackage {
    name = "htmlparser2-3.8.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/htmlparser2/-/htmlparser2-3.8.3.tgz";
        name = "htmlparser2-3.8.3.tgz";
        sha1 = "996c28b191516a8be86501a7d79757e5c70c1068";
      })
    ];
    buildInputs =
      (self.nativeDeps."htmlparser2" or []);
    deps = {
      "domhandler-2.3.0" = self.by-version."domhandler"."2.3.0";
      "domutils-1.5.1" = self.by-version."domutils"."1.5.1";
      "domelementtype-1.3.0" = self.by-version."domelementtype"."1.3.0";
      "readable-stream-1.1.13" = self.by-version."readable-stream"."1.1.13";
      "entities-1.0.0" = self.by-version."entities"."1.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "htmlparser2" ];
  };
  by-spec."http-signature"."~1.1.0" =
    self.by-version."http-signature"."1.1.0";
  by-version."http-signature"."1.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "http-signature-1.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/http-signature/-/http-signature-1.1.0.tgz";
        name = "http-signature-1.1.0.tgz";
        sha1 = "5d2d7e9b6ef49980ad5b128d8e4ef09a31c90d95";
      })
    ];
    buildInputs =
      (self.nativeDeps."http-signature" or []);
    deps = {
      "assert-plus-0.1.5" = self.by-version."assert-plus"."0.1.5";
      "jsprim-1.2.2" = self.by-version."jsprim"."1.2.2";
      "sshpk-1.7.3" = self.by-version."sshpk"."1.7.3";
    };
    peerDependencies = [
    ];
    passthru.names = [ "http-signature" ];
  };
  by-spec."iconv-lite"."~0.2.11" =
    self.by-version."iconv-lite"."0.2.11";
  by-version."iconv-lite"."0.2.11" = lib.makeOverridable self.buildNodePackage {
    name = "iconv-lite-0.2.11";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/iconv-lite/-/iconv-lite-0.2.11.tgz";
        name = "iconv-lite-0.2.11.tgz";
        sha1 = "1ce60a3a57864a292d1321ff4609ca4bb965adc8";
      })
    ];
    buildInputs =
      (self.nativeDeps."iconv-lite" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "iconv-lite" ];
  };
  by-spec."image-size"."~0.3.5" =
    self.by-version."image-size"."0.3.5";
  by-version."image-size"."0.3.5" = lib.makeOverridable self.buildNodePackage {
    name = "image-size-0.3.5";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/image-size/-/image-size-0.3.5.tgz";
        name = "image-size-0.3.5.tgz";
        sha1 = "83240eab2fb5b00b04aab8c74b0471e9cba7ad8c";
      })
    ];
    buildInputs =
      (self.nativeDeps."image-size" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "image-size" ];
  };
  by-spec."inherits"."1" =
    self.by-version."inherits"."1.0.2";
  by-version."inherits"."1.0.2" = lib.makeOverridable self.buildNodePackage {
    name = "inherits-1.0.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/inherits/-/inherits-1.0.2.tgz";
        name = "inherits-1.0.2.tgz";
        sha1 = "ca4309dadee6b54cc0b8d247e8d7c7a0975bdc9b";
      })
    ];
    buildInputs =
      (self.nativeDeps."inherits" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "inherits" ];
  };
  by-spec."inherits"."2" =
    self.by-version."inherits"."2.0.1";
  by-version."inherits"."2.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "inherits-2.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/inherits/-/inherits-2.0.1.tgz";
        name = "inherits-2.0.1.tgz";
        sha1 = "b17d08d326b4423e568eff719f91b0b1cbdf69f1";
      })
    ];
    buildInputs =
      (self.nativeDeps."inherits" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "inherits" ];
  };
  by-spec."inherits"."~2.0.1" =
    self.by-version."inherits"."2.0.1";
  by-spec."is-my-json-valid"."^2.12.4" =
    self.by-version."is-my-json-valid"."2.12.4";
  by-version."is-my-json-valid"."2.12.4" = lib.makeOverridable self.buildNodePackage {
    name = "is-my-json-valid-2.12.4";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/is-my-json-valid/-/is-my-json-valid-2.12.4.tgz";
        name = "is-my-json-valid-2.12.4.tgz";
        sha1 = "d4ed2bc1d7f88daf8d0f763b3e3e39a69bd37880";
      })
    ];
    buildInputs =
      (self.nativeDeps."is-my-json-valid" or []);
    deps = {
      "generate-function-2.0.0" = self.by-version."generate-function"."2.0.0";
      "generate-object-property-1.2.0" = self.by-version."generate-object-property"."1.2.0";
      "jsonpointer-2.0.0" = self.by-version."jsonpointer"."2.0.0";
      "xtend-4.0.1" = self.by-version."xtend"."4.0.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "is-my-json-valid" ];
  };
  by-spec."is-property"."^1.0.0" =
    self.by-version."is-property"."1.0.2";
  by-version."is-property"."1.0.2" = lib.makeOverridable self.buildNodePackage {
    name = "is-property-1.0.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/is-property/-/is-property-1.0.2.tgz";
        name = "is-property-1.0.2.tgz";
        sha1 = "57fe1c4e48474edd65b09911f26b1cd4095dda84";
      })
    ];
    buildInputs =
      (self.nativeDeps."is-property" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "is-property" ];
  };
  by-spec."is-typedarray"."~1.0.0" =
    self.by-version."is-typedarray"."1.0.0";
  by-version."is-typedarray"."1.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "is-typedarray-1.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/is-typedarray/-/is-typedarray-1.0.0.tgz";
        name = "is-typedarray-1.0.0.tgz";
        sha1 = "e479c80858df0c1b11ddda6940f96011fcda4a9a";
      })
    ];
    buildInputs =
      (self.nativeDeps."is-typedarray" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "is-typedarray" ];
  };
  by-spec."isarray"."0.0.1" =
    self.by-version."isarray"."0.0.1";
  by-version."isarray"."0.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "isarray-0.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/isarray/-/isarray-0.0.1.tgz";
        name = "isarray-0.0.1.tgz";
        sha1 = "8a18acfca9a8f4177e09abfc6038939b05d1eedf";
      })
    ];
    buildInputs =
      (self.nativeDeps."isarray" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "isarray" ];
  };
  by-spec."isstream"."~0.1.2" =
    self.by-version."isstream"."0.1.2";
  by-version."isstream"."0.1.2" = lib.makeOverridable self.buildNodePackage {
    name = "isstream-0.1.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/isstream/-/isstream-0.1.2.tgz";
        name = "isstream-0.1.2.tgz";
        sha1 = "47e63f7af55afa6f92e1500e690eb8b8529c099a";
      })
    ];
    buildInputs =
      (self.nativeDeps."isstream" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "isstream" ];
  };
  by-spec."jodid25519".">=1.0.0 <2.0.0" =
    self.by-version."jodid25519"."1.0.2";
  by-version."jodid25519"."1.0.2" = lib.makeOverridable self.buildNodePackage {
    name = "jodid25519-1.0.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/jodid25519/-/jodid25519-1.0.2.tgz";
        name = "jodid25519-1.0.2.tgz";
        sha1 = "06d4912255093419477d425633606e0e90782967";
      })
    ];
    buildInputs =
      (self.nativeDeps."jodid25519" or []);
    deps = {
      "jsbn-0.1.0" = self.by-version."jsbn"."0.1.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "jodid25519" ];
  };
  by-spec."js-yaml"."~2.0.5" =
    self.by-version."js-yaml"."2.0.5";
  by-version."js-yaml"."2.0.5" = lib.makeOverridable self.buildNodePackage {
    name = "js-yaml-2.0.5";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/js-yaml/-/js-yaml-2.0.5.tgz";
        name = "js-yaml-2.0.5.tgz";
        sha1 = "a25ae6509999e97df278c6719da11bd0687743a8";
      })
    ];
    buildInputs =
      (self.nativeDeps."js-yaml" or []);
    deps = {
      "argparse-0.1.16" = self.by-version."argparse"."0.1.16";
      "esprima-1.0.4" = self.by-version."esprima"."1.0.4";
    };
    peerDependencies = [
    ];
    passthru.names = [ "js-yaml" ];
  };
  by-spec."jsbn".">=0.1.0 <0.2.0" =
    self.by-version."jsbn"."0.1.0";
  by-version."jsbn"."0.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "jsbn-0.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/jsbn/-/jsbn-0.1.0.tgz";
        name = "jsbn-0.1.0.tgz";
        sha1 = "650987da0dd74f4ebf5a11377a2aa2d273e97dfd";
      })
    ];
    buildInputs =
      (self.nativeDeps."jsbn" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "jsbn" ];
  };
  by-spec."jsbn"."~0.1.0" =
    self.by-version."jsbn"."0.1.0";
  by-spec."jshint"."^2.9.1-rc3" =
    self.by-version."jshint"."2.9.1";
  by-version."jshint"."2.9.1" = lib.makeOverridable self.buildNodePackage {
    name = "jshint-2.9.1";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/jshint/-/jshint-2.9.1.tgz";
        name = "jshint-2.9.1.tgz";
        sha1 = "3136b68f8b6fa37423aacb8ec5e18a1ada7a2638";
      })
    ];
    buildInputs =
      (self.nativeDeps."jshint" or []);
    deps = {
      "cli-0.6.6" = self.by-version."cli"."0.6.6";
      "console-browserify-1.1.0" = self.by-version."console-browserify"."1.1.0";
      "exit-0.1.2" = self.by-version."exit"."0.1.2";
      "htmlparser2-3.8.3" = self.by-version."htmlparser2"."3.8.3";
      "minimatch-2.0.10" = self.by-version."minimatch"."2.0.10";
      "shelljs-0.3.0" = self.by-version."shelljs"."0.3.0";
      "strip-json-comments-1.0.4" = self.by-version."strip-json-comments"."1.0.4";
      "lodash-3.7.0" = self.by-version."lodash"."3.7.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "jshint" ];
  };
  "jshint" = self.by-version."jshint"."2.9.1";
  by-spec."jshint"."~2.9.1" =
    self.by-version."jshint"."2.9.1";
  by-spec."json-schema"."0.2.2" =
    self.by-version."json-schema"."0.2.2";
  by-version."json-schema"."0.2.2" = lib.makeOverridable self.buildNodePackage {
    name = "json-schema-0.2.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/json-schema/-/json-schema-0.2.2.tgz";
        name = "json-schema-0.2.2.tgz";
        sha1 = "50354f19f603917c695f70b85afa77c3b0f23506";
      })
    ];
    buildInputs =
      (self.nativeDeps."json-schema" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "json-schema" ];
  };
  by-spec."json-stringify-safe"."~5.0.1" =
    self.by-version."json-stringify-safe"."5.0.1";
  by-version."json-stringify-safe"."5.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "json-stringify-safe-5.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/json-stringify-safe/-/json-stringify-safe-5.0.1.tgz";
        name = "json-stringify-safe-5.0.1.tgz";
        sha1 = "1296a2d58fd45f19a0f6ce01d65701e2c735b6eb";
      })
    ];
    buildInputs =
      (self.nativeDeps."json-stringify-safe" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "json-stringify-safe" ];
  };
  by-spec."jsonpointer"."2.0.0" =
    self.by-version."jsonpointer"."2.0.0";
  by-version."jsonpointer"."2.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "jsonpointer-2.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/jsonpointer/-/jsonpointer-2.0.0.tgz";
        name = "jsonpointer-2.0.0.tgz";
        sha1 = "3af1dd20fe85463910d469a385e33017d2a030d9";
      })
    ];
    buildInputs =
      (self.nativeDeps."jsonpointer" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "jsonpointer" ];
  };
  by-spec."jsprim"."^1.2.2" =
    self.by-version."jsprim"."1.2.2";
  by-version."jsprim"."1.2.2" = lib.makeOverridable self.buildNodePackage {
    name = "jsprim-1.2.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/jsprim/-/jsprim-1.2.2.tgz";
        name = "jsprim-1.2.2.tgz";
        sha1 = "f20c906ac92abd58e3b79ac8bc70a48832512da1";
      })
    ];
    buildInputs =
      (self.nativeDeps."jsprim" or []);
    deps = {
      "extsprintf-1.0.2" = self.by-version."extsprintf"."1.0.2";
      "json-schema-0.2.2" = self.by-version."json-schema"."0.2.2";
      "verror-1.3.6" = self.by-version."verror"."1.3.6";
    };
    peerDependencies = [
    ];
    passthru.names = [ "jsprim" ];
  };
  by-spec."less"."~2.5.0" =
    self.by-version."less"."2.5.3";
  by-version."less"."2.5.3" = lib.makeOverridable self.buildNodePackage {
    name = "less-2.5.3";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/less/-/less-2.5.3.tgz";
        name = "less-2.5.3.tgz";
        sha1 = "9ff586e8a703515fc18dc99c7bc498d2f3ad4849";
      })
    ];
    buildInputs =
      (self.nativeDeps."less" or []);
    deps = {
      "errno-0.1.4" = self.by-version."errno"."0.1.4";
      "graceful-fs-3.0.8" = self.by-version."graceful-fs"."3.0.8";
      "image-size-0.3.5" = self.by-version."image-size"."0.3.5";
      "mime-1.3.4" = self.by-version."mime"."1.3.4";
      "mkdirp-0.5.1" = self.by-version."mkdirp"."0.5.1";
      "promise-6.1.0" = self.by-version."promise"."6.1.0";
      "request-2.67.0" = self.by-version."request"."2.67.0";
      "source-map-0.4.4" = self.by-version."source-map"."0.4.4";
    };
    peerDependencies = [
    ];
    passthru.names = [ "less" ];
  };
  by-spec."lodash"."3.7.x" =
    self.by-version."lodash"."3.7.0";
  by-version."lodash"."3.7.0" = lib.makeOverridable self.buildNodePackage {
    name = "lodash-3.7.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/lodash/-/lodash-3.7.0.tgz";
        name = "lodash-3.7.0.tgz";
        sha1 = "3678bd8ab995057c07ade836ed2ef087da811d45";
      })
    ];
    buildInputs =
      (self.nativeDeps."lodash" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "lodash" ];
  };
  by-spec."lodash"."^3.2.0" =
    self.by-version."lodash"."3.10.1";
  by-version."lodash"."3.10.1" = lib.makeOverridable self.buildNodePackage {
    name = "lodash-3.10.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/lodash/-/lodash-3.10.1.tgz";
        name = "lodash-3.10.1.tgz";
        sha1 = "5bf45e8e49ba4189e17d482789dfd15bd140b7b6";
      })
    ];
    buildInputs =
      (self.nativeDeps."lodash" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "lodash" ];
  };
  by-spec."lodash"."~0.9.2" =
    self.by-version."lodash"."0.9.2";
  by-version."lodash"."0.9.2" = lib.makeOverridable self.buildNodePackage {
    name = "lodash-0.9.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/lodash/-/lodash-0.9.2.tgz";
        name = "lodash-0.9.2.tgz";
        sha1 = "8f3499c5245d346d682e5b0d3b40767e09f1a92c";
      })
    ];
    buildInputs =
      (self.nativeDeps."lodash" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "lodash" ];
  };
  by-spec."lodash"."~1.0.1" =
    self.by-version."lodash"."1.0.2";
  by-version."lodash"."1.0.2" = lib.makeOverridable self.buildNodePackage {
    name = "lodash-1.0.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/lodash/-/lodash-1.0.2.tgz";
        name = "lodash-1.0.2.tgz";
        sha1 = "8f57560c83b59fc270bd3d561b690043430e2551";
      })
    ];
    buildInputs =
      (self.nativeDeps."lodash" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "lodash" ];
  };
  by-spec."lodash"."~2.4.1" =
    self.by-version."lodash"."2.4.2";
  by-version."lodash"."2.4.2" = lib.makeOverridable self.buildNodePackage {
    name = "lodash-2.4.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/lodash/-/lodash-2.4.2.tgz";
        name = "lodash-2.4.2.tgz";
        sha1 = "fadd834b9683073da179b3eae6d9c0d15053f73e";
      })
    ];
    buildInputs =
      (self.nativeDeps."lodash" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "lodash" ];
  };
  by-spec."lru-cache"."2" =
    self.by-version."lru-cache"."2.7.3";
  by-version."lru-cache"."2.7.3" = lib.makeOverridable self.buildNodePackage {
    name = "lru-cache-2.7.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/lru-cache/-/lru-cache-2.7.3.tgz";
        name = "lru-cache-2.7.3.tgz";
        sha1 = "6d4524e8b955f95d4f5b58851ce21dd72fb4e952";
      })
    ];
    buildInputs =
      (self.nativeDeps."lru-cache" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "lru-cache" ];
  };
  by-spec."mime"."^1.2.11" =
    self.by-version."mime"."1.3.4";
  by-version."mime"."1.3.4" = lib.makeOverridable self.buildNodePackage {
    name = "mime-1.3.4";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/mime/-/mime-1.3.4.tgz";
        name = "mime-1.3.4.tgz";
        sha1 = "115f9e3b6b3daf2959983cb38f149a2d40eb5d53";
      })
    ];
    buildInputs =
      (self.nativeDeps."mime" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "mime" ];
  };
  by-spec."mime-db"."~1.21.0" =
    self.by-version."mime-db"."1.21.0";
  by-version."mime-db"."1.21.0" = lib.makeOverridable self.buildNodePackage {
    name = "mime-db-1.21.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/mime-db/-/mime-db-1.21.0.tgz";
        name = "mime-db-1.21.0.tgz";
        sha1 = "9b5239e3353cf6eb015a00d890261027c36d4bac";
      })
    ];
    buildInputs =
      (self.nativeDeps."mime-db" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "mime-db" ];
  };
  by-spec."mime-types"."^2.1.3" =
    self.by-version."mime-types"."2.1.9";
  by-version."mime-types"."2.1.9" = lib.makeOverridable self.buildNodePackage {
    name = "mime-types-2.1.9";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/mime-types/-/mime-types-2.1.9.tgz";
        name = "mime-types-2.1.9.tgz";
        sha1 = "dfb396764b5fdf75be34b1f4104bc3687fb635f8";
      })
    ];
    buildInputs =
      (self.nativeDeps."mime-types" or []);
    deps = {
      "mime-db-1.21.0" = self.by-version."mime-db"."1.21.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "mime-types" ];
  };
  by-spec."mime-types"."~2.1.7" =
    self.by-version."mime-types"."2.1.9";
  by-spec."minimatch"."0.3" =
    self.by-version."minimatch"."0.3.0";
  by-version."minimatch"."0.3.0" = lib.makeOverridable self.buildNodePackage {
    name = "minimatch-0.3.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/minimatch/-/minimatch-0.3.0.tgz";
        name = "minimatch-0.3.0.tgz";
        sha1 = "275d8edaac4f1bb3326472089e7949c8394699dd";
      })
    ];
    buildInputs =
      (self.nativeDeps."minimatch" or []);
    deps = {
      "lru-cache-2.7.3" = self.by-version."lru-cache"."2.7.3";
      "sigmund-1.0.1" = self.by-version."sigmund"."1.0.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "minimatch" ];
  };
  by-spec."minimatch"."2.0.x" =
    self.by-version."minimatch"."2.0.10";
  by-version."minimatch"."2.0.10" = lib.makeOverridable self.buildNodePackage {
    name = "minimatch-2.0.10";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/minimatch/-/minimatch-2.0.10.tgz";
        name = "minimatch-2.0.10.tgz";
        sha1 = "8d087c39c6b38c001b97fca7ce6d0e1e80afbac7";
      })
    ];
    buildInputs =
      (self.nativeDeps."minimatch" or []);
    deps = {
      "brace-expansion-1.1.2" = self.by-version."brace-expansion"."1.1.2";
    };
    peerDependencies = [
    ];
    passthru.names = [ "minimatch" ];
  };
  by-spec."minimatch"."~0.2.11" =
    self.by-version."minimatch"."0.2.14";
  by-version."minimatch"."0.2.14" = lib.makeOverridable self.buildNodePackage {
    name = "minimatch-0.2.14";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/minimatch/-/minimatch-0.2.14.tgz";
        name = "minimatch-0.2.14.tgz";
        sha1 = "c74e780574f63c6f9a090e90efbe6ef53a6a756a";
      })
    ];
    buildInputs =
      (self.nativeDeps."minimatch" or []);
    deps = {
      "lru-cache-2.7.3" = self.by-version."lru-cache"."2.7.3";
      "sigmund-1.0.1" = self.by-version."sigmund"."1.0.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "minimatch" ];
  };
  by-spec."minimatch"."~0.2.12" =
    self.by-version."minimatch"."0.2.14";
  by-spec."minimist"."0.0.8" =
    self.by-version."minimist"."0.0.8";
  by-version."minimist"."0.0.8" = lib.makeOverridable self.buildNodePackage {
    name = "minimist-0.0.8";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/minimist/-/minimist-0.0.8.tgz";
        name = "minimist-0.0.8.tgz";
        sha1 = "857fcabfc3397d2625b8228262e86aa7a011b05d";
      })
    ];
    buildInputs =
      (self.nativeDeps."minimist" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "minimist" ];
  };
  by-spec."mkdirp"."^0.5.0" =
    self.by-version."mkdirp"."0.5.1";
  by-version."mkdirp"."0.5.1" = lib.makeOverridable self.buildNodePackage {
    name = "mkdirp-0.5.1";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/mkdirp/-/mkdirp-0.5.1.tgz";
        name = "mkdirp-0.5.1.tgz";
        sha1 = "30057438eac6cf7f8c4767f38648d6697d75c903";
      })
    ];
    buildInputs =
      (self.nativeDeps."mkdirp" or []);
    deps = {
      "minimist-0.0.8" = self.by-version."minimist"."0.0.8";
    };
    peerDependencies = [
    ];
    passthru.names = [ "mkdirp" ];
  };
  by-spec."node-uuid"."~1.4.7" =
    self.by-version."node-uuid"."1.4.7";
  by-version."node-uuid"."1.4.7" = lib.makeOverridable self.buildNodePackage {
    name = "node-uuid-1.4.7";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/node-uuid/-/node-uuid-1.4.7.tgz";
        name = "node-uuid-1.4.7.tgz";
        sha1 = "6da5a17668c4b3dd59623bda11cf7fa4c1f60a6f";
      })
    ];
    buildInputs =
      (self.nativeDeps."node-uuid" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "node-uuid" ];
  };
  by-spec."nopt"."~1.0.10" =
    self.by-version."nopt"."1.0.10";
  by-version."nopt"."1.0.10" = lib.makeOverridable self.buildNodePackage {
    name = "nopt-1.0.10";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/nopt/-/nopt-1.0.10.tgz";
        name = "nopt-1.0.10.tgz";
        sha1 = "6ddd21bd2a31417b92727dd585f8a6f37608ebee";
      })
    ];
    buildInputs =
      (self.nativeDeps."nopt" or []);
    deps = {
      "abbrev-1.0.7" = self.by-version."abbrev"."1.0.7";
    };
    peerDependencies = [
    ];
    passthru.names = [ "nopt" ];
  };
  by-spec."nopt"."~2.0.0" =
    self.by-version."nopt"."2.0.0";
  by-version."nopt"."2.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "nopt-2.0.0";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/nopt/-/nopt-2.0.0.tgz";
        name = "nopt-2.0.0.tgz";
        sha1 = "ca7416f20a5e3f9c3b86180f96295fa3d0b52e0d";
      })
    ];
    buildInputs =
      (self.nativeDeps."nopt" or []);
    deps = {
      "abbrev-1.0.7" = self.by-version."abbrev"."1.0.7";
    };
    peerDependencies = [
    ];
    passthru.names = [ "nopt" ];
  };
  by-spec."noptify"."~0.0.3" =
    self.by-version."noptify"."0.0.3";
  by-version."noptify"."0.0.3" = lib.makeOverridable self.buildNodePackage {
    name = "noptify-0.0.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/noptify/-/noptify-0.0.3.tgz";
        name = "noptify-0.0.3.tgz";
        sha1 = "58f654a73d9753df0c51d9686dc92104a67f4bbb";
      })
    ];
    buildInputs =
      (self.nativeDeps."noptify" or []);
    deps = {
      "nopt-2.0.0" = self.by-version."nopt"."2.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "noptify" ];
  };
  by-spec."oauth-sign"."~0.8.0" =
    self.by-version."oauth-sign"."0.8.0";
  by-version."oauth-sign"."0.8.0" = lib.makeOverridable self.buildNodePackage {
    name = "oauth-sign-0.8.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/oauth-sign/-/oauth-sign-0.8.0.tgz";
        name = "oauth-sign-0.8.0.tgz";
        sha1 = "938fdc875765ba527137d8aec9d178e24debc553";
      })
    ];
    buildInputs =
      (self.nativeDeps."oauth-sign" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "oauth-sign" ];
  };
  by-spec."pinkie"."^2.0.0" =
    self.by-version."pinkie"."2.0.1";
  by-version."pinkie"."2.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "pinkie-2.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/pinkie/-/pinkie-2.0.1.tgz";
        name = "pinkie-2.0.1.tgz";
        sha1 = "4236c86fc29f261c2045bbe81f78cbb2a5e8306c";
      })
    ];
    buildInputs =
      (self.nativeDeps."pinkie" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "pinkie" ];
  };
  by-spec."pinkie-promise"."^2.0.0" =
    self.by-version."pinkie-promise"."2.0.0";
  by-version."pinkie-promise"."2.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "pinkie-promise-2.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/pinkie-promise/-/pinkie-promise-2.0.0.tgz";
        name = "pinkie-promise-2.0.0.tgz";
        sha1 = "4c83538de1f6e660c29e0a13446844f7a7e88259";
      })
    ];
    buildInputs =
      (self.nativeDeps."pinkie-promise" or []);
    deps = {
      "pinkie-2.0.1" = self.by-version."pinkie"."2.0.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "pinkie-promise" ];
  };
  by-spec."process-nextick-args"."~1.0.6" =
    self.by-version."process-nextick-args"."1.0.6";
  by-version."process-nextick-args"."1.0.6" = lib.makeOverridable self.buildNodePackage {
    name = "process-nextick-args-1.0.6";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/process-nextick-args/-/process-nextick-args-1.0.6.tgz";
        name = "process-nextick-args-1.0.6.tgz";
        sha1 = "0f96b001cea90b12592ce566edb97ec11e69bd05";
      })
    ];
    buildInputs =
      (self.nativeDeps."process-nextick-args" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "process-nextick-args" ];
  };
  by-spec."promise"."^6.0.1" =
    self.by-version."promise"."6.1.0";
  by-version."promise"."6.1.0" = lib.makeOverridable self.buildNodePackage {
    name = "promise-6.1.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/promise/-/promise-6.1.0.tgz";
        name = "promise-6.1.0.tgz";
        sha1 = "2ce729f6b94b45c26891ad0602c5c90e04c6eef6";
      })
    ];
    buildInputs =
      (self.nativeDeps."promise" or []);
    deps = {
      "asap-1.0.0" = self.by-version."asap"."1.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "promise" ];
  };
  by-spec."prr"."~0.0.0" =
    self.by-version."prr"."0.0.0";
  by-version."prr"."0.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "prr-0.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/prr/-/prr-0.0.0.tgz";
        name = "prr-0.0.0.tgz";
        sha1 = "1a84b85908325501411853d0081ee3fa86e2926a";
      })
    ];
    buildInputs =
      (self.nativeDeps."prr" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "prr" ];
  };
  by-spec."qs"."~0.5.2" =
    self.by-version."qs"."0.5.6";
  by-version."qs"."0.5.6" = lib.makeOverridable self.buildNodePackage {
    name = "qs-0.5.6";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/qs/-/qs-0.5.6.tgz";
        name = "qs-0.5.6.tgz";
        sha1 = "31b1ad058567651c526921506b9a8793911a0384";
      })
    ];
    buildInputs =
      (self.nativeDeps."qs" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "qs" ];
  };
  by-spec."qs"."~5.2.0" =
    self.by-version."qs"."5.2.0";
  by-version."qs"."5.2.0" = lib.makeOverridable self.buildNodePackage {
    name = "qs-5.2.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/qs/-/qs-5.2.0.tgz";
        name = "qs-5.2.0.tgz";
        sha1 = "a9f31142af468cb72b25b30136ba2456834916be";
      })
    ];
    buildInputs =
      (self.nativeDeps."qs" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "qs" ];
  };
  by-spec."readable-stream"."1.1" =
    self.by-version."readable-stream"."1.1.13";
  by-version."readable-stream"."1.1.13" = lib.makeOverridable self.buildNodePackage {
    name = "readable-stream-1.1.13";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/readable-stream/-/readable-stream-1.1.13.tgz";
        name = "readable-stream-1.1.13.tgz";
        sha1 = "f6eef764f514c89e2b9e23146a75ba106756d23e";
      })
    ];
    buildInputs =
      (self.nativeDeps."readable-stream" or []);
    deps = {
      "core-util-is-1.0.2" = self.by-version."core-util-is"."1.0.2";
      "isarray-0.0.1" = self.by-version."isarray"."0.0.1";
      "string_decoder-0.10.31" = self.by-version."string_decoder"."0.10.31";
      "inherits-2.0.1" = self.by-version."inherits"."2.0.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "readable-stream" ];
  };
  by-spec."readable-stream"."~2.0.5" =
    self.by-version."readable-stream"."2.0.5";
  by-version."readable-stream"."2.0.5" = lib.makeOverridable self.buildNodePackage {
    name = "readable-stream-2.0.5";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/readable-stream/-/readable-stream-2.0.5.tgz";
        name = "readable-stream-2.0.5.tgz";
        sha1 = "a2426f8dcd4551c77a33f96edf2886a23c829669";
      })
    ];
    buildInputs =
      (self.nativeDeps."readable-stream" or []);
    deps = {
      "core-util-is-1.0.2" = self.by-version."core-util-is"."1.0.2";
      "inherits-2.0.1" = self.by-version."inherits"."2.0.1";
      "isarray-0.0.1" = self.by-version."isarray"."0.0.1";
      "process-nextick-args-1.0.6" = self.by-version."process-nextick-args"."1.0.6";
      "string_decoder-0.10.31" = self.by-version."string_decoder"."0.10.31";
      "util-deprecate-1.0.2" = self.by-version."util-deprecate"."1.0.2";
    };
    peerDependencies = [
    ];
    passthru.names = [ "readable-stream" ];
  };
  by-spec."request"."^2.51.0" =
    self.by-version."request"."2.67.0";
  by-version."request"."2.67.0" = lib.makeOverridable self.buildNodePackage {
    name = "request-2.67.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/request/-/request-2.67.0.tgz";
        name = "request-2.67.0.tgz";
        sha1 = "8af74780e2bf11ea0ae9aa965c11f11afd272742";
      })
    ];
    buildInputs =
      (self.nativeDeps."request" or []);
    deps = {
      "bl-1.0.1" = self.by-version."bl"."1.0.1";
      "caseless-0.11.0" = self.by-version."caseless"."0.11.0";
      "extend-3.0.0" = self.by-version."extend"."3.0.0";
      "forever-agent-0.6.1" = self.by-version."forever-agent"."0.6.1";
      "form-data-1.0.0-rc3" = self.by-version."form-data"."1.0.0-rc3";
      "json-stringify-safe-5.0.1" = self.by-version."json-stringify-safe"."5.0.1";
      "mime-types-2.1.9" = self.by-version."mime-types"."2.1.9";
      "node-uuid-1.4.7" = self.by-version."node-uuid"."1.4.7";
      "qs-5.2.0" = self.by-version."qs"."5.2.0";
      "tunnel-agent-0.4.2" = self.by-version."tunnel-agent"."0.4.2";
      "tough-cookie-2.2.1" = self.by-version."tough-cookie"."2.2.1";
      "http-signature-1.1.0" = self.by-version."http-signature"."1.1.0";
      "oauth-sign-0.8.0" = self.by-version."oauth-sign"."0.8.0";
      "hawk-3.1.3" = self.by-version."hawk"."3.1.3";
      "aws-sign2-0.6.0" = self.by-version."aws-sign2"."0.6.0";
      "stringstream-0.0.5" = self.by-version."stringstream"."0.0.5";
      "combined-stream-1.0.5" = self.by-version."combined-stream"."1.0.5";
      "isstream-0.1.2" = self.by-version."isstream"."0.1.2";
      "is-typedarray-1.0.0" = self.by-version."is-typedarray"."1.0.0";
      "har-validator-2.0.6" = self.by-version."har-validator"."2.0.6";
    };
    peerDependencies = [
    ];
    passthru.names = [ "request" ];
  };
  by-spec."rimraf"."~2.2.8" =
    self.by-version."rimraf"."2.2.8";
  by-version."rimraf"."2.2.8" = lib.makeOverridable self.buildNodePackage {
    name = "rimraf-2.2.8";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/rimraf/-/rimraf-2.2.8.tgz";
        name = "rimraf-2.2.8.tgz";
        sha1 = "e439be2aaee327321952730f99a8929e4fc50582";
      })
    ];
    buildInputs =
      (self.nativeDeps."rimraf" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "rimraf" ];
  };
  by-spec."shelljs"."0.3.x" =
    self.by-version."shelljs"."0.3.0";
  by-version."shelljs"."0.3.0" = lib.makeOverridable self.buildNodePackage {
    name = "shelljs-0.3.0";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/shelljs/-/shelljs-0.3.0.tgz";
        name = "shelljs-0.3.0.tgz";
        sha1 = "3596e6307a781544f591f37da618360f31db57b1";
      })
    ];
    buildInputs =
      (self.nativeDeps."shelljs" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "shelljs" ];
  };
  by-spec."sigmund"."~1.0.0" =
    self.by-version."sigmund"."1.0.1";
  by-version."sigmund"."1.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "sigmund-1.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/sigmund/-/sigmund-1.0.1.tgz";
        name = "sigmund-1.0.1.tgz";
        sha1 = "3ff21f198cad2175f9f3b781853fd94d0d19b590";
      })
    ];
    buildInputs =
      (self.nativeDeps."sigmund" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "sigmund" ];
  };
  by-spec."sntp"."1.x.x" =
    self.by-version."sntp"."1.0.9";
  by-version."sntp"."1.0.9" = lib.makeOverridable self.buildNodePackage {
    name = "sntp-1.0.9";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/sntp/-/sntp-1.0.9.tgz";
        name = "sntp-1.0.9.tgz";
        sha1 = "6541184cc90aeea6c6e7b35e2659082443c66198";
      })
    ];
    buildInputs =
      (self.nativeDeps."sntp" or []);
    deps = {
      "hoek-2.16.3" = self.by-version."hoek"."2.16.3";
    };
    peerDependencies = [
    ];
    passthru.names = [ "sntp" ];
  };
  by-spec."source-map"."^0.3.0" =
    self.by-version."source-map"."0.3.0";
  by-version."source-map"."0.3.0" = lib.makeOverridable self.buildNodePackage {
    name = "source-map-0.3.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/source-map/-/source-map-0.3.0.tgz";
        name = "source-map-0.3.0.tgz";
        sha1 = "8586fb9a5a005e5b501e21cd18b6f21b457ad1f9";
      })
    ];
    buildInputs =
      (self.nativeDeps."source-map" or []);
    deps = {
      "amdefine-1.0.0" = self.by-version."amdefine"."1.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "source-map" ];
  };
  by-spec."source-map"."^0.4.2" =
    self.by-version."source-map"."0.4.4";
  by-version."source-map"."0.4.4" = lib.makeOverridable self.buildNodePackage {
    name = "source-map-0.4.4";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/source-map/-/source-map-0.4.4.tgz";
        name = "source-map-0.4.4.tgz";
        sha1 = "eba4f5da9c0dc999de68032d8b4f76173652036b";
      })
    ];
    buildInputs =
      (self.nativeDeps."source-map" or []);
    deps = {
      "amdefine-1.0.0" = self.by-version."amdefine"."1.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "source-map" ];
  };
  by-spec."sshpk"."^1.7.0" =
    self.by-version."sshpk"."1.7.3";
  by-version."sshpk"."1.7.3" = lib.makeOverridable self.buildNodePackage {
    name = "sshpk-1.7.3";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/sshpk/-/sshpk-1.7.3.tgz";
        name = "sshpk-1.7.3.tgz";
        sha1 = "caa8ef95e30765d856698b7025f9f211ab65962f";
      })
    ];
    buildInputs =
      (self.nativeDeps."sshpk" or []);
    deps = {
      "asn1-0.2.3" = self.by-version."asn1"."0.2.3";
      "assert-plus-0.2.0" = self.by-version."assert-plus"."0.2.0";
      "dashdash-1.12.2" = self.by-version."dashdash"."1.12.2";
      "jsbn-0.1.0" = self.by-version."jsbn"."0.1.0";
      "tweetnacl-0.13.3" = self.by-version."tweetnacl"."0.13.3";
      "jodid25519-1.0.2" = self.by-version."jodid25519"."1.0.2";
      "ecc-jsbn-0.1.1" = self.by-version."ecc-jsbn"."0.1.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "sshpk" ];
  };
  by-spec."string_decoder"."~0.10.x" =
    self.by-version."string_decoder"."0.10.31";
  by-version."string_decoder"."0.10.31" = lib.makeOverridable self.buildNodePackage {
    name = "string_decoder-0.10.31";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/string_decoder/-/string_decoder-0.10.31.tgz";
        name = "string_decoder-0.10.31.tgz";
        sha1 = "62e203bc41766c6c28c9fc84301dab1c5310fa94";
      })
    ];
    buildInputs =
      (self.nativeDeps."string_decoder" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "string_decoder" ];
  };
  by-spec."stringstream"."~0.0.4" =
    self.by-version."stringstream"."0.0.5";
  by-version."stringstream"."0.0.5" = lib.makeOverridable self.buildNodePackage {
    name = "stringstream-0.0.5";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/stringstream/-/stringstream-0.0.5.tgz";
        name = "stringstream-0.0.5.tgz";
        sha1 = "4e484cd4de5a0bbbee18e46307710a8a81621878";
      })
    ];
    buildInputs =
      (self.nativeDeps."stringstream" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "stringstream" ];
  };
  by-spec."strip-ansi"."^0.3.0" =
    self.by-version."strip-ansi"."0.3.0";
  by-version."strip-ansi"."0.3.0" = lib.makeOverridable self.buildNodePackage {
    name = "strip-ansi-0.3.0";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/strip-ansi/-/strip-ansi-0.3.0.tgz";
        name = "strip-ansi-0.3.0.tgz";
        sha1 = "25f48ea22ca79187f3174a4db8759347bb126220";
      })
    ];
    buildInputs =
      (self.nativeDeps."strip-ansi" or []);
    deps = {
      "ansi-regex-0.2.1" = self.by-version."ansi-regex"."0.2.1";
    };
    peerDependencies = [
    ];
    passthru.names = [ "strip-ansi" ];
  };
  by-spec."strip-ansi"."^3.0.0" =
    self.by-version."strip-ansi"."3.0.0";
  by-version."strip-ansi"."3.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "strip-ansi-3.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/strip-ansi/-/strip-ansi-3.0.0.tgz";
        name = "strip-ansi-3.0.0.tgz";
        sha1 = "7510b665567ca914ccb5d7e072763ac968be3724";
      })
    ];
    buildInputs =
      (self.nativeDeps."strip-ansi" or []);
    deps = {
      "ansi-regex-2.0.0" = self.by-version."ansi-regex"."2.0.0";
    };
    peerDependencies = [
    ];
    passthru.names = [ "strip-ansi" ];
  };
  by-spec."strip-json-comments"."1.0.x" =
    self.by-version."strip-json-comments"."1.0.4";
  by-version."strip-json-comments"."1.0.4" = lib.makeOverridable self.buildNodePackage {
    name = "strip-json-comments-1.0.4";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/strip-json-comments/-/strip-json-comments-1.0.4.tgz";
        name = "strip-json-comments-1.0.4.tgz";
        sha1 = "1e15fbcac97d3ee99bf2d73b4c656b082bbafb91";
      })
    ];
    buildInputs =
      (self.nativeDeps."strip-json-comments" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "strip-json-comments" ];
  };
  by-spec."supports-color"."^0.2.0" =
    self.by-version."supports-color"."0.2.0";
  by-version."supports-color"."0.2.0" = lib.makeOverridable self.buildNodePackage {
    name = "supports-color-0.2.0";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/supports-color/-/supports-color-0.2.0.tgz";
        name = "supports-color-0.2.0.tgz";
        sha1 = "d92de2694eb3f67323973d7ae3d8b55b4c22190a";
      })
    ];
    buildInputs =
      (self.nativeDeps."supports-color" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "supports-color" ];
  };
  by-spec."supports-color"."^2.0.0" =
    self.by-version."supports-color"."2.0.0";
  by-version."supports-color"."2.0.0" = lib.makeOverridable self.buildNodePackage {
    name = "supports-color-2.0.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/supports-color/-/supports-color-2.0.0.tgz";
        name = "supports-color-2.0.0.tgz";
        sha1 = "535d045ce6b6363fa40117084629995e9df324c7";
      })
    ];
    buildInputs =
      (self.nativeDeps."supports-color" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "supports-color" ];
  };
  by-spec."tiny-lr-fork"."0.0.5" =
    self.by-version."tiny-lr-fork"."0.0.5";
  by-version."tiny-lr-fork"."0.0.5" = lib.makeOverridable self.buildNodePackage {
    name = "tiny-lr-fork-0.0.5";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/tiny-lr-fork/-/tiny-lr-fork-0.0.5.tgz";
        name = "tiny-lr-fork-0.0.5.tgz";
        sha1 = "1e99e1e2a8469b736ab97d97eefa98c71f76ed0a";
      })
    ];
    buildInputs =
      (self.nativeDeps."tiny-lr-fork" or []);
    deps = {
      "qs-0.5.6" = self.by-version."qs"."0.5.6";
      "faye-websocket-0.4.4" = self.by-version."faye-websocket"."0.4.4";
      "noptify-0.0.3" = self.by-version."noptify"."0.0.3";
      "debug-0.7.4" = self.by-version."debug"."0.7.4";
    };
    peerDependencies = [
    ];
    passthru.names = [ "tiny-lr-fork" ];
  };
  by-spec."tough-cookie"."~2.2.0" =
    self.by-version."tough-cookie"."2.2.1";
  by-version."tough-cookie"."2.2.1" = lib.makeOverridable self.buildNodePackage {
    name = "tough-cookie-2.2.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/tough-cookie/-/tough-cookie-2.2.1.tgz";
        name = "tough-cookie-2.2.1.tgz";
        sha1 = "3b0516b799e70e8164436a1446e7e5877fda118e";
      })
    ];
    buildInputs =
      (self.nativeDeps."tough-cookie" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "tough-cookie" ];
  };
  by-spec."tunnel-agent"."~0.4.1" =
    self.by-version."tunnel-agent"."0.4.2";
  by-version."tunnel-agent"."0.4.2" = lib.makeOverridable self.buildNodePackage {
    name = "tunnel-agent-0.4.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/tunnel-agent/-/tunnel-agent-0.4.2.tgz";
        name = "tunnel-agent-0.4.2.tgz";
        sha1 = "1104e3f36ac87125c287270067d582d18133bfee";
      })
    ];
    buildInputs =
      (self.nativeDeps."tunnel-agent" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "tunnel-agent" ];
  };
  by-spec."tweetnacl".">=0.13.0 <1.0.0" =
    self.by-version."tweetnacl"."0.13.3";
  by-version."tweetnacl"."0.13.3" = lib.makeOverridable self.buildNodePackage {
    name = "tweetnacl-0.13.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/tweetnacl/-/tweetnacl-0.13.3.tgz";
        name = "tweetnacl-0.13.3.tgz";
        sha1 = "d628b56f3bcc3d5ae74ba9d4c1a704def5ab4b56";
      })
    ];
    buildInputs =
      (self.nativeDeps."tweetnacl" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "tweetnacl" ];
  };
  by-spec."underscore"."~1.7.0" =
    self.by-version."underscore"."1.7.0";
  by-version."underscore"."1.7.0" = lib.makeOverridable self.buildNodePackage {
    name = "underscore-1.7.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/underscore/-/underscore-1.7.0.tgz";
        name = "underscore-1.7.0.tgz";
        sha1 = "6bbaf0877500d36be34ecaa584e0db9fef035209";
      })
    ];
    buildInputs =
      (self.nativeDeps."underscore" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "underscore" ];
  };
  by-spec."underscore.string"."~2.2.1" =
    self.by-version."underscore.string"."2.2.1";
  by-version."underscore.string"."2.2.1" = lib.makeOverridable self.buildNodePackage {
    name = "underscore.string-2.2.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/underscore.string/-/underscore.string-2.2.1.tgz";
        name = "underscore.string-2.2.1.tgz";
        sha1 = "d7c0fa2af5d5a1a67f4253daee98132e733f0f19";
      })
    ];
    buildInputs =
      (self.nativeDeps."underscore.string" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "underscore.string" ];
  };
  by-spec."underscore.string"."~2.3.3" =
    self.by-version."underscore.string"."2.3.3";
  by-version."underscore.string"."2.3.3" = lib.makeOverridable self.buildNodePackage {
    name = "underscore.string-2.3.3";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/underscore.string/-/underscore.string-2.3.3.tgz";
        name = "underscore.string-2.3.3.tgz";
        sha1 = "71c08bf6b428b1133f37e78fa3a21c82f7329b0d";
      })
    ];
    buildInputs =
      (self.nativeDeps."underscore.string" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "underscore.string" ];
  };
  by-spec."underscore.string"."~2.4.0" =
    self.by-version."underscore.string"."2.4.0";
  by-version."underscore.string"."2.4.0" = lib.makeOverridable self.buildNodePackage {
    name = "underscore.string-2.4.0";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/underscore.string/-/underscore.string-2.4.0.tgz";
        name = "underscore.string-2.4.0.tgz";
        sha1 = "8cdd8fbac4e2d2ea1e7e2e8097c42f442280f85b";
      })
    ];
    buildInputs =
      (self.nativeDeps."underscore.string" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "underscore.string" ];
  };
  by-spec."util-deprecate"."~1.0.1" =
    self.by-version."util-deprecate"."1.0.2";
  by-version."util-deprecate"."1.0.2" = lib.makeOverridable self.buildNodePackage {
    name = "util-deprecate-1.0.2";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/util-deprecate/-/util-deprecate-1.0.2.tgz";
        name = "util-deprecate-1.0.2.tgz";
        sha1 = "450d4dc9fa70de732762fbd2d4a28981419a0ccf";
      })
    ];
    buildInputs =
      (self.nativeDeps."util-deprecate" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "util-deprecate" ];
  };
  by-spec."verror"."1.3.6" =
    self.by-version."verror"."1.3.6";
  by-version."verror"."1.3.6" = lib.makeOverridable self.buildNodePackage {
    name = "verror-1.3.6";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/verror/-/verror-1.3.6.tgz";
        name = "verror-1.3.6.tgz";
        sha1 = "cff5df12946d297d2baaefaa2689e25be01c005c";
      })
    ];
    buildInputs =
      (self.nativeDeps."verror" or []);
    deps = {
      "extsprintf-1.0.2" = self.by-version."extsprintf"."1.0.2";
    };
    peerDependencies = [
    ];
    passthru.names = [ "verror" ];
  };
  by-spec."which"."~1.0.5" =
    self.by-version."which"."1.0.9";
  by-version."which"."1.0.9" = lib.makeOverridable self.buildNodePackage {
    name = "which-1.0.9";
    bin = true;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/which/-/which-1.0.9.tgz";
        name = "which-1.0.9.tgz";
        sha1 = "460c1da0f810103d0321a9b633af9e575e64486f";
      })
    ];
    buildInputs =
      (self.nativeDeps."which" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "which" ];
  };
  by-spec."xtend"."^4.0.0" =
    self.by-version."xtend"."4.0.1";
  by-version."xtend"."4.0.1" = lib.makeOverridable self.buildNodePackage {
    name = "xtend-4.0.1";
    bin = false;
    src = [
      (fetchurl {
        url = "http://registry.npmjs.org/xtend/-/xtend-4.0.1.tgz";
        name = "xtend-4.0.1.tgz";
        sha1 = "a5c6d532be656e23db820efb943a1f04998d63af";
      })
    ];
    buildInputs =
      (self.nativeDeps."xtend" or []);
    deps = {
    };
    peerDependencies = [
    ];
    passthru.names = [ "xtend" ];
  };
}
