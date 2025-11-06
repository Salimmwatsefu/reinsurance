from sklearn.linear_model import LogisticRegression
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, mean_squared_error
import joblib
import pandas as pd
import numpy as np
import os
from werkzeug.exceptions import BadRequest
import logging
from app import db
from app.models import Prediction
from app.utils.data_generator import generate_synthetic_claims

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model storage paths (relative to project root)
FRAUD_MODEL_PATH = os.getenv('FRAUD_MODEL_PATH', 'ml_models/fraud_model.pkl')
RESERVE_MODEL_PATH = os.getenv('RESERVE_MODEL_PATH', 'ml_models/reserve_model.pkl')

# Feature columns for ML models
NUMERIC_FEATURES = ['claim_amount', 'claimant_age', 'claim_length']
CATEGORICAL_FEATURES = ['claim_type']

def preprocess_data(data: pd.DataFrame) -> tuple:
    """Preprocess data for training or prediction."""
    X = data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), NUMERIC_FEATURES),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), CATEGORICAL_FEATURES)
        ]
    )
    return X, preprocessor

def train_fraud_model(data: pd.DataFrame = None) -> None:
    """Train the fraud detection model using logistic regression."""
    try:
        # Use synthetic data if none provided
        if data is None:
            data = generate_synthetic_claims()
        
        if not isinstance(data, pd.DataFrame) or data.empty:
            raise BadRequest("Invalid or empty training data")
        
        X, preprocessor = preprocess_data(data)
        y = data['is_fraudulent']
        
        # Create pipeline
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression(random_state=42))
        ])
        
        # Train
        model.fit(X, y)
        
        # Evaluate
        y_pred = model.predict(X)
        logger.info("Fraud model performance:\n%s", classification_report(y, y_pred))
        
        # Save model
        os.makedirs(os.path.dirname(FRAUD_MODEL_PATH), exist_ok=True)
        joblib.dump(model, FRAUD_MODEL_PATH)
        logger.info("Fraud model trained and saved to %s", FRAUD_MODEL_PATH)
    except Exception as e:
        logger.error("Error training fraud model: %s", str(e))
        raise BadRequest(f"Failed to train fraud model: {str(e)}")

def train_reserve_model(data: pd.DataFrame = None) -> None:
    """Train the reserve estimation model using XGBoost."""
    try:
        # Use synthetic data if none provided
        if data is None:
            data = generate_synthetic_claims()
        
        if not isinstance(data, pd.DataFrame) or data.empty:
            raise BadRequest("Invalid or empty training data")
        
        X, preprocessor = preprocess_data(data)
        y = data['reserve_amount']
        
        # Create pipeline
        model = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', XGBRegressor(random_state=42))
        ])
        
        # Train
        model.fit(X, y)
        
        # Evaluate
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        logger.info("Reserve model MSE: %f", mse)
        
        # Save model
        os.makedirs(os.path.dirname(RESERVE_MODEL_PATH), exist_ok=True)
        joblib.dump(model, RESERVE_MODEL_PATH)
        logger.info("Reserve model trained and saved to %s", RESERVE_MODEL_PATH)
    except Exception as e:
        logger.error("Error training reserve model: %s", str(e))
        raise BadRequest(f"Failed to train reserve model: {str(e)}")

def predict_fraud_and_reserve(claim_id: int, extracted_data: dict) -> dict:
    """Predict fraud score and reserve estimate, store in Prediction model."""
    try:
        # Validate claim exists
        from app.models import Claim
        claim = Claim.query.get(claim_id)
        if not claim:
            raise BadRequest(f"Claim ID {claim_id} not found")
        
        # Load models
        if not os.path.exists(FRAUD_MODEL_PATH) or not os.path.exists(RESERVE_MODEL_PATH):
            raise BadRequest("Models not trained or missing")
        
        fraud_model = joblib.load(FRAUD_MODEL_PATH)
        reserve_model = joblib.load(RESERVE_MODEL_PATH)
        
        # Prepare input
        input_data = pd.DataFrame([{
            'claim_amount': float(extracted_data.get('claim_amount', 0.0)),
            'claim_type': extracted_data.get('claim_type', 'auto'),
            'claimant_age': extracted_data.get('claimant_age', 30),  # Default
            'claim_length': len(extracted_data.get('claim_date', '')) or 10  # Default
        }])
        
        # Predict
        fraud_prob = fraud_model.predict_proba(input_data)[0][1]
        is_fraudulent = bool(fraud_prob > 0.5)
        reserve_estimate = float(reserve_model.predict(input_data)[0])
        
        # Store prediction
        prediction = Prediction(
            claim_id=claim_id,
            fraud_score=fraud_prob,
            is_fraudulent=is_fraudulent,
            reserve_estimate=reserve_estimate,
            model_version='v1.0'
        )
        db.session.add(prediction)
        db.session.commit()
        
        result = {
            'claim_id': claim_id,
            'fraud_score': fraud_prob,
            'is_fraudulent': is_fraudulent,
            'reserve_estimate': reserve_estimate,
            'model_version': 'v1.0'
        }
        logger.info("Prediction for claim %d: %s", claim_id, result)
        return result
    except Exception as e:
        logger.error("Error predicting for claim %d: %s", claim_id, str(e))
        raise BadRequest(f"Failed to predict: {str(e)}")
