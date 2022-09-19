{ pkgs ? import <nixpkgs> {}} :

let
  pythonPackages = pkgs.python310.withPackages (p: with p; [
    llvmlite
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
