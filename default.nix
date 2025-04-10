{ pkgs ? import <nixpkgs> { } }:

let
  pythonEnv = pkgs.python312.withPackages (ps: with ps; [
    flask
    requests
    pillow
    waitress
  ]);

  devShell = pkgs.mkShell {
    name = "python-dev-env";
    buildInputs = [
      pythonEnv
    ];
  };

  dockerImage = pkgs.dockerTools.buildLayeredImage {
    name = "images.local:5000/imgproxy-lite";
    tag = "latest";
    contents = [ pythonEnv ];
    config = {
      Cmd = [ "${pythonEnv}/bin/python" "-u" "app.py" ];
      WorkingDir = "/opt";
    };
    extraCommands = ''
      mkdir -p ./opt
      cp ${./app.py} ./opt/app.py
    '';
  };

in

if builtins.getEnv "BUILD" == "1"
then dockerImage
else devShell
