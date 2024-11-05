from flask import Flask, request, send_file
from PIL import Image
import requests
import time
import uuid
import os
from io import BytesIO

app = Flask(__name__)


def prune_cache(directory, limit=100):
    files_with_dates = [
        (f, os.path.getctime(os.path.join(directory, f)))
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

    files_with_dates.sort(key=lambda x: x[1], reverse=True)
    recent_files = files_with_dates[:limit]
    recent_filenames = {f[0] for f in recent_files}

    for filename, _ in files_with_dates[limit:]:
        if filename not in recent_filenames:
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                print(f"{file_path} pruned")
            except (FileNotFoundError, OSError) as e:
                print(f"{file_path} pruning failed: {e}")


@app.route("/")
def convert():
    image_url = f"https://cdn.nih.earth/web-assets/{request.args.get('img')}"
    cache_key = str(uuid.uuid5(uuid.NAMESPACE_OID, request.url))

    try:
        with open(f"artifacts/{cache_key}", "rb") as f:
            image_stream = BytesIO(f.read())

        print("cache hit")
        image_stream.seek(0)
        return send_file(image_stream, mimetype="image/jpeg")
    except (FileNotFoundError, IOError, OSError, EOFError):
        print("cache miss")
        prune_cache("artifacts")
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

            try:
                with open(f"artifacts/{cache_key}", "wb") as f:
                    f.write(membuf.getvalue())
            except (OSError, IOError) as e:
                print(f"error writing cache object: {e}")
                # in out-of-space scenarios, it appears the empty file is still created,
                # which then causes subequent 'hits' on the empty file:
                try:
                    os.remove(f"artifacts/{cache_key}")
                except FileNotFoundError:
                    pass

            membuf.seek(0)
            return send_file(membuf, mimetype="image/jpeg")
        except TypeError:
            return send_file(image_stream, mimetype="image/jpeg")


def main():
    os.makedirs("artifacts", exist_ok=True)
    app.run(debug=False, host="0.0.0.0")


if __name__ == "__main__":
    main()
