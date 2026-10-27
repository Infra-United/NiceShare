# To run: nix develop 
# To reinitialize the: nix flake update
# Manuall uv sync: uv sync --dev 
# To run the project: uv run niceshare

{
  description = "NiceShare development environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python314
            uv
            tk
            gcc-unwrapped
            ruff 
          ];

          shellHook = ''
            export LD_LIBRARY_PATH=${pkgs.gcc-unwrapped.lib}/lib:$LD_LIBRARY_PATH
            export UV_PYTHON_PREFERENCE=only-system
            export UV_PYTHON=python314

            echo "Python: $(python --version)"
            echo "Syncing dependencies..."
            uv sync --dev
            echo "Start with \"uv run niceshare\""
          '';
        };
      }
    );
}