# import os
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from model_utils import load_model
# from rag_utils import ingest_pdfs_to_chroma, answer_query

# # ✅ FastAPI app setup
# app = FastAPI(
#     title="GreenLens Backend 🌱",
#     version="1.0",
#     description="AI-powered ESG & Sustainability Intelligence API"
# )

# # ✅ Enable CORS (so frontend can call backend)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ✅ Paths
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "carbon_model.pkl")
# DOCS_DIR = os.path.join(BASE_DIR, "..", "docs")

# # ✅ Load the trained ML model
# try:
#     model = load_model(MODEL_PATH)
#     print(f"✅ Model loaded successfully from {MODEL_PATH}")
# except Exception as e:
#     print(f"❌ Failed to load model: {e}")
#     model = None


# # ✅ Health check endpoint
# @app.get("/")
# def root():
#     return {
#         "message": "🌱 GreenLens API is live!",
#         "endpoints": ["/predict", "/ask", "/ingest_docs", "/health"]
#     }


# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}


# # ✅ Predict endpoint
# class PredictRequest(BaseModel):
#     Company: str
#     Month: str
#     Total_Usage_kWh: float
#     month: int
#     is_winter: int
#     prev_CO2: float
#     renewable_share: float


# @app.post("/predict")
# def predict(data: PredictRequest):
#     if not model:
#         raise HTTPException(status_code=500, detail="Model not loaded")

#     import numpy as np
#     features = np.array([
#         data.Total_Usage_kWh,
#         data.month,
#         data.is_winter,
#         data.prev_CO2,
#         data.renewable_share
#     ]).reshape(1, -1)

#     try:
#         prediction = model.predict(features)[0]
#         esg_score = max(0, 100 - (prediction / 10))  # example score calculation
#         return {
#             "predicted_CO2_kg": round(float(prediction), 2),
#             "esg_score": round(float(esg_score), 2)
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


# # ✅ Document ingestion for RAG
# @app.post("/ingest_docs")
# async def ingest_docs(file: UploadFile = File(...)):
#     """Upload and embed a PDF into Chroma DB"""
#     try:
#         file_path = os.path.join(DOCS_DIR, file.filename)
#         with open(file_path, "wb") as f:
#             f.write(await file.read())
#         print(f"📄 Uploaded file saved at {file_path}")

#         # Call the RAG ingestion pipeline
#         result = ingest_pdfs_to_chroma(file_path)
#         return {"message": f"✅ {file.filename} ingested successfully.", "details": result}

#     except Exception as e:
#         print(f"❌ Ingestion failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# # ✅ Ask ESG/Compliance-related queries
# class Question(BaseModel):
#     question: str


# @app.post("/ask")
# def ask_esg(query: Question):
#     try:
#         response = answer_query(query.question)
#         return {"answer": response}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"RAG failed: {e}")
import os
import random
import time
import threading
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model_utils import load_model
from rag_utils import ingest_pdfs_to_chroma, answer_query

# ✅ FastAPI app setup
app = FastAPI(
    title="GreenLens Backend 🌱",
    version="1.1",
    description="AI-powered ESG & Sustainability Intelligence API with Live Energy Tracking"
)

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "carbon_model.pkl")
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs")

# ✅ Load ML Model
try:
    model = load_model(MODEL_PATH)
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    model = None

# ✅ Simulated live energy data
live_data = []

def generate_energy_data():
    """Continuously generate simulated electricity usage data (every 5 seconds)."""
    while True:
        usage_kw = round(random.uniform(700, 1200), 2)
        live_data.append(usage_kw)
        if len(live_data) > 30:
            live_data.pop(0)
        time.sleep(5)

threading.Thread(target=generate_energy_data, daemon=True).start()

# ✅ Routes
@app.get("/")
def root():
    return {
        "message": "🌱 GreenLens API is live!",
        "endpoints": ["/predict", "/ask", "/ingest_docs", "/live-data", "/health"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ✅ Predict endpoint
class PredictRequest(BaseModel):
    Company: str
    Month: str
    Total_Usage_kWh: float
    month: int
    is_winter: int
    prev_CO2: float
    renewable_share: float

@app.post("/predict")
def predict(data: PredictRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    import numpy as np
    features = np.array([
        data.Total_Usage_kWh,
        data.month,
        data.is_winter,
        data.prev_CO2,
        data.renewable_share
    ]).reshape(1, -1)

    try:
        prediction = model.predict(features)[0]
        esg_score = max(0, 100 - (prediction / 10))
        return {
            "predicted_CO2_kg": round(float(prediction), 2),
            "esg_score": round(float(esg_score), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

# ✅ RAG document ingestion
@app.post("/ingest_docs")
async def ingest_docs(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(DOCS_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        print(f"📄 Uploaded file saved at {file_path}")

        result = ingest_pdfs_to_chroma(file_path)
        return {"message": f"✅ {file.filename} ingested successfully.", "details": result}
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ RAG question answering
class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_esg(query: Question):
    try:
        response = answer_query(query.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG failed: {e}")

# ✅ Real-time energy data + ESG prediction
@app.get("/live-data")
def live_energy_data():
    """Stream live electricity data and provide ESG insight."""
    THRESHOLD = 1000
    recent = live_data[-3:] if len(live_data) >= 3 else live_data

    if len(recent) >= 3:
        avg_usage = sum(recent) / len(recent)
        if avg_usage > THRESHOLD:
            message = "⚠️ High energy usage detected! Please minimize electricity consumption."
        elif avg_usage < 800:
            message = "✅ Excellent efficiency! Emissions predicted to remain well below threshold."
        else:
            message = "⚡ Stable usage — keep monitoring for sustainable operation."
    else:
        message = "Collecting initial readings..."

    return {
        "timestamp": time.strftime("%H:%M:%S"),
        "usage_data": live_data,
        "message": message
    }
