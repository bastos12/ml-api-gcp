import os
from flask import (
    Flask,
    request,
)
from flask.helpers import send_from_directory
from flask_cors import (
    CORS,
    cross_origin
)
from back.model import (
    MaskDetector,
    SaveData
)
from back.utils import image_to_array

# application
app = Flask(__name__, static_folder='./myapp/build', static_url_path='/')
CORS(app)

# API detection du masque
@app.route("/api/importationimage", methods=['POST'])
@cross_origin()
def upload_image():
    filename = request.files["image"].filename
    image_bytes = request.files["image"]
    image_array = image_to_array(image_bytes)
    detector = MaskDetector()
    output = detector.detection(image_array)
    # inserer votre propre bucket ici
    save = SaveData(os.environ.get('BUCKET_NAME'))
    save.save_image(filename, output)
    return "Image uploaded successfully", 200

@app.route("/")
@cross_origin()
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory(app.static_folder, 'index.html'), 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
