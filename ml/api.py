from fastapi import FastAPI
from pydantic import BaseModel

from risk.model import IncidentRiskPredictor
from risk.state_adapter import build_risk_features
from risk.training import generate_dataset


app = FastAPI(
    title="NexCord ML Service",
    version="0.1.0",
)


class PredictionRequest(BaseModel):
    event_id: int


# Train the prototype model once when the
# ML service starts.
samples, labels = generate_dataset()

predictor = IncidentRiskPredictor()
predictor.fit(samples, labels)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_fitted": True,
    }


@app.post("/predict")
def predict(request: PredictionRequest):
    features = build_risk_features(
        request.event_id
    )

    prediction = predictor.predict(
        features
    )

    return {
        "event_id": request.event_id,
        "prediction": prediction,
    }