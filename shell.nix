{ pkgs ? import <nixpkgs> {}} :

let
  pythonPackages = pkgs.python310.withPackages (p: with p; [
    llvmlite
    black
    pyyaml
    termcolor
  ]);
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    pythonPackages
    pre-commit
    wasmer
    llvmPackages_14.llvm
    llvmPackages_14.bintools
    clang_14
  ];
}
