inputs:
let
  inherit (inputs.nixpkgs)
    lib
    ;

  inherit (lib.attrsets)
    genAttrs
    ;

  inherit (lib.sources)
    cleanSource
    ;
in
genAttrs
  [
    "x86_64-linux"
    "aarch64-linux"
  ]
  (
    system:
    let
      pkgs = inputs.self.legacyPackages.${system};
    in
    {
      core = pkgs.testers.runNixOSTest (import ./core.nix { inherit inputs; });
      loghost = pkgs.testers.runNixOSTest ./loghost.nix;

      pytest-facts =
        let
          testPython = (
            pkgs.python3.withPackages (
              pythonPackages: with pythonPackages; [
                pylint
                pytest
                jinja2
              ]
            )
          );
        in
        (pkgs.runCommand "pytest-facts" { } ''
          cp -r --no-preserve=mode ${cleanSource inputs.self}/* .
          cd facts
          ${testPython}/bin/pylint --persistent n *.py
          ${testPython}/bin/pytest -vv -p no:cacheprovider
          touch $out
        '');

      duplicates-facts = (
        pkgs.runCommand "duplicates-facts" { buildInputs = [ pkgs.fish ]; } ''
          cp -r --no-preserve=mode ${cleanSource inputs.self}/* .
          cd facts
          fish test_duplicates.fish
          touch $out
        ''
      );

      perl-switches = (
        pkgs.runCommand "perl-switches"
          {
            buildInputs = [
              pkgs.gnumake
              pkgs.perl
            ];
          }
          ''
            cp -r --no-preserve=mode ${cleanSource inputs.self}/* .
            cd switch-configuration
            make .lint
            make .build-switch-configs
            touch $out
          ''
      );

      openwrt-golden =
        pkgs.runCommand "openwrt-golden"
          {
            buildInputs = [
              pkgs.diffutils
              pkgs.gomplate
            ];
          }
          ''
            cp -r --no-preserve=mode ${cleanSource inputs.self}/* .
            cd tests/unit/openwrt
            mkdir -p $out/tmp/ar71xx
            ${pkgs.bash}/bin/bash test.sh -t ar71xx -o $out
          '';

      formatting = inputs.self.formatterModule.${system}.config.build.check inputs.self;

    }
  )
