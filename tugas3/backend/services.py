import os
import google.generativeai as genai
from transformers import pipeline

# 1. Setup Hugging Face Sentiment Analysis
# Menggunakan model distilbert agar lebih ringan
print("Loading Hugging Face Model...")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# 2. Setup Gemini
# Pastikan set environment variable GOOGLE_API_KEY
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def analyze_sentiment(text):
    """Mengembalikan label: POSITIVE / NEGATIVE"""
    try:
        # Truncate text jika terlalu panjang untuk model
        result = sentiment_pipeline(text[:512])[0]
        return result['label']
    except Exception as e:
        print(f"HF Error: {e}")
        return "UNKNOWN"

def extract_key_points(text):
    """Menggunakan Gemini untuk extract key points"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Analyze this product review and extract 3 main key points in a concise bullet list format:\n\nReview: {text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Failed to extract key points."
