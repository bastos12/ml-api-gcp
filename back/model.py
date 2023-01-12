from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from google.cloud import storage
import cv2
import os
import numpy as np

# credential
# inserer vos propres credentials
GCP_CREDENTIAL_UPLOAD = {
    "type": os.environ.get('TYPE'),
    "project_id":os.environ.get('PROJECT_ID'),
    "private_key_id":os.environ.get('PRIVATE_KEY_ID'),
    "private_key":os.environ.get('PRIVATE_KEY'),
    "client_email":os.environ.get('CLIENT_EMAIL'),
    "client_id":os.environ.get('CLIENT_ID'),
    "auth_uri":os.environ.get('AUTH_URI'),
    "token_uri":os.environ.get('TOKEN_URI'),
    "auth_provider_x509_cert_url":os.environ.get('AUTH_TOKEN_PROVIDER'),
    "client_x509_cert_url":os.environ.get('CLIENT_CERT_URL')
}

class MaskDetector:
    def __init__(self):
        self.model = load_model(os.getcwd() + "/back/model/mask_detector.model")
        self.net = cv2.dnn.readNet(
            os.getcwd() + "/back/model/deploy.prototxt",
            os.getcwd() + "/back/model/res10_300x300_ssd_iter_140000.caffemodel"
            )
    
    @staticmethod
    def read_image_open_cv(image_array):
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return image
    
    @staticmethod
    def reshape_image(image):
        (h, w) = image.shape[:2]
        return (h, w)
    
    @staticmethod
    def blob_construction(image):
        blob = cv2.dnn.blobFromImage(image,1.0, (300, 300),(104.0, 177.0, 123.0))
        return blob
    
    @staticmethod
    def coordonate_frame(startX, startY, endX, endY, w, h):
        (startX, startY) = (max(0, startX), max(0, startY))
        (endX, endY) = (min(w - 1, endX), min(h - 1, endY))
        return (startX, startY, endX, endY)
    
    @staticmethod
    def face_process(image, startY, endY, startX, endX):
        face = image[startY:endY, startX:endX]
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = cv2.resize(face, (224, 224))
        face = img_to_array(face)
        face = preprocess_input(face)
        face = np.expand_dims(face, axis=0)
        return face
    
    @staticmethod
    def check_label(mask, withoutMask):
        label = "Masque" if mask > withoutMask else "Pas de masque"
        return label
    
    @staticmethod
    def design_label(label, mask, withoutMask):
        label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
        return label
    
    @staticmethod
    def check_color(label):
        color = (0, 255, 0) if label == "Masque" else (0, 0, 255)
        return color
    
    @staticmethod
    def construct_shape_detection(image, label, startX, startY, endX, endY, color):
        cv2.putText(image, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
        cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)
        return image
    
    @staticmethod
    def encoding_for_saving(image):
        _, img_encoded = cv2.imencode('.jpg', image)
        return img_encoded

    def predict(self, face):
        (mask, withoutMask) = self.model.predict(face)[0]
        return (mask, withoutMask)
    
    def detection(self, image_array):
        image = self.read_image_open_cv(image_array)
        (h, w) = self.reshape_image(image)
        blob = self.blob_construction(image)
        self.net.setInput(blob)
        detections = self.net.forward()
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                (startX, startY, endX, endY) = self.coordonate_frame(startX, startY, endX, endY, w, h)
                face = self.face_process(image, startY, endY, startX, endX)
                (mask, withoutMask) = self.predict(face)
                label = self.check_label(mask, withoutMask)
                color = self.check_color(label)
                label = self.design_label(label, mask, withoutMask)
                image = self.construct_shape_detection(image, label, startX, startY, endX, endY, color)
                img_encoded = self.encoding_for_saving(image)
                return img_encoded


class SaveData():
    def __init__(self, bucket_name) -> None:
        self.client = storage.Client.from_service_account_info(GCP_CREDENTIAL_UPLOAD)
        self.bucket = self.client.bucket(bucket_name)

    def save_image(self, filename, img_encoded):
        blob = self.bucket.blob(filename)
        blob.upload_from_string(img_encoded.tobytes(), 'image/jpeg')