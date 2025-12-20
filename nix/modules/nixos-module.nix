{ package }:
{ config
, systemdUtils
, lib
, pkgs
, ...
}:
let
  inherit (systemdUtils.unitOptions) unitOption;

  cfg = config.services.geekdo-sync;
in
{
  options = {
    services.geekdo-sync = {
      enable = lib.mkEnableOption "geekdo-sync";

      package = lib.mkOption {
        type = lib.types.package;
        default = package;
      };

      environment = lib.mkOption {
        type = lib.types.submodule {
          freeformType = unitOption;
          options = {
            GRIST_DOC_ID = lib.mkOption {
              type = lib.types.str;
            };
          };
        };

        default = { };
      };

      environmentFile = lib.mkOption {
        type = lib.types.listOf lib.types.path;
        default = [ ];
      };

      timerConfig = lib.mkOption {
        type = lib.types.nullOr (lib.types.attrsOf unitOption);
        default = {
          OnCalendar = "daily";
          Persistent = true;
        };
        description = ''
          When to run the backup. See {manpage}`systemd.timer(5)` for
          details. If null no timer is created and the backup will only
          run when explicitly started.
        '';
        example = {
          OnCalendar = "00:05";
          RandomizedDelaySec = "5h";
          Persistent = true;
        };
      };
    };
  };

  config = lib.mkIf cfg.enable {
    systemd = {
      timers.geekdo-sync = lib.mkIf (cfg.timerConfig != null) {
        description = "Timer for Geekdo Sync";
        wantedBy = [ "timers.target" ];

        timerConfig = cfg.timerConfig;
      };

      services.geekdo-sync = {
        description = "Geekdo Sync";
        wantedBy = [ "multi-user.target" ];
        after = [ "network-online.target" ];

        serviceConfig = {
          ExecStart = lib.getExe cfg.package;

          Environment = cfg.environment;
          EnvironmentFile = cfg.environmentFile;

          # Hardening
          AmbientCapabilities = [ ];
          CapabilityBoundingSet = [ ];
          LockPersonality = true;
          PrivateDevices = true;
          PrivateTmp = true;
          PrivateUsers = true;
          DynamicUser = true;
          ProtectKernelModules = true;
          ProtectKernelTunables = true;
          ProtectKernelLogs = true;
          ProtectControlGroups = true;
          RestrictSUIDSGID = true;
          RestrictNamespaces = true;
          ProtectClock = true;
          ProtectSystem = "strict";
          NoNewPrivileges = true;
          RestrictAddressFamilies = [
            "AF_INET"
            "AF_INET6"
          ];
        };
      };
    };
  };
}
