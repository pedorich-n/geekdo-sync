{ flake-parts-lib, moduleWithSystem, ... }:
{
  flake.nixosModules = {
    default = moduleWithSystem (
      perSystem@{ config, ... }: # NOTE: only explicitly named parameters will be in perSystem
      (flake-parts-lib.importApply ../nix/modules/nixos-module.nix { package = perSystem.config.packages.geekdo-sync; })
    );
  };
}
