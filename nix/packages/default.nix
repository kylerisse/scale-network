inputs:
inputs.nixpkgs.lib.genAttrs
  [
    "x86_64-linux"
    "aarch64-linux"
  ]
  (system: {
    inherit (inputs.self.legacyPackages.${system}.scale-network)
      massflash
      scaleInventory
      serverspec
      ;
  })