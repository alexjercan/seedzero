{
  description = "Seed Zero: simulation-driven YouTube Shorts studio";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = inputs: let
    systems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
    eachSystem = f:
      builtins.listToAttrs (map (system: {
        name = system;
        value = f inputs.nixpkgs.legacyPackages.${system};
      }) systems);
  in {
    devShells = eachSystem (pkgs: {
      default = pkgs.mkShell {
        packages = with pkgs; [
          (python3.withPackages (ps:
            with ps; [
              numpy
              pillow
              google-api-python-client
              google-auth-oauthlib
            ]))
          ffmpeg
          imagemagick
          jq
          curl
        ];
        SEED_ZERO_FONT = "${pkgs.dejavu_fonts}/share/fonts/truetype/DejaVuSans-Bold.ttf";
      };
    });

    checks = eachSystem (pkgs: {
      shell-syntax =
        pkgs.runCommand "shell-syntax" {src = ./scripts;} ''
          for f in "$src"/*.sh; do
            ${pkgs.bash}/bin/bash -n "$f"
          done
          touch "$out"
        '';
    });
  };
}
