let
  pkgs = import <nixpkgs> {};
  inherit (pkgs) lib;
  nix-ip = pkgs.fetchFromGitHub {
    owner = "djacu";
    repo = "nix-ip";
    rev = "main";
    hash = "sha256-T08YBrSIiiHbAGL5anFCAREoycGfBSQCntUkyXgBzWo=";
  };
  ipv4 = import (nix-ip + "/default.nix") { inherit lib;};

  vlanDir = builtins.readDir ../switch-configuration/config/vlans.d;
  files = lib.attrNames (lib.filterAttrs (name: value: value == "regular") vlanDir);

  vlanFiles = lib.splitString "\n" (lib.concatStrings (builtins.map (x: builtins.readFile ../switch-configuration/config/vlans.d/${x}) files));
  realVlans = builtins.filter (x:
    if x == ""
      then false
    else if builtins.match "^//.*" x == null
      then true
    else
      false
  ) vlanFiles;
  allVlansRaw = builtins.map (builtins.split "\t+") realVlans;
  allVlans = builtins.map (elem: builtins.filter (x: x!= []) elem ) allVlansRaw;

  allVlanProperties = builtins.map (
    x: let
      name = builtins.elemAt x 1;
      id = builtins.elemAt x 2;
      ipv6 = builtins.elemAt x 3;
      ipv4cidr = builtins.elemAt x 4;
      description = builtins.elemAt x 5;

  in
    { inherit
        name
        id
        ipv6
        description;
        ipv4Props = ipv4.getNetworkProperties ipv4cidr;
    }

  ) allVlans;
in
  #ipv4.getNetworkProperties "192.168.23.10/24"
  #vlanFile
  #files
  #allVlans
  #realVlans
  allVlanProperties
  #builtins.readDir ../switch-configuration/config/vlans.d
  #vlanFiles
