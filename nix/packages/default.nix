inputs:
inputs.nixpkgs.lib.genAttrs
  [
    "x86_64-linux"
    "aarch64-linux"
  ]
  (system: {
    inherit (inputs.self.legacyPackages.${system}.scale-network)
      dhcptest
      mac2eui64
      makeDhcpd
      massflash
      scaleInventory
      serverspec
      perlNetArp
      perlNetInterface
      perlNetPing
      ;
  })
