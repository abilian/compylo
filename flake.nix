{
  description = "Compylo";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        stdenv = with pkgs; overrideCC clangStdenv [
          llvmPackages_14.llvm
          llvmPackages_14.bintools
          clang_14
        ];
        pythonPackages = pkgs.python310.withPackages
          (p: with p; [
            llvmlite
          ]);
      in
      rec {
        packages = flake-utils.lib.flattenTree
          {
            "compylo" = stdenv.mkDerivation
              {
                pname = "compylo";
                version = "0.1";
                srs = ./.;
                nativeBuildInputs = [
                  (pkgs.python310.withPackages
                    (p: with p; [ llvmlite ]))
                ];
              };
          };
        defaultPackage = packages."compylo";
        devShell = pkgs.mkShell.override { inherit stdenv; } {
          inputsFrom = [ packages."compylo" ];
          packages = [
            pkgs.wasmer
            pkgs.pre-commit
            pkgs.ruff
            pkgs.poetry
            (pkgs.python3.withPackages
              (p: with p; [ black pyyaml pytest ]))
          ];
        };
      }
    );
}
