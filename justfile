build: lint
  buildah build --tag imgproxy-lite .
  buildah push imgproxy-lite docker://images.local:5000/imgproxy-lite:latest
  kubectl rollout restart deployments/imgproxy-lite

run: lint
  nix-shell . --run 'python3 app.py'

lint:
  black .
  flake8 . --ignore=E501,W503
