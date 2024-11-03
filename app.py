from flask import Flask, request, send_file
from PIL import Image
import requests
import time
from io import BytesIO

app = Flask(__name__)


# wget http://127.0.0.1:5000/?img=main.jpg&q=33


@app.route("/")
def convert():
    image_url = f"https://cdn.nih.earth/web-assets/{request.args.get('img')}"
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        image_stream = BytesIO(response.content)
        image_obj = Image.open(image_stream)
        image_stream.seek(0)

        try:
            q = int(request.args.get("q"))
            start = time.time()
            membuf = BytesIO()
            image_obj.save(membuf, format="jpeg", quality=q)
            membuf.seek(0)
            elapsed = time.time() - start
            print(f"converting took {elapsed}")

            return send_file(membuf, mimetype="image/jpeg")
        except TypeError:
            return send_file(image_stream, mimetype="image/jpeg")

    except requests.exceptions.RequestException as e:
        return f"Failed to fetch image: {e}", 500
