from alpine:3.20

run apk add py3-pip
run pip install flask pillow requests --break-system-packages

workdir /opt
copy app.py .

cmd ["flask", "run", "-h", "0.0.0.0"]
