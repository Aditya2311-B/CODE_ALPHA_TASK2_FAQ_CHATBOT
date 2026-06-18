import pytest
from chatbot.vectorizer import FAQVectorizer
from chatbot.matcher import FAQMatcher

@pytest.fixture
def mock_faqs():
    return [
        {
            "id": 1,
            "question": "What is Machine Learning?",
            "answer": "Machine learning is a branch of AI that enables systems to learn from data."
        },
        {
            "id": 2,
            "question": "What is Deep Learning?",
            "answer": "Deep learning is a subset of machine learning based on artificial neural networks."
        },
        {
            "id": 3,
            "question": "What is Python Programming?",
            "answer": "Python is a high-level, interpreted programming language widely used in AI."
        }
    ]

@pytest.fixture
def matcher(mock_faqs):
    vectorizer = FAQVectorizer()
    vectorizer.fit_faqs(mock_faqs)
    return FAQMatcher(vectorizer)

def test_exact_match(matcher):
    res = matcher.match("What is Machine Learning?")
    assert res["matched"] is True
    assert res["id"] == 1
    assert res["confidence"] > 0.8
    assert "machine" in res["matched_keywords"]

def test_semantic_overlap_match(matcher):
    res = matcher.match("Explain machine learning concepts")
    assert res["matched"] is True
    assert res["id"] == 1
    assert res["confidence"] > 0.35

def test_fallback_match(matcher):
    # Completely irrelevant query should fallback
    res = matcher.match("How do I make a chocolate cake?")
    assert res["matched"] is False
    assert res["id"] is None
    assert res["confidence"] < 0.35
    assert res["answer"] == "Sorry, I couldn't find an answer for that question."

def test_suggestions(matcher):
    res = matcher.match("learning program")
    # Even if query is low confidence or matches slightly, check suggestions overlap
    assert len(res["suggestions"]) > 0
    assert any(s["id"] in [1, 2, 3] for s in res["suggestions"])
