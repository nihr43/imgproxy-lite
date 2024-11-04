from flask import Flask, request, send_file
from PIL import Image
import requests
import time
import uuid
from io import BytesIO

app = Flask(__name__)


# wget http://127.0.0.1:5000/?img=main.jpg&q=33


@app.route("/")
def convert():
    image_url = f"https://cdn.nih.earth/web-assets/{request.args.get('img')}"
    cache_key = str(uuid.uuid5(uuid.NAMESPACE_OID, request.url))

    try:
        with open(cache_key, "rb") as f:
            image_stream = BytesIO(f.read())

        print("cache hit")
        image_stream.seek(0)
        return send_file(image_stream, mimetype="image/jpeg")
    except FileNotFoundError:
        print("cache miss")
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_stream = BytesIO(response.content)

        except requests.exceptions.RequestException as e:
            return f"Failed to fetch image: {e}", 500

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

            with open(cache_key, "wb") as f:
                f.write(membuf.getvalue())

            membuf.seek(0)
            return send_file(membuf, mimetype="image/jpeg")
        except TypeError:
            return send_file(image_stream, mimetype="image/jpeg")
