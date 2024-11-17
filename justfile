build: lint
  buildah build --tag imgproxy-lite .
  buildah push imgproxy-lite docker://images.local:5000/imgproxy-lite:latest
  kubectl rollout restart deployments/imgproxy-lite
  kubectl rollout restart deployments/imgproxy-lite-gc

run: lint
  nix-shell . --run 'python3 app.py --serve'

gc: lint
  nix-shell . --run 'python3 app.py --gc'

lint:
  black .
  flake8 . --ignore=E501,W503
