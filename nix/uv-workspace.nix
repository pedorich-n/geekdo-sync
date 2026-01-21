{
  pkgs,
  lib,
  uv2nix,
  pyproject-nix,
  pyproject-build-systems,
}:
let
  inherit (pkgs.callPackages pyproject-nix.build.util { }) mkApplication;

  python = pkgs.python313;

  workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ../.; };

  overlay = workspace.mkPyprojectOverlay {
    # Prefer prebuilt binary wheels as a package source.
    # Sdists are less likely to "just work" because of the metadata missing from uv.lock.
    # Binary wheels are more likely to, but may still require overrides for library dependencies.
    sourcePreference = "wheel";
  };

  pyproject-packages = pkgs.callPackage pyproject-nix.build.packages {
    inherit python;
  };

  pythonSet = pyproject-packages.overrideScope (
    lib.composeManyExtensions [
      pyproject-build-systems.overlays.default
      overlay
    ]
  );

  venv = (pythonSet.mkVirtualEnv "geekdo-sync-env" workspace.deps.default).overrideAttrs (old: {
    passthru = lib.recursiveUpdate (old.passthru or { }) {
      inherit python;
    };
  });

  ruff = pythonSet.ruff.overrideAttrs (old: {
    meta = old.meta or { } // {
      mainProgram = "ruff";
    };
  });
in
{
  inherit venv python ruff;

  geekdo-sync = mkApplication {
    inherit venv;
    package = pythonSet.geekdo-sync;
  };
}
