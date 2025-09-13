from app.utils.logger import logger
from app.db.database import SessionLocal, Guidelines
from app.services.ml_model import predict_disease

# services/ml_model.py

def predict_disease(image_path: str) -> str:
    # Return a fake disease for testing
    return "Leaf Blight"

def get_guidelines(crop_image_path: str):
    try:
        # 1. Run ML model on image
        disease = predict_disease(crop_image_path)
        logger.info("Predicted disease from image %s: %s", crop_image_path, disease)

        # 2. Fetch relevant guidelines from DB
        db = SessionLocal()
        rows = db.query(Guidelines).filter(Guidelines.disease == disease).all()
        logger.info("Fetched %d guidelines for disease=%s", len(rows), disease)

        return [row.text for row in rows]

    except Exception as e:
        logger.exception("Error fetching guidelines for image %s: %s", crop_image_path, e)
        raise

    finally:
        db.close()
