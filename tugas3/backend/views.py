from pyramid.view import view_config
from pyramid.response import Response
from .models import DBSession, Review
from .services import analyze_sentiment, extract_key_points
import transaction

# --- GET: Get All Reviews ---
@view_config(route_name='get_reviews', renderer='json', request_method='GET')
def get_reviews(request):
    try:
        reviews = DBSession.query(Review).order_by(Review.created_at.desc()).all()
        return {'status': 'success', 'data': [r.to_json() for r in reviews]}
    except Exception as e:
        request.response.status = 500
        return {'status': 'error', 'message': str(e)}

# --- POST: Analyze Review ---
@view_config(route_name='analyze_review', renderer='json', request_method='POST')
def analyze_review(request):
    try:
        data = request.json_body
        text = data.get('text', '')

        if not text:
            request.response.status = 400
            return {'status': 'error', 'message': 'Text is required'}

        # 1. AI Analysis
        sentiment = analyze_sentiment(text)
        key_points = extract_key_points(text)

        # 2. Save to DB
        new_review = Review(
            product_text=text,
        DBSession.add(new_review)
	DBSession.flush()

        return {'status': 'success', 'data': new_review.to_json()}

    except Exception as e:
        request.response.status = 500
        return {'status': 'error', 'message': str(e)}
