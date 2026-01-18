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

      perSystem =
        { config, ... }:
        {
          treefmt.config = {
            projectRoot = ../.;

            programs = {
              # Use uv-provided ruff.
              ruff-format = {
                enable = true;
                package = config.packages.ruff;
              };
              ruff-check = {
                enable = true;
                package = config.packages.ruff;
              };
            };

            settings = {
              formatter.deadnix.excludes = [
                "flake-parts/nixos-modules.nix"
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
