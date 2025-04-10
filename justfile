build: lint
  docker load < $(BUILD=1 nix build -f default.nix --no-link --print-out-paths)
  docker push images.local:5000/imgproxy-lite
  kubectl rollout restart deployments/imgproxy-lite

run: lint
  nix-shell --run 'python3 app.py --serve'

gc: lint
  nix-shell --run 'python3 app.py --gc'

lint:
  black .
  flake8 . --ignore=E501,W503
