{ pkgs ? import <nixpkgs> { } }:

let
  pythonEnv = pkgs.python312.withPackages (ps: with ps; [
    flask
    requests
    pillow
    kubernetes
  ]);
in

if builtins.getEnv "BUILD" == "1"
then pythonEnv
else pkgs.mkShell {
  name = "python-dev-env";
  buildInputs = [
    pkgs.python312
    pythonEnv
  ];
}
