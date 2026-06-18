import os
import json
import logging
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import config_by_name
from database import db, User, FAQ, ChatSession
from chatbot import initialize_chatbot

def create_app(config_name=None):
    """
    Flask Application Factory.
    """
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Configure Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Initialize Database
    db.init_app(app)

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'danger'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from auth import auth_bp
    from dashboard import dashboard_bp
    from api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403

    # Main Application Views
    @app.route('/')
    def index():
        """
        Public landing page. Redirects authenticated users to the chat panel.
        """
        if current_user.is_authenticated:
            return redirect(url_for('chat'))
        return render_template('index.html')

    @app.route('/chat')
    @login_required
    def chat():
        """
        Loads the main chatbot interface, passing existing conversational sessions.
        """
        sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.updated_at.desc()).all()
        return render_template('index.html', sessions=sessions)

    # Database Seeding and Chatbot Initialization
    with app.app_context():
        try:
            db.create_all()
            
            # Seed FAQ table if empty (and not in testing mode to keep test DB isolated)
            if FAQ.query.count() == 0 and not app.config.get('TESTING'):
                faq_file_path = os.path.join(app.root_path, 'faq_data.json')
                if os.path.exists(faq_file_path):
                    with open(faq_file_path, 'r') as f:
                        faq_seed = json.load(f)
                        for item in faq_seed:
                            faq = FAQ(
                                question=item.get('question'),
                                answer=item.get('answer'),
                                category=item.get('category', 'General')
                            )
                            db.session.add(faq)
                        db.session.commit()
                        logger.info("Successfully seeded database with FAQs.")
                else:
                    logger.warning("faq_data.json file not found. Database not seeded.")

            # Load NLTK resources and fit similarity matrix
            all_faqs = FAQ.query.all()
            initialize_chatbot(all_faqs)
            logger.info("Chatbot matching engine initialized successfully.")
            
        except Exception as e:
            logger.error(f"Error during app startup initialization: {e}", exc_info=True)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001)
