let
  pkgs = import <nixpkgs> {};
  inherit (pkgs) lib;
  baseDir = ../switch-configuration/config/vlans.d;
  vlansD = builtins.readDir baseDir;
  files = lib.attrNames (lib.filterAttrs (name: value: value == "regular") vlansD);
in
  files
