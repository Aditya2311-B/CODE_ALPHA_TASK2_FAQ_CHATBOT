import pytest
import json
from app import create_app
from database import db, FAQ, User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Seed two initial FAQs for testing
        faq1 = FAQ(question="What is Machine Learning?", answer="ML is data learning.", category="Machine Learning")
        faq2 = FAQ(question="What is Python?", answer="Python is coding.", category="Python Programming")
        db.session.add(faq1)
        db.session.add(faq2)
        db.session.commit()
        
        # Refit the chatbot vectorizer with the test FAQs
        from chatbot import vectorizer
        vectorizer.fit_faqs(FAQ.query.all())
        
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Client logged in as test user."""
    client.post('/register', data={
        'username': 'tester',
        'email': 'tester@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/login', data={
        'username_or_email': 'tester',
        'password': 'password123'
    })
    return client

def test_unauthorized_endpoints(client):
    # API endpoints should fail with 401 if not logged in
    res = client.get('/api/faqs')
    assert res.status_code == 401
    assert b"Unauthorized" in res.data

def test_get_faqs(auth_client):
    res = auth_client.get('/api/faqs')
    assert res.status_code == 200
    data = json.loads(res.data.decode('utf-8'))
    assert data["total"] == 2
    assert len(data["faqs"]) == 2
    assert data["faqs"][0]["question"] == "What is Machine Learning?"

def test_chat_matching(auth_client):
    res = auth_client.post('/api/chat', 
        data=json.dumps({"message": "What is Machine Learning?"}),
        content_type='application/json'
    )
    assert res.status_code == 200
    data = json.loads(res.data.decode('utf-8'))
    assert data["response"]["matched"] is True
    assert "ML is data learning." in data["response"]["answer"]
    assert data["response"]["confidence"] > 0.8
    assert data["session_id"] is not None

def test_faq_crud_endpoints(auth_client):
    # 1. Create FAQ
    new_faq = {
        "question": "What is Computer Vision?",
        "answer": "CV processes digital images.",
        "category": "Computer Vision"
    }
    res_create = auth_client.post('/api/faq',
        data=json.dumps(new_faq),
        content_type='application/json'
    )
    assert res_create.status_code == 201
    created = json.loads(res_create.data.decode('utf-8'))
    faq_id = created["id"]
    assert created["question"] == "What is Computer Vision?"

    # 2. Update FAQ
    updated_faq = {
        "answer": "Computer Vision deals with visual media processing."
    }
    res_update = auth_client.put(f'/api/faq/{faq_id}',
        data=json.dumps(updated_faq),
        content_type='application/json'
    )
    assert res_update.status_code == 200
    updated = json.loads(res_update.data.decode('utf-8'))
    assert updated["answer"] == "Computer Vision deals with visual media processing."

    # 3. Delete FAQ
    res_delete = auth_client.delete(f'/api/faq/{faq_id}')
    assert res_delete.status_code == 200
    delete_msg = json.loads(res_delete.data.decode('utf-8'))
    assert "successfully deleted" in delete_msg["message"]
