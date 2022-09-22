{ pkgs ? import <nixpkgs> {}} :

let
  pythonPackages = pkgs.python310.withPackages (p: with p; [
    llvmlite
    black
  ]);
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    pythonPackages
    wasmer
    libllvm
    llvm
  ];
}
