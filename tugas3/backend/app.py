import os
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base

def main():
    # Setup Database URL
    # Format: postgresql://user:password@localhost/dbname
    db_url = os.environ.get("POSTGREE_URL", "postgresql://postgres:password@localhost/review_db")
    settings = {
        'sqlalchemy.url': db_url,
        'pyramid.includes': ['pyramid_tm'] # Transaction Manager
    }

    config = Configurator(settings=settings)

    # Setup Database Engine
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine) # Create tables if not exist

    # Setup Routes
    config.add_route('analyze_review', '/api/analyze-review')
    config.add_route('get_reviews', '/api/reviews')

    # Setup CORS (Agar React bisa akses)
    config.add_tween('backend.app.cors_tween_factory')

    config.scan('backend.views') # Scan file views.py

    app = config.make_wsgi_app()
    return app

# Simple CORS Middleware
def cors_tween_factory(handler, registry):
    def cors_tween(request):
        response = handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    return cors_tween

if __name__ == '__main__':
    from waitress import serve
    app = main()
    print("Server running on http://0.0.0.0:6543")
    serve(app, host='0.0.0.0', port=6543)
