import os
import json
import requests
from google import genai # Perbaikan 1: Menggunakan SDK terbaru
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base # Perbaikan 2: Impor yang benar untuk menghilangkan Warning
from datetime import datetime
import transaction

# --- KONFIGURASI ENV & API KEYS ---
# Masukkan DATABASE_URL, HF_API_KEY, dan GEMINI_API_KEY anda
DATABASE_URL = "postgresql://neondb_owner:npg_Hory0Okdq7jX@ep-misty-sunset-a903txac-pooler.gwc.azure.neon.tech/neondb?sslmode=require&channel_binding=require" # Ganti dengan link Database anda
HF_API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english" # Ini tidak perlu diganti
HF_API_KEY = "Bearer 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" # Ganti dengan Token Hugging Face Anda
GEMINI_API_KEY = "AIzaSyDC6NqxouJVYBM_YL6myDWPtgEzyM5nkPo" # Ganti dengan API Key Google AI Studio Anda
MODEL_NAME = 'gemini-2.5-flash' # Model yang akan digunakan

# Inisialisasi Gemini Client
client = None
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"Gemini Client initialized using {MODEL_NAME}.")
except Exception as e:
    print(f"Error initializing Gemini Client: {e}")

# --- DATABASE SETUP (SQLAlchemy) ---
Base = declarative_base() 

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    product_text = Column(Text, nullable=False)
    sentiment_label = Column(String(50)) 
    sentiment_score = Column(String(50))
    key_points = Column(Text) 
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.product_text,
            'sentiment': self.sentiment_label,
            'score': self.sentiment_score,
            'key_points': self.key_points,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Inisialisasi DB Engine
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# --- HELPER FUNCTIONS UNTUK AI ---
def analyze_sentiment_hf(text):
    """Kirim request ke Hugging Face Inference API"""
    headers = {"Authorization": HF_API_KEY}
    payload = {"inputs": text}
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            top_result = max(data[0], key=lambda x: x['score'])
            return top_result['label'], f"{top_result['score']:.2f}"
    except Exception as e:
        print(f"HF Error: {e}")
    return "UNKNOWN", "0.0"

def extract_keypoints_gemini(text):
    global client 
    if client is None:
        return "Failed to extract key points: Client not initialized."
        
    try:
        prompt = f"Extract 3-5 bullet points of key pros/cons from this review. Return only the points separated by newline: '{text}'"
        
        # Memanggil model
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=prompt
        )
        
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Failed to extract key points."

# --- PYRAMID VIEWS (CONTROLLERS) ---
# Middleware untuk CORS
def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        'Access-Control-Max-Age': '1728000',
        })
    event.request.add_response_callback(cors_headers)

@view_config(route_name='analyze', renderer='json', request_method='OPTIONS')
@view_config(route_name='reviews', renderer='json', request_method='OPTIONS')
def cors_preflight(request):
    return {}

@view_config(route_name='analyze', renderer='json', request_method='POST')
def analyze_review_view(request):
    try:
        req_data = request.json_body
        text = req_data.get('text', '')
        
        if not text:
            request.response.status = 400
            return {'error': 'Text is required'}

        # Memanggil AI Services
        sentiment, score = analyze_sentiment_hf(text)
        key_points = extract_keypoints_gemini(text)

        # Menyimpan ke Database
        session = Session()
        new_review = Review(
            product_text=text,
            sentiment_label=sentiment,
            sentiment_score=score,
            key_points=key_points
        )
        session.add(new_review)
        session.commit()
        
        result_dict = new_review.to_dict()
        session.close()

        return result_dict

    except Exception as e:
        request.response.status = 500
        return {'error': str(e)}

@view_config(route_name='reviews', renderer='json', request_method='GET')
def get_reviews_view(request):
    session = Session()
    reviews = session.query(Review).order_by(Review.created_at.desc()).all()
    data = [r.to_dict() for r in reviews]
    session.close()
    return data

# --- MAIN PROGRAM ---
if __name__ == '__main__':
    with Configurator() as config:
        config.add_route('analyze', '/api/analyze-review')
        config.add_route('reviews', '/api/reviews')
        
        config.scan()

        config.add_subscriber(add_cors_headers_response_callback, 'pyramid.events.NewRequest')

        app = config.make_wsgi_app()
    
    print("\n--- Server running on http://localhost:6543 ---")
    from waitress import serve
    serve(app, host='0.0.0.0', port=6543)