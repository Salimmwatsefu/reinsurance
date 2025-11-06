from flask_restful import Resource, Api
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.ml_service import train_fraud_model, train_reserve_model
from app.models import ModelStats
from app import db
import logging
import pandas as pd
from werkzeug.exceptions import BadRequest
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint for ML routes
ml_bp = Blueprint('ml', __name__)
api = Api(ml_bp)

# Path to CSV data
CSV_DATA_PATH = "/home/sjet/salim/reinsurance/Backend/app/data/synthetic_claims.csv"

class TrainFraudModel(Resource):
    @jwt_required()
    def post(self):
        claims = get_jwt()

        if claims["role"] != "admin":
            return {"message": "Admin access required"}, 403

        # Check if CSV exists
        if not os.path.exists(CSV_DATA_PATH):
            logger.error("CSV data file not found at %s", CSV_DATA_PATH)
            return {"message": "Training CSV not found"}, 400

        try:
            data = pd.read_csv(CSV_DATA_PATH)
            if data.empty:
                raise BadRequest("CSV data is empty")

            train_fraud_model(data)

            # Store model stats
            model_stats = ModelStats(
                model_name="fraud_model",
                model_type="fraud",
                metrics={"status": "trained", "timestamp": pd.Timestamp.now().isoformat()},
                status="active"
            )
            db.session.add(model_stats)
            db.session.commit()

            logger.info("Fraud model trained by user %s", claims["email"])
            return {"message": "Fraud model trained successfully", "model_stats_id": model_stats.id}, 200
        except BadRequest as e:
            logger.error("Error training fraud model: %s", str(e))
            return {"message": str(e)}, 400

class TrainReserveModel(Resource):
    @jwt_required()
    def post(self):
        claims = get_jwt()

        if claims["role"] != "admin":
            return {"message": "Admin access required"}, 403

        # Check if CSV exists
        if not os.path.exists(CSV_DATA_PATH):
            logger.error("CSV data file not found at %s", CSV_DATA_PATH)
            return {"message": "Training CSV not found"}, 400

        try:
            data = pd.read_csv(CSV_DATA_PATH)
            if data.empty:
                raise BadRequest("CSV data is empty")

            train_reserve_model(data)

            # Store model stats
            model_stats = ModelStats(
                model_name="reserve_model",
                model_type="reserve",
                metrics={"status": "trained", "timestamp": pd.Timestamp.now().isoformat()},
                status="active"
            )
            db.session.add(model_stats)
            db.session.commit()

            logger.info("Reserve model trained by user %s", claims["email"])
            return {"message": "Reserve model trained successfully", "model_stats_id": model_stats.id}, 200
        except BadRequest as e:
            logger.error("Error training reserve model: %s", str(e))
            return {"message": str(e)}, 400

class ModelStatsResource(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt()

        if claims["role"] != "admin":
            return {"message": "Admin access required"}, 403

        try:
            stats = ModelStats.query.all()
            return [{
                "id": stat.id,
                "model_name": stat.model_name,
                "model_type": stat.model_type,
                "metrics": stat.metrics,
                "status": stat.status,
                "trained_at": stat.trained_at.isoformat()
            } for stat in stats], 200
        except Exception as e:
            logger.error("Error retrieving model stats: %s", str(e))
            return {"message": f"Failed to retrieve model stats: {str(e)}"}, 400

# Add resources to API
api.add_resource(TrainFraudModel, "/train-fraud")
api.add_resource(TrainReserveModel, "/train-reserve")
api.add_resource(ModelStatsResource, "/model-stats")
