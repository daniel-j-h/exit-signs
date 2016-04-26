# Nix development environment for reproducible builds.
# Enter development environment via `nix-shell`.
#
# Resources:
# - https://nixos.org/nix/
# - https://nixos.org/nix/manual/#chap-quick-start
# - https://nixos.org/nixpkgs/manual/

with import <nixpkgs> {}; {
  devEnv = stdenv.mkDerivation {
    name = "exit-signs";
    buildInputs = [ cmake ninja boost zlib ];
  };
}
