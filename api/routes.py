from functools import wraps
from flask import Blueprint, request, jsonify
from flask_login import current_user
from database import db, FAQ, ChatSession, ChatMessage, AnalyticsLog
from chatbot import matcher, vectorizer

api_bp = Blueprint('api', __name__)

def api_login_required(f):
    """Custom decorator to return JSON 401 responses instead of redirects."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized. Please log in to access this API."}), 401
        return f(*args, **kwargs)
    return decorated_function

def refit_vectorizer():
    """Triggers in-memory vector cache reload."""
    all_faqs = FAQ.query.all()
    vectorizer.fit_faqs(all_faqs)

@api_bp.route('/api/faqs', methods=['GET'])
@api_login_required
def get_faqs():
    """
    GET /api/faqs
    Lists FAQs with pagination and keyword filtering.
    Query params:
      - search: string filter
      - page: int (default 1)
      - per_page: int (default 10)
    """
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = FAQ.query
    if search:
        query = query.filter(
            FAQ.question.like(f"%{search}%") |
            FAQ.answer.like(f"%{search}%") |
            FAQ.category.like(f"%{search}%")
        )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "faqs": [faq.to_dict() for faq in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
        "per_page": per_page
    }), 200


@api_bp.route('/api/chat', methods=['POST'])
@api_login_required
def chat():
    """
    POST /api/chat
    Interacts with the FAQ chatbot engine.
    JSON parameters:
      - message: str (required)
      - session_id: str (optional)
    """
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    session_id = data.get('session_id')

    if not message:
        return jsonify({"error": "Message parameter is required."}), 400

    # Retrieve or create ChatSession
    session = None
    if session_id:
        session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    
    if not session:
        # Create a new session with an auto-generated title (first 5 words of message)
        words = message.split()
        title = " ".join(words[:5]) + ("..." if len(words) > 5 else "")
        session = ChatSession(user_id=current_user.id, title=title)
        db.session.add(session)
        db.session.commit()
        session_id = session.id

    # 1. User Message
    user_msg = ChatMessage(
        session_id=session_id,
        sender='user',
        message=message
    )
    db.session.add(user_msg)

    # 2. Match FAQ
    match_result = matcher.match(message)
    matched_faq_id = match_result.get('id')
    confidence = match_result.get('confidence', 0.0)
    answer = match_result.get('answer', '')

    # 3. Bot Message
    bot_msg = ChatMessage(
        session_id=session_id,
        sender='bot',
        message=answer,
        confidence_score=confidence,
        matched_faq_id=matched_faq_id
    )
    db.session.add(bot_msg)

    # 4. Log to Analytics
    analytics_entry = AnalyticsLog(
        user_id=current_user.id,
        query=message,
        matched_faq_id=matched_faq_id,
        confidence_score=confidence
    )
    db.session.add(analytics_entry)
    
    # Save all database changes
    db.session.commit()

    return jsonify({
        "session_id": session_id,
        "session_title": session.title,
        "response": {
            "matched": match_result.get('matched', False),
            "question": match_result.get('question'),
            "answer": answer,
            "confidence": confidence,
            "matched_keywords": match_result.get('matched_keywords', []),
            "suggestions": match_result.get('suggestions', [])
        }
    }), 200


@api_bp.route('/api/faq', methods=['POST'])
@api_login_required
def create_faq():
    """
    POST /api/faq
    Creates a new FAQ entry.
    JSON parameters:
      - question: str (required)
      - answer: str (required)
      - category: str (optional)
    """
    data = request.get_json() or {}
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    category = data.get('category', 'General').strip()

    if not question or not answer:
        return jsonify({"error": "Both 'question' and 'answer' are required."}), 400

    # Avoid duplicate check
    existing = FAQ.query.filter_by(question=question).first()
    if existing:
        return jsonify({"error": "An FAQ with this question already exists."}), 400

    faq = FAQ(question=question, answer=answer, category=category)
    db.session.add(faq)
    db.session.commit()
    
    # Reload memory vectors
    refit_vectorizer()

    return jsonify(faq.to_dict()), 201


@api_bp.route('/api/faq/<int:faq_id>', methods=['PUT'])
@api_login_required
def update_faq(faq_id):
    """
    PUT /api/faq/<id>
    Updates an existing FAQ entry.
    JSON parameters:
      - question: str
      - answer: str
      - category: str
    """
    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({"error": f"FAQ with ID {faq_id} not found."}), 404

    data = request.get_json() or {}
    
    if 'question' in data:
        q = data.get('question', '').strip()
        if q:
            # check conflict with other questions
            conflict = FAQ.query.filter(FAQ.id != faq_id, FAQ.question == q).first()
            if conflict:
                return jsonify({"error": "Another FAQ with this question already exists."}), 400
            faq.question = q
            
    if 'answer' in data:
        a = data.get('answer', '').strip()
        if a:
            faq.answer = a
            
    if 'category' in data:
        cat = data.get('category', '').strip()
        if cat:
            faq.category = cat

    db.session.commit()
    
    # Reload vectors
    refit_vectorizer()

    return jsonify(faq.to_dict()), 200


@api_bp.route('/api/faq/<int:faq_id>', methods=['DELETE'])
@api_login_required
def delete_faq(faq_id):
    """
    DELETE /api/faq/<id>
    Deletes an FAQ entry.
    """
    faq = FAQ.query.get(faq_id)
    if not faq:
        return jsonify({"error": f"FAQ with ID {faq_id} not found."}), 404

    db.session.delete(faq)
    db.session.commit()
    
    # Reload vectors
    refit_vectorizer()

    return jsonify({"message": f"FAQ with ID {faq_id} successfully deleted."}), 200


@api_bp.route('/api/chat/sessions', methods=['GET'])
@api_login_required
def get_chat_sessions():
    """
    GET /api/chat/sessions
    Retrieves all chat sessions for the authenticated user.
    """
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.updated_at.desc()).all()
    return jsonify([session.to_dict() for session in sessions]), 200


@api_bp.route('/api/chat/session/<string:session_id>', methods=['GET'])
@api_login_required
def get_session_messages(session_id):
    """
    GET /api/chat/session/<session_id>
    Retrieves all chat messages for a specific session.
    """
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return jsonify({"error": "Chat session not found."}), 404
        
    messages = [msg.to_dict() for msg in session.messages]
    return jsonify({
        "session": session.to_dict(),
        "messages": messages
    }), 200


@api_bp.route('/api/chat/session/<string:session_id>', methods=['PUT'])
@api_login_required
def rename_chat_session(session_id):
    """
    PUT /api/chat/session/<session_id>
    Renames a user's chat session.
    """
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return jsonify({"error": "Chat session not found."}), 404
        
    data = request.get_json() or {}
    new_title = data.get('title', '').strip()
    if not new_title:
        return jsonify({"error": "Title parameter cannot be empty."}), 400
        
    session.title = new_title
    db.session.commit()
    
    return jsonify(session.to_dict()), 200


@api_bp.route('/api/chat/session/<string:session_id>', methods=['DELETE'])
@api_login_required
def delete_chat_session(session_id):
    """
    DELETE /api/chat/session/<session_id>
    Deletes a user's chat session and associated messages.
    """
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        return jsonify({"error": "Chat session not found."}), 404
        
    db.session.delete(session)
    db.session.commit()
    
    return jsonify({"message": "Chat session successfully deleted."}), 200

