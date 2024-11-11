from nixos/nix
arg BUILD=1

copy default.nix .
run nix-channel --add https://nixos.org/channels/nixos-24.05 nixpkgs
run nix-env -if default.nix

workdir /opt
copy app.py .

cmd ["python3", "app.py"]
