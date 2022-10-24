{ pkgs ? import <nixpkgs> {} }:

let
  pythonPackages = pkgs.python310.withPackages (p: with p; [
    llvmlite
    black
  ]);
in
pkgs.pkgsCross.wasi32.stdenv.mkDerivation {
  pname = "compylo";
  version = "0.1";

  src = ./src;

  buildInputs = with pkgs; [
    pythonPackages
    pre-commit
    clang_14
    llvmPackages_14.llvm
    llvmPackages_14.bintools
    wasilibc
    wasmer
  ];

  buildPhase = ''
    python $src/translator.py > toto.ll
    clang-14 --target=wasm32-unknown-wasi -o test toto.ll
  '';

  installPhase = ''
      runHook preinstall

      mkdir -p $out/bin
      cp test $out/bin
      cp toto.ll $out/

      runHook postinstall
    '';
}
