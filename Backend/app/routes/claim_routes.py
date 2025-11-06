
from flask_restful import Resource, Api, reqparse
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ocr_service import process_pdf
from app.services.data_extraction import extract_structured_data
from app.services.ml_service import predict_fraud_and_reserve
from app.models import Claim
from app import db
import os
import logging
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint for claim routes
claim_bp = Blueprint('claim', __name__)
api = Api(claim_bp)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UploadClaim(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True, help="PDF file is required")
        args = parser.parse_args()

        file = args['file']
        if not allowed_file(file.filename):
            return {'message': 'Only PDF files are allowed'}, 400

        try:
            # Save file temporarily
            upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Process PDF
            raw_text = process_pdf(file_path)
            extracted_data = extract_structured_data(raw_text)

            # Create claim
            user_identity = get_jwt_identity()
            claim = Claim(
                user_id=user_identity['id'],
                pdf_filename=filename,
                extracted_data=extracted_data,
                status='pending'
            )
            db.session.add(claim)
            db.session.commit()

            # Predict fraud and reserve
            prediction = predict_fraud_and_reserve(claim.id, extracted_data)

            logger.info("Claim uploaded and processed: %s", filename)
            return {
                'message': 'Claim processed successfully',
                'claim': {
                    'id': claim.id,
                    'user_id': claim.user_id,
                    'pdf_filename': claim.pdf_filename,
                    'status': claim.status,
                    'prediction': prediction
                }
            }, 201
        except Exception as e:
            logger.error("Error processing claim: %s", str(e))
            return {'message': f"Failed to process claim: {str(e)}"}, 400

class Prediction(Resource):
    @jwt_required()
    def get(self, claim_id: int):
        try:
            claim = Claim.query.get_or_404(claim_id)
            prediction = Prediction.query.filter_by(claim_id=claim_id).first()
            if not prediction:
                return {'message': 'No prediction found for this claim'}, 404
            
            user_identity = get_jwt_identity()
            if claim.user_id != user_identity['id'] and user_identity['role'] != 'admin':
                return {'message': 'Unauthorized access to claim'}, 403

            return {
                'claim_id': claim.id,
                'fraud_score': prediction.fraud_score,
                'is_fraudulent': prediction.is_fraudulent,
                'reserve_estimate': prediction.reserve_estimate,
                'model_version': prediction.model_version
            }, 200
        except Exception as e:
            logger.error("Error retrieving prediction for claim %d: %s", claim_id, str(e))
            return {'message': f"Failed to retrieve prediction: {str(e)}"}, 400

# Add resources to API
api.add_resource(UploadClaim, '/upload-claim')
api.add_resource(Prediction, '/predictions/<int:claim_id>')