{ nixpkgs ? import <nixpkgs> {  } }:

let
  pkgs = with nixpkgs.python312Packages; [
    flask
    requests
    pillow
  ];

in
  nixpkgs.stdenv.mkDerivation {
    name = "env";
    buildInputs = pkgs;
  }
