{ inputs, ... }:
{
  perSystem =
    { pkgs, lib, ... }:
    {
      packages =
        let
          uv-workspace = import ../nix/packages/uv-workspace.nix {
            inherit pkgs lib;
            inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
          };

        in
        {
          inherit (uv-workspace) venv geekdo-sync;
        };
    };
}
