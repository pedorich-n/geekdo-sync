{ inputs, ... }:
{
  imports = [
    inputs.flake-parts.flakeModules.partitions
  ];

  partitions.dev = {
    extraInputsFlake = ../dev;
    module = {
      imports = [
        ../dev/flake-module.nix
      ];

      perSystem = _: {
        treefmt.config = {
          projectRoot = ../.;

          programs = {
            ruff-format.enable = true;
            ruff-check.enable = true;
          };

          settings = {
            formatter.deadnix.excludes = [
              "flake-parts/nixosModules.nix"
            ];
          };
        };
      };
    };
  };

  partitionedAttrs = {
    devShells = "dev";
    checks = "dev";
    formatter = "dev";
  };
}
