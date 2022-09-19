{ pkgs ? import <nixpkgs> {}} :

pkgs.mkShell {
  buildInputs = with pkgs; [
    python310
    wasmer
    llvm  # FIXME: this is LLVM v11.0, is it the one we want or should we use
          # a more recent version ? (If so, we need to make our own lib)
  ];
}
