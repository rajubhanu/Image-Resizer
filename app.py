from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import io
import zipfile

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_SIZE_MB = 4.5
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        width = int(request.form["width"])
        height = int(request.form["height"])
        format_option = request.form["format"].upper()
        files = request.files.getlist("images")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for file in files:
                if file.filename.endswith((".jpg", ".jpeg", ".png")):
                    file.seek(0, os.SEEK_END)
                    size = file.tell()
                    file.seek(0)

                    if size > MAX_SIZE_BYTES:
                        return f"File '{file.filename}' is too large! Limit: 4.5MB"

                    img = Image.open(file)
                    img = img.resize((width, height))

                    output_io = io.BytesIO()
                    save_name = os.path.splitext(file.filename)[0] + "." + format_option.lower()
                    img.save(output_io, format=format_option)
                    output_io.seek(0)

                    zipf.writestr(save_name, output_io.read())

        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name="resized_images.zip", mimetype='application/zip')

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
