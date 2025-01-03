import os
import base64
import qrcode
from io import BytesIO
from flask import Blueprint, request, send_file
from zeep import Client
from PyPDF2 import PdfReader, PdfWriter

sign_blueprint = Blueprint('sign', __name__)
UPLOAD_FOLDER = 'uploads'
SIGNED_FOLDER = 'signed'

API_URL = "http://<hostname>:8080/signserver/ClientWSService/ClientWS?wsdl"
REQUESTER_NAME = "exampleRequester"


def sign_document(api_url, requester_name, document_path):
    client = Client(wsdl=api_url)
    with open(document_path, "rb") as file:
        document_data = base64.b64encode(file.read()).decode()
    response = client.service.sign(requester_name, document_path, document_data)
    return response.signature, base64.b64decode(response.signedDocument)


def generate_qr_code(data):
    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def overlay_qr_on_pdf(signed_pdf_data, qr_img, output_path):
    reader = PdfReader(BytesIO(signed_pdf_data))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_path, "wb") as output_file:
        writer.write(output_file)


@sign_blueprint.route('/sign', methods=['POST'])
def sign():
    uploaded_file = request.files['file']
    if not uploaded_file or uploaded_file.filename == '':
        return "No file uploaded", 400

    input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
    uploaded_file.save(input_path)

    try:
        signature, signed_pdf_data = sign_document(API_URL, REQUESTER_NAME, input_path)
        qr_image = generate_qr_code(signature)
        output_path = os.path.join(SIGNED_FOLDER, f"signed_{uploaded_file.filename}")
        overlay_qr_on_pdf(signed_pdf_data, qr_image, output_path)
        return send_file(output_path, as_attachment=True, download_name=f"signed_{uploaded_file.filename}")
    except Exception as e:
        return f"Error occurred: {e}", 500
